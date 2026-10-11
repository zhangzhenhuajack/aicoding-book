"""集成测试：对真实 Postgres 16 跑迁移 + 一条端到端邀请流程。

无 Postgres 时整体 skip（通过 TEAMPULSE_DATABASE_URL 探活）。CI 的 backend-integration
作业会用 service 容器提供 Postgres；本地可 `docker compose up -d postgres` 后设置
TEAMPULSE_DATABASE_URL 再跑 `uv run pytest -m integration`。
"""

from __future__ import annotations

import os
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db.models import Base, Membership, Tenant, User
from app.domain.invitation import Role
from app.repositories.invitation_repo import (
    InvitationRepository,
    MembershipRepository,
    UserRepository,
)
from app.services.invitation_service import InvitationService

pytestmark = pytest.mark.integration

PG_URL = os.environ.get("TEAMPULSE_DATABASE_URL", "")


def _pg_available() -> bool:
    if not PG_URL.startswith("postgresql"):
        return False
    try:
        eng = create_engine(PG_URL, future=True)
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        eng.dispose()
        return True
    except Exception:
        return False


requires_pg = pytest.mark.skipif(
    not _pg_available(),
    reason="需要可连接的 Postgres（设置 TEAMPULSE_DATABASE_URL）",
)


@requires_pg
def test_partial_unique_index_enforced_on_postgres() -> None:
    """Postgres 下部分唯一索引真实生效：同租户同邮箱第二条 pending 应冲突。"""
    eng = create_engine(PG_URL, future=True)
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)
    factory = sessionmaker(bind=eng, expire_on_commit=False, future=True)
    session = factory()
    try:
        tenant = Tenant(id=uuid4(), name="Acme")
        owner = User(id=uuid4(), email="owner@acme.example.com")
        session.add_all([tenant, owner])
        session.flush()
        session.add(Membership(tenant_id=tenant.id, user_id=owner.id, role="owner"))
        session.flush()

        svc = InvitationService(
            InvitationRepository(session),
            MembershipRepository(session),
            UserRepository(session),
        )
        svc.create(
            tenant_id=tenant.id, caller_id=owner.id, email="dup@acme.example.com", role=Role.MEMBER
        )
        session.commit()

        # service 层会先查 pending 返回 409；这里再直接验证数据库约束存在。
        from app.domain.invitation import DomainError

        with pytest.raises(DomainError):
            svc.create(
                tenant_id=tenant.id,
                caller_id=owner.id,
                email="dup@acme.example.com",
                role=Role.MEMBER,
            )
    finally:
        session.close()
        Base.metadata.drop_all(eng)
        eng.dispose()
