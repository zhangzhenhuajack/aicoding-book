"""测试夹具：SQLite 内存库 + service / TestClient 装配。

单元 / 契约 / 架构测试全部用 SQLite 内存库，快且无需 docker。
"""

from __future__ import annotations

from collections.abc import Iterator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import deps
from app.db.models import Base, Membership, Tenant, User
from app.main import create_app
from app.repositories.invitation_repo import (
    InvitationRepository,
    MembershipRepository,
    UserRepository,
)
from app.services.invitation_service import InvitationService


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    s = factory()
    try:
        yield s
    finally:
        s.close()
        engine.dispose()


@pytest.fixture
def service(session: Session) -> InvitationService:
    return InvitationService(
        invitations=InvitationRepository(session),
        memberships=MembershipRepository(session),
        users=UserRepository(session),
    )


def seed_tenant_with_owner(session: Session, owner_email: str) -> tuple[UUID, UUID]:
    """建一个租户 + 一个 owner，返回 (tenant_id, owner_user_id)。"""
    tenant = Tenant(id=uuid4(), name="Acme")
    owner = User(id=uuid4(), email=owner_email.lower())
    session.add_all([tenant, owner])
    session.flush()
    session.add(Membership(tenant_id=tenant.id, user_id=owner.id, role="owner"))
    session.flush()
    return tenant.id, owner.id


def add_member(session: Session, tenant_id: UUID, email: str, role: str) -> UUID:
    user = User(id=uuid4(), email=email.lower())
    session.add(user)
    session.flush()
    session.add(Membership(tenant_id=tenant_id, user_id=user.id, role=role))
    session.flush()
    return user.id


@pytest.fixture
def client(session: Session) -> Iterator[TestClient]:
    """TestClient，覆盖 get_db 复用同一 SQLite 会话。"""
    app = create_app()

    def _override_db() -> Iterator[Session]:
        yield session
        session.commit()

    app.dependency_overrides[deps.get_db] = _override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
