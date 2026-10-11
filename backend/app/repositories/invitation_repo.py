"""数据访问层。本层是唯一允许触碰 app.db.models 的地方。

铁律：所有邀请查询都必须带 tenant_id，严禁跨租户查询（REQ-INV-010）。
按 token_hash 的查询不带 tenant_id（因为接受邀请时还不知道租户），但只用哈希比对，
且后续由 service 校验调用者邮箱与成员关系（REQ-INV-007/010/011）。
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Invitation, Membership, User


class InvitationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, invitation: Invitation) -> Invitation:
        self._session.add(invitation)
        self._session.flush()
        return invitation

    def get_by_id(self, tenant_id: UUID, invitation_id: UUID) -> Invitation | None:
        stmt = select(Invitation).where(
            Invitation.tenant_id == tenant_id,
            Invitation.id == invitation_id,
        )
        return self._session.scalars(stmt).one_or_none()

    def get_by_token_hash(self, token_hash: str) -> Invitation | None:
        stmt = select(Invitation).where(Invitation.token_hash == token_hash)
        return self._session.scalars(stmt).one_or_none()

    def find_pending(self, tenant_id: UUID, email: str) -> Invitation | None:
        stmt = select(Invitation).where(
            Invitation.tenant_id == tenant_id,
            Invitation.email == email,
            Invitation.status == "pending",
        )
        return self._session.scalars(stmt).one_or_none()

    def list_for_tenant(self, tenant_id: UUID, status: str | None) -> list[Invitation]:
        stmt = select(Invitation).where(Invitation.tenant_id == tenant_id)
        if status is not None:
            stmt = stmt.where(Invitation.status == status)
        stmt = stmt.order_by(Invitation.created_at.desc())
        return list(self._session.scalars(stmt).all())


class MembershipRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def is_member(self, tenant_id: UUID, user_id: UUID) -> bool:
        stmt = select(Membership).where(
            Membership.tenant_id == tenant_id,
            Membership.user_id == user_id,
        )
        return self._session.scalars(stmt).one_or_none() is not None

    def get_role(self, tenant_id: UUID, user_id: UUID) -> str | None:
        stmt = select(Membership).where(
            Membership.tenant_id == tenant_id,
            Membership.user_id == user_id,
        )
        m = self._session.scalars(stmt).one_or_none()
        return m.role if m is not None else None

    def email_is_member(self, tenant_id: UUID, email: str) -> bool:
        stmt = (
            select(Membership)
            .join(User, User.id == Membership.user_id)
            .where(Membership.tenant_id == tenant_id, User.email == email)
        )
        return self._session.scalars(stmt).one_or_none() is not None

    def add(self, tenant_id: UUID, user_id: UUID, role: str) -> None:
        self._session.add(Membership(tenant_id=tenant_id, user_id=user_id, role=role))
        self._session.flush()


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self._session.scalars(stmt).one_or_none()

    def get_or_create(self, email: str) -> User:
        user = self.get_by_email(email)
        if user is None:
            user = User(email=email)
            self._session.add(user)
            self._session.flush()
        return user
