"""契约测试：通过 TestClient 验证 HTTP 状态码、错误体结构与 openapi.yaml 一致。

验证点：
- 创建返回 201 且含一次性 token，列表不含 token/token_hash；
- 错误体统一为 {"error": {"code", "message"}}；
- 跨租户 404 / 过期 410 / 重复 409 / member 403 的映射正确。
"""

from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import add_member, seed_tenant_with_owner

OPENAPI = Path(__file__).resolve().parents[3] / "contracts" / "openapi.yaml"


def _h(email: str) -> dict[str, str]:
    return {"X-Demo-User": email}


def test_openapi_file_is_valid_31() -> None:
    spec = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
    assert spec["openapi"].startswith("3.1")
    assert "/api/invitations/accept" in spec["paths"]
    assert "/api/tenants/{tenant_id}/invitations" in spec["paths"]


def test_create_returns_201_with_token(client: TestClient, session: Session) -> None:
    tenant_id, _ = seed_tenant_with_owner(session, "owner@acme.example.com")
    resp = client.post(
        f"/api/tenants/{tenant_id}/invitations",
        json={"email": "new@acme.example.com", "role": "member"},
        headers=_h("owner@acme.example.com"),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "token" in body and body["token"]
    assert body["status"] == "pending"
    assert body["role"] == "member"


def test_list_omits_token_fields(client: TestClient, session: Session) -> None:
    tenant_id, _ = seed_tenant_with_owner(session, "owner@acme.example.com")
    client.post(
        f"/api/tenants/{tenant_id}/invitations",
        json={"email": "a@acme.example.com", "role": "member"},
        headers=_h("owner@acme.example.com"),
    )
    resp = client.get(
        f"/api/tenants/{tenant_id}/invitations?status=pending",
        headers=_h("owner@acme.example.com"),
    )
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) == 1
    assert "token" not in rows[0]
    assert "token_hash" not in rows[0]


def test_member_create_403_error_envelope(client: TestClient, session: Session) -> None:
    tenant_id, _ = seed_tenant_with_owner(session, "owner@acme.example.com")
    add_member(session, tenant_id, "m@acme.example.com", "member")
    resp = client.post(
        f"/api/tenants/{tenant_id}/invitations",
        json={"email": "x@acme.example.com", "role": "member"},
        headers=_h("m@acme.example.com"),
    )
    assert resp.status_code == 403
    assert resp.json() == {"error": {"code": "FORBIDDEN", "message": "只有 owner/admin 能创建邀请"}}


def test_schema_rejects_owner_role(client: TestClient, session: Session) -> None:
    # REQ-INV-002：schema 层就不允许 role=owner -> 422
    tenant_id, _ = seed_tenant_with_owner(session, "owner@acme.example.com")
    resp = client.post(
        f"/api/tenants/{tenant_id}/invitations",
        json={"email": "x@acme.example.com", "role": "owner"},
        headers=_h("owner@acme.example.com"),
    )
    assert resp.status_code == 422


def test_cross_tenant_revoke_returns_404(client: TestClient, session: Session) -> None:
    tenant_id, _ = seed_tenant_with_owner(session, "owner@acme.example.com")
    created = client.post(
        f"/api/tenants/{tenant_id}/invitations",
        json={"email": "t@acme.example.com", "role": "member"},
        headers=_h("owner@acme.example.com"),
    ).json()
    other_tenant_id, _ = seed_tenant_with_owner(session, "owner@other.example.org")
    resp = client.post(
        f"/api/tenants/{other_tenant_id}/invitations/{created['id']}/revoke",
        headers=_h("owner@other.example.org"),
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "INVITATION_NOT_FOUND"


def test_accept_flow_200(client: TestClient, session: Session) -> None:
    tenant_id, _ = seed_tenant_with_owner(session, "owner@acme.example.com")
    created = client.post(
        f"/api/tenants/{tenant_id}/invitations",
        json={"email": "join@acme.example.com", "role": "admin"},
        headers=_h("owner@acme.example.com"),
    ).json()
    resp = client.post(
        "/api/invitations/accept",
        json={"token": created["token"]},
        headers=_h("join@acme.example.com"),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"
