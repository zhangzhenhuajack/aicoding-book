"""FastAPI 依赖。

认证为演示简化：从请求头 X-Demo-User 读取当前用户邮箱（生产须换 OIDC/JWT）。
get_db 提供一个按请求生命周期管理的 Session（提交 / 回滚 / 关闭）。
本模块只依赖 services 层（不直接 import app.repositories / app.db.models），满足分层契约。
"""

from __future__ import annotations

from collections.abc import Iterator
from uuid import UUID

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.domain.invitation import normalize_email
from app.services.invitation_service import InvitationService, build_service


def get_db() -> Iterator[Session]:
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_current_user_email(x_demo_user: str = Header(..., alias="X-Demo-User")) -> str:
    if not x_demo_user:
        raise HTTPException(status_code=401, detail="missing X-Demo-User")
    return normalize_email(x_demo_user)


def get_service(db: Session = Depends(get_db)) -> InvitationService:
    return build_service(db)


def get_current_user_id(
    email: str = Depends(get_current_user_email),
    service: InvitationService = Depends(get_service),
) -> UUID:
    return service.resolve_user_id(email)
