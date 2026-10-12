"""业务规则层。编排 repository，实施 REQ-INV-001~011。

本层不碰 HTTP（不 import fastapi），也不碰 ORM 模型以外的框架细节；错误用 DomainError
抛出，由 api 层统一映射成错误体。所有"我有没有权限看这个租户"的判断都在这里做，
不满足一律按 404 处理，避免泄露资源存在性（REQ-INV-010）。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from app.core.security import generate_token, hash_token
from app.db.models import Invitation as InvitationModel
from app.domain.invitation import (
    DomainError,
    InvitationStatus,
    Role,
    can_invite,
    compute_expiry,
    normalize_email,
    utcnow,
)
from app.repositories.invitation_repo import (
    InvitationRepository,
    MembershipRepository,
    UserRepository,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


@dataclass(frozen=True)
class CreatedInvitation:
    model: InvitationModel
    token: str  # 一次性明文 token，仅返回一次


@dataclass(frozen=True)
class AcceptOutcome:
    tenant_id: UUID
    user_email: str
    role: str
    status: str


def _not_found() -> DomainError:
    # 跨租户 / 未知资源统一 404，错误码不区分，避免存在性泄露。
    return DomainError("INVITATION_NOT_FOUND", "邀请不存在")


class InvitationService:
    def __init__(
        self,
        invitations: InvitationRepository,
        memberships: MembershipRepository,
        users: UserRepository,
    ) -> None:
        self._invitations = invitations
        self._memberships = memberships
        self._users = users

    def resolve_user_id(self, email: str) -> UUID:
        """按邮箱取/建用户，返回其 id（demo 登录装配用）。"""
        return self._users.get_or_create(normalize_email(email)).id

    def _require_tenant_member(self, tenant_id: UUID, caller_id: UUID) -> str:
        """调用者必须是该租户成员，否则按 404（REQ-INV-010）。返回其角色。"""
        role = self._memberships.get_role(tenant_id, caller_id)
        if role is None:
            raise _not_found()
        return role

    def create(
        self,
        *,
        tenant_id: UUID,
        caller_id: UUID,
        email: str,
        role: Role,
        now: datetime | None = None,
    ) -> CreatedInvitation:
        now = now or utcnow()
        caller_role = Role(self._require_tenant_member(tenant_id, caller_id))

        # REQ-INV-001：只有 owner/admin 能创建，member 创建返回 403。
        if not can_invite(caller_role):
            raise DomainError("FORBIDDEN", "只有 owner/admin 能创建邀请")

        # REQ-INV-002：owner 不可被邀请（领域/schema 不允许），这里兜底校验。
        if role not in (Role.ADMIN, Role.MEMBER):
            raise DomainError("FORBIDDEN", "不能邀请该角色")

        email = normalize_email(email)

        # REQ-INV-004：已是成员则 409 ALREADY_MEMBER。
        if self._memberships.email_is_member(tenant_id, email):
            raise DomainError("ALREADY_MEMBER", "该邮箱已是租户成员")

        # REQ-INV-003：已有 pending 则 409 INVITATION_ALREADY_PENDING。
        if self._invitations.find_pending(tenant_id, email) is not None:
            raise DomainError("INVITATION_ALREADY_PENDING", "已存在待处理的邀请")

        # REQ-INV-005：生成明文 token，仅存哈希。
        token = generate_token()
        model = InvitationModel(
            id=uuid4(),
            tenant_id=tenant_id,
            email=email,
            role=role.value,
            token_hash=hash_token(token),
            status=InvitationStatus.PENDING.value,
            expires_at=compute_expiry(now),
            created_by=caller_id,
            created_at=now,
            accepted_at=None,
        )
        self._invitations.add(model)
        return CreatedInvitation(model=model, token=token)

    def list(
        self, *, tenant_id: UUID, caller_id: UUID, status: str | None
    ) -> list[InvitationModel]:
        self._require_tenant_member(tenant_id, caller_id)
        return self._invitations.list_for_tenant(tenant_id, status)

    def revoke(self, *, tenant_id: UUID, caller_id: UUID, invitation_id: UUID) -> InvitationModel:
        caller_role = Role(self._require_tenant_member(tenant_id, caller_id))
        if not can_invite(caller_role):
            raise DomainError("FORBIDDEN", "只有 owner/admin 能撤销邀请")

        inv = self._invitations.get_by_id(tenant_id, invitation_id)
        if inv is None:
            raise _not_found()  # REQ-INV-010：含跨租户

        # REQ-INV-009：只能撤销 pending。
        if inv.status != InvitationStatus.PENDING.value:
            raise DomainError("INVITATION_NOT_PENDING", "只能撤销待处理的邀请")

        inv.status = InvitationStatus.REVOKED.value
        return inv

    def accept(
        self, *, token: str, caller_email: str, now: datetime | None = None
    ) -> AcceptOutcome:
        now = now or utcnow()
        caller_email = normalize_email(caller_email)

        # REQ-INV-011：用哈希查询，未知 token 一律 404（查询路径不因存在与否而异）。
        inv = self._invitations.get_by_token_hash(hash_token(token))
        if inv is None:
            raise _not_found()

        # REQ-INV-008：幂等——重复接受已接受的邀请返回当前结果，不重复建成员。
        if inv.status == InvitationStatus.ACCEPTED.value:
            if normalize_email(inv.email) != caller_email:
                raise DomainError("EMAIL_MISMATCH", "登录邮箱与邀请邮箱不一致")
            user = self._users.get_or_create(caller_email)
            role = self._memberships.get_role(inv.tenant_id, user.id) or inv.role
            return AcceptOutcome(inv.tenant_id, caller_email, role, inv.status)

        # 撤销 / 已过期状态不可接受。
        if inv.status == InvitationStatus.REVOKED.value:
            raise _not_found()

        # REQ-INV-006：过期返回 410（含状态仍是 pending 但时间已过）。
        # SQLite 不保留 tzinfo，取回可能是 naive datetime，这里统一视为 UTC 再比较。
        expires_at = inv.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if inv.status == InvitationStatus.EXPIRED.value or now >= expires_at:
            inv.status = InvitationStatus.EXPIRED.value
            raise DomainError("INVITATION_EXPIRED", "邀请已过期")

        # REQ-INV-007：当前登录邮箱必须与邀请邮箱一致（大小写不敏感）。
        if normalize_email(inv.email) != caller_email:
            raise DomainError("EMAIL_MISMATCH", "登录邮箱与邀请邮箱不一致")

        # 成功：建成员、置 accepted（REQ-INV-008）。
        user = self._users.get_or_create(caller_email)
        if not self._memberships.is_member(inv.tenant_id, user.id):
            self._memberships.add(inv.tenant_id, user.id, inv.role)
        inv.status = InvitationStatus.ACCEPTED.value
        inv.accepted_at = now
        return AcceptOutcome(inv.tenant_id, caller_email, inv.role, inv.status)


def build_service(session: Session) -> InvitationService:
    """组合根：由会话装配 service 及其依赖的仓库。

    放在 services 层而非 api 层，使 api 不必直接 import app.repositories
    （满足分层契约：api → services）。
    """
    return InvitationService(
        invitations=InvitationRepository(session),
        memberships=MembershipRepository(session),
        users=UserRepository(session),
    )
