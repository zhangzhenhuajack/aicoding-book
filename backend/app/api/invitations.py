"""路由层：只做 HTTP <-> 服务调用的翻译，不含业务规则。

严禁 import app.repositories 或 app.db.models（import-linter 强制）。错误码到 HTTP
状态的映射集中在这里。
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Protocol
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

from app.api.deps import get_current_user_email, get_current_user_id, get_service
from app.domain.invitation import DomainError, InvitationStatus, Role
from app.services.invitation_service import InvitationService

router = APIRouter()

# 错误码 -> HTTP 状态。
_CODE_TO_STATUS: dict[str, int] = {
    "FORBIDDEN": 403,
    "EMAIL_MISMATCH": 403,
    "INVITATION_NOT_FOUND": 404,
    "INVITATION_ALREADY_PENDING": 409,
    "ALREADY_MEMBER": 409,
    "INVITATION_NOT_PENDING": 409,
    "INVITATION_EXPIRED": 410,
}


def _error_response(err: DomainError) -> JSONResponse:
    status = _CODE_TO_STATUS.get(err.code, 400)
    return JSONResponse(
        status_code=status,
        content={"error": {"code": err.code, "message": err.message}},
    )


class InvitationCreateBody(BaseModel):
    email: EmailStr
    # schema 层只接受 admin/member；owner 不在可邀请集合里（REQ-INV-002）。
    role: Literal["admin", "member"]

    model_config = {"extra": "forbid"}


class AcceptBody(BaseModel):
    token: str

    model_config = {"extra": "forbid"}


class _InvitationRow(Protocol):
    id: UUID
    tenant_id: UUID
    email: str
    role: str
    status: str
    expires_at: datetime
    created_at: datetime
    accepted_at: datetime | None


def _serialize(inv: _InvitationRow) -> dict[str, object]:
    # 列表/撤销响应不含 token / token_hash。
    return {
        "id": str(inv.id),
        "tenant_id": str(inv.tenant_id),
        "email": inv.email,
        "role": inv.role,
        "status": inv.status,
        "expires_at": inv.expires_at.isoformat(),
        "created_at": inv.created_at.isoformat(),
        "accepted_at": (inv.accepted_at.isoformat() if inv.accepted_at is not None else None),
    }


@router.post("/api/tenants/{tenant_id}/invitations", status_code=201)
def create_invitation(
    tenant_id: UUID,
    body: InvitationCreateBody,
    caller_id: UUID = Depends(get_current_user_id),
    service: InvitationService = Depends(get_service),
) -> JSONResponse:
    try:
        created = service.create(
            tenant_id=tenant_id,
            caller_id=caller_id,
            email=str(body.email),
            role=Role(body.role),
        )
    except DomainError as err:
        return _error_response(err)
    payload = _serialize(created.model)
    payload["token"] = created.token  # 一次性明文 token
    return JSONResponse(status_code=201, content=payload)


@router.get("/api/tenants/{tenant_id}/invitations")
def list_invitations(
    tenant_id: UUID,
    status: str | None = None,
    caller_id: UUID = Depends(get_current_user_id),
    service: InvitationService = Depends(get_service),
) -> JSONResponse:
    if status is not None and status not in {s.value for s in InvitationStatus}:
        return JSONResponse(
            status_code=400, content={"error": {"code": "BAD_STATUS", "message": "无效 status"}}
        )
    try:
        rows = service.list(tenant_id=tenant_id, caller_id=caller_id, status=status)
    except DomainError as err:
        return _error_response(err)
    return JSONResponse(status_code=200, content=[_serialize(r) for r in rows])


@router.post("/api/tenants/{tenant_id}/invitations/{invitation_id}/revoke")
def revoke_invitation(
    tenant_id: UUID,
    invitation_id: UUID,
    caller_id: UUID = Depends(get_current_user_id),
    service: InvitationService = Depends(get_service),
) -> JSONResponse:
    try:
        inv = service.revoke(tenant_id=tenant_id, caller_id=caller_id, invitation_id=invitation_id)
    except DomainError as err:
        return _error_response(err)
    return JSONResponse(status_code=200, content=_serialize(inv))


@router.post("/api/invitations/accept")
def accept_invitation(
    body: AcceptBody,
    caller_email: str = Depends(get_current_user_email),
    service: InvitationService = Depends(get_service),
) -> JSONResponse:
    try:
        outcome = service.accept(token=body.token, caller_email=caller_email)
    except DomainError as err:
        return _error_response(err)
    return JSONResponse(
        status_code=200,
        content={
            "tenant_id": str(outcome.tenant_id),
            "user_email": outcome.user_email,
            "role": outcome.role,
            "status": outcome.status,
        },
    )
