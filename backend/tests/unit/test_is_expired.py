"""is_expired 边界测试。

本文件记录变异测试演示：先是一个弱断言的假测试（被变异揭穿），后补强。
对应 docs/mutation-demo.md。
"""

from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from app.domain.invitation import (
    Invitation,
    InvitationStatus,
    Role,
    utcnow,
)


def _make(expires_in: timedelta) -> Invitation:
    now = utcnow()
    return Invitation(
        id=uuid4(),
        tenant_id=uuid4(),
        email="x@acme.example.com",
        role=Role.MEMBER,
        status=InvitationStatus.PENDING,
        expires_at=now + expires_in,
        created_at=now,
        accepted_at=None,
    )


def test_is_expired_boundary() -> None:
    # 强断言：钉住 >= 的三点行为（来自 REQ-INV-006 的"7 天后过期"语义）。
    now = utcnow()
    inv = _make(timedelta(days=1))

    # 1) 过期时刻之前：未过期。
    assert inv.is_expired(now) is False
    # 2) 恰好等于 expires_at（边界）：按 >= 语义应判为已过期。
    assert inv.is_expired(inv.expires_at) is True
    # 3) 过期时刻之后：已过期。
    assert inv.is_expired(inv.expires_at + timedelta(seconds=1)) is True
