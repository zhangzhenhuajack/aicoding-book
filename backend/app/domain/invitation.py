"""纯领域对象与规则。本模块严禁 import fastapi / sqlalchemy / app.db / app.api。

领域层只表达"邀请是什么、它的状态如何流转、什么算过期"，不关心它怎么持久化、
怎么通过 HTTP 暴露。import-linter 的 forbidden 契约会机械地守住这条边界。
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

INVITATION_TTL = timedelta(days=7)


class Role(enum.StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class InvitationStatus(enum.StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REVOKED = "revoked"
    EXPIRED = "expired"


# 可被邀请的角色（schema 层就不允许 owner，见 REQ-INV-002）。
INVITABLE_ROLES = (Role.ADMIN, Role.MEMBER)
# 有权创建邀请的角色（REQ-INV-001）。
CAN_INVITE_ROLES = (Role.OWNER, Role.ADMIN)


class DomainError(Exception):
    """领域规则违反。携带一个稳定的错误码，由上层映射到 HTTP 状态。"""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class Invitation:
    """领域视角的邀请快照（与 ORM 模型解耦）。"""

    id: UUID
    tenant_id: UUID
    email: str
    role: Role
    status: InvitationStatus
    expires_at: datetime
    created_at: datetime
    accepted_at: datetime | None

    def is_expired(self, now: datetime) -> bool:
        """过期判定：当前时间 >= expires_at（REQ-INV-006）。"""
        return now >= self.expires_at


def normalize_email(email: str) -> str:
    """邮箱统一小写并去空白，保证大小写不敏感的匹配（REQ-INV-007）。"""
    return email.strip().lower()


def compute_expiry(created_at: datetime) -> datetime:
    """创建时刻 + 7 天（UTC）。"""
    return created_at + INVITATION_TTL


def can_invite(inviter_role: Role) -> bool:
    """只有 owner / admin 能创建邀请（REQ-INV-001）。"""
    return inviter_role in CAN_INVITE_ROLES


def utcnow() -> datetime:
    return datetime.now(UTC)
