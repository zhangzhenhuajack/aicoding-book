"""邀请业务规则单测（REQ-INV-001~011）。SQLite 内存库，真实 service。"""

from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.domain.invitation import DomainError, Role, utcnow
from app.services.invitation_service import InvitationService
from tests.conftest import add_member, seed_tenant_with_owner


def test_owner_can_create_invitation(service: InvitationService, session: Session) -> None:
    tenant_id, owner_id = seed_tenant_with_owner(session, "owner@acme.example.com")
    created = service.create(
        tenant_id=tenant_id, caller_id=owner_id, email="New@Acme.example.com", role=Role.MEMBER
    )
    assert created.model.email == "new@acme.example.com"  # 存小写
    assert created.model.status == "pending"
    assert created.token  # 明文 token 返回


def test_member_cannot_create_returns_403(service: InvitationService, session: Session) -> None:
    # REQ-INV-001
    tenant_id, _ = seed_tenant_with_owner(session, "owner@acme.example.com")
    member_id = add_member(session, tenant_id, "m@acme.example.com", "member")
    with pytest.raises(DomainError) as e:
        service.create(
            tenant_id=tenant_id, caller_id=member_id, email="x@acme.example.com", role=Role.MEMBER
        )
    assert e.value.code == "FORBIDDEN"


def test_token_only_stored_as_hash(service: InvitationService, session: Session) -> None:
    # REQ-INV-005：明文 token 从不落库，只存 SHA-256。
    tenant_id, owner_id = seed_tenant_with_owner(session, "owner@acme.example.com")
    created = service.create(
        tenant_id=tenant_id, caller_id=owner_id, email="z@acme.example.com", role=Role.MEMBER
    )
    import hashlib

    assert created.model.token_hash == hashlib.sha256(created.token.encode()).hexdigest()
    assert created.model.token_hash != created.token
    assert len(created.model.token_hash) == 64
    # 库里任何字段都不含明文 token
    assert created.token not in (created.model.email, created.model.token_hash)


def test_duplicate_pending_returns_409(service: InvitationService, session: Session) -> None:
    # REQ-INV-003
    tenant_id, owner_id = seed_tenant_with_owner(session, "owner@acme.example.com")
    service.create(
        tenant_id=tenant_id, caller_id=owner_id, email="dup@acme.example.com", role=Role.MEMBER
    )
    with pytest.raises(DomainError) as e:
        service.create(
            tenant_id=tenant_id, caller_id=owner_id, email="dup@acme.example.com", role=Role.MEMBER
        )
    assert e.value.code == "INVITATION_ALREADY_PENDING"


def test_invite_existing_member_returns_409(service: InvitationService, session: Session) -> None:
    # REQ-INV-004
    tenant_id, owner_id = seed_tenant_with_owner(session, "owner@acme.example.com")
    add_member(session, tenant_id, "already@acme.example.com", "member")
    with pytest.raises(DomainError) as e:
        service.create(
            tenant_id=tenant_id,
            caller_id=owner_id,
            email="already@acme.example.com",
            role=Role.MEMBER,
        )
    assert e.value.code == "ALREADY_MEMBER"


def test_cross_tenant_access_returns_404(service: InvitationService, session: Session) -> None:
    # REQ-INV-010：调用者不是该租户成员 -> 404（NOT_FOUND），不泄露存在性。
    tenant_id, owner_id = seed_tenant_with_owner(session, "owner@acme.example.com")
    created = service.create(
        tenant_id=tenant_id, caller_id=owner_id, email="t@acme.example.com", role=Role.MEMBER
    )
    # 另一个租户的 owner 试图撤销本租户的邀请
    other_tenant_id, other_owner_id = seed_tenant_with_owner(session, "owner@other.example.org")
    with pytest.raises(DomainError) as e:
        service.revoke(
            tenant_id=other_tenant_id,
            caller_id=other_owner_id,
            invitation_id=created.model.id,
        )
    # 用 other_tenant_id 查不到该邀请 -> NOT_FOUND
    assert e.value.code == "INVITATION_NOT_FOUND"

    # 非成员读取本租户列表也 404
    stranger_id = uuid4()
    with pytest.raises(DomainError) as e2:
        service.list(tenant_id=tenant_id, caller_id=stranger_id, status=None)
    assert e2.value.code == "INVITATION_NOT_FOUND"


def test_accept_expired_returns_410(service: InvitationService, session: Session) -> None:
    # REQ-INV-006
    tenant_id, owner_id = seed_tenant_with_owner(session, "owner@acme.example.com")
    created = service.create(
        tenant_id=tenant_id, caller_id=owner_id, email="late@acme.example.com", role=Role.MEMBER
    )
    future = utcnow() + timedelta(days=8)  # 已过 7 天
    with pytest.raises(DomainError) as e:
        service.accept(token=created.token, caller_email="late@acme.example.com", now=future)
    assert e.value.code == "INVITATION_EXPIRED"


def test_accept_email_mismatch_returns_403(service: InvitationService, session: Session) -> None:
    # REQ-INV-007
    tenant_id, owner_id = seed_tenant_with_owner(session, "owner@acme.example.com")
    created = service.create(
        tenant_id=tenant_id, caller_id=owner_id, email="right@acme.example.com", role=Role.MEMBER
    )
    with pytest.raises(DomainError) as e:
        service.accept(token=created.token, caller_email="wrong@acme.example.com")
    assert e.value.code == "EMAIL_MISMATCH"


def test_accept_success_and_idempotent(service: InvitationService, session: Session) -> None:
    # REQ-INV-008：成功建成员、置 accepted；重复接受幂等、不重复建成员。
    tenant_id, owner_id = seed_tenant_with_owner(session, "owner@acme.example.com")
    created = service.create(
        tenant_id=tenant_id, caller_id=owner_id, email="Join@Acme.example.com", role=Role.ADMIN
    )
    out1 = service.accept(token=created.token, caller_email="join@acme.example.com")
    assert out1.status == "accepted"
    assert out1.role == "admin"
    # 幂等重复
    out2 = service.accept(token=created.token, caller_email="JOIN@acme.example.com")
    assert out2.status == "accepted"
    assert out2.tenant_id == tenant_id


def test_accept_unknown_token_returns_404(service: InvitationService, session: Session) -> None:
    # REQ-INV-011
    with pytest.raises(DomainError) as e:
        service.accept(token="totally-unknown-token", caller_email="a@b.example.com")
    assert e.value.code == "INVITATION_NOT_FOUND"


def test_revoke_non_pending_returns_409(service: InvitationService, session: Session) -> None:
    # REQ-INV-009
    tenant_id, owner_id = seed_tenant_with_owner(session, "owner@acme.example.com")
    created = service.create(
        tenant_id=tenant_id, caller_id=owner_id, email="r@acme.example.com", role=Role.MEMBER
    )
    service.accept(token=created.token, caller_email="r@acme.example.com")  # 变 accepted
    with pytest.raises(DomainError) as e:
        service.revoke(tenant_id=tenant_id, caller_id=owner_id, invitation_id=created.model.id)
    assert e.value.code == "INVITATION_NOT_PENDING"
