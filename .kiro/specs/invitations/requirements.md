# 需求：租户邀请（Invitation）

> 采用 EARS 写法。错误码与状态码与 `../../../contracts/openapi.yaml` 及 `TEAMPULSE-SPEC.md` 第 4/5 节逐字一致。
> 认证为演示简化：请求头 `X-Demo-User: <email>` 代表当前登录用户。

## 1. 功能需求（EARS）

**REQ-INV-001｜创建权限**
当一个用户对某租户发起创建邀请的请求时，若该用户是该租户的 owner 或 admin，则系统应当创建邀请并返回 201；若该用户是 member，则系统应当拒绝并返回 403。

**REQ-INV-002｜可邀请角色**
当创建邀请的请求体中 `role` 为 `owner` 时，系统应当在 schema 层直接拒绝（422），即 admin/owner 都不能邀请 owner；当 `role` 为 `admin` 或 `member` 时，系统应当接受该字段。

**REQ-INV-003｜重复 pending 去重**
若同一租户、同一邮箱已存在一条 `pending` 邀请，当再次创建针对该邮箱的邀请时，系统应当拒绝并返回 409，错误码 `INVITATION_ALREADY_PENDING`。

**REQ-INV-004｜已是成员**
若被邀请邮箱已是该租户成员，当创建针对该邮箱的邀请时，系统应当拒绝并返回 409，错误码 `ALREADY_MEMBER`。

**REQ-INV-005｜token 生成与存储**
当创建邀请时，系统应当用 `secrets.token_urlsafe(32)` 生成明文 token，仅在创建响应中返回该明文一次，并且只持久化其 SHA-256 十六进制哈希；系统不应当将明文 token 落库。

**REQ-INV-006｜过期**
当邀请创建时，系统应当将 `expires_at` 设为创建时刻 + 7 天（UTC）；当用户接受一个当前时间已达到或超过 `expires_at` 的邀请时，系统应当拒绝并返回 410，错误码 `INVITATION_EXPIRED`。

**REQ-INV-007｜邮箱一致**
当用户接受邀请时，若当前登录邮箱与邀请邮箱（大小写不敏感比较）不一致，则系统应当拒绝并返回 403，错误码 `EMAIL_MISMATCH`。

**REQ-INV-008｜接受成功与幂等**
当用户以一致邮箱接受一条有效 pending 邀请时，系统应当创建对应 Membership 并将邀请状态置为 `accepted`，返回 200；若同一用户再次接受一条已 `accepted` 的邀请，则系统应当返回 200 且不重复创建 Membership（幂等）。

**REQ-INV-009｜撤销限 pending**
当 owner/admin 请求撤销邀请时，若邀请状态为 `pending`，则系统应当将其置为 `revoked` 并返回 200；若状态非 `pending`，则系统应当拒绝并返回 409，错误码 `INVITATION_NOT_PENDING`。

**REQ-INV-010｜跨租户隔离**
当请求中的 `tenant_id` 与资源不匹配，或调用者不是该租户成员时，系统应当一律返回 404，不区分“无权限”与“不存在”，以避免泄露资源存在性。

**REQ-INV-011｜未知 token**
当接受邀请提供的 token 未知或错误时，系统应当返回 404，错误码 `INVITATION_NOT_FOUND`；系统应当以 token 的哈希进行查询，使响应是否存在不因 token 是否命中而走不同的数据库查询路径。

## 2. 验收条件表

| 编号 | 场景 | 期望状态码 | 错误码 | 自动化验证点 |
|---|---|---|---|---|
| REQ-INV-001 | member 创建邀请 | 403 | FORBIDDEN | `tests/unit::test_member_cannot_create_returns_403` / `tests/contract::test_member_create_403_error_envelope` |
| REQ-INV-002 | role=owner 创建 | 422 | （schema 拒绝） | `tests/contract::test_schema_rejects_owner_role` |
| REQ-INV-003 | 重复 pending | 409 | INVITATION_ALREADY_PENDING | `tests/unit::test_duplicate_pending_returns_409` |
| REQ-INV-004 | 已是成员 | 409 | ALREADY_MEMBER | `tests/unit::test_invite_existing_member_returns_409` |
| REQ-INV-005 | 只存哈希 | 201 | — | `tests/unit::test_token_only_stored_as_hash` |
| REQ-INV-006 | 接受过期 | 410 | INVITATION_EXPIRED | `tests/unit::test_accept_expired_returns_410` |
| REQ-INV-007 | 邮箱不一致 | 403 | EMAIL_MISMATCH | `tests/unit::test_accept_email_mismatch_returns_403` |
| REQ-INV-008 | 接受成功/幂等 | 200 | — | `tests/unit::test_accept_success_and_idempotent` |
| REQ-INV-009 | 撤销非 pending | 409 | INVITATION_NOT_PENDING | `tests/unit::test_revoke_non_pending_returns_409` |
| REQ-INV-010 | 跨租户访问 | 404 | INVITATION_NOT_FOUND | `tests/unit::test_cross_tenant_access_returns_404` / `tests/contract::test_cross_tenant_revoke_returns_404` |
| REQ-INV-011 | 未知 token | 404 | INVITATION_NOT_FOUND | `tests/unit::test_accept_unknown_token_returns_404` |

## 3. 需求评审记录（示意）

- 评审时间：2026-10-08　参与：产品、后端、安全。
- 争议点一：跨租户访问应返回 403 还是 404？**结论**：统一 404（REQ-INV-010），避免通过 403/404 的差异探测资源是否存在。安全同意，记入 ADR-0001。
- 争议点二：admin 能否邀请 owner？**结论**：不能，且在 schema 层（Pydantic/`openapi.yaml`）就不接受 `owner`（REQ-INV-002），而非只在 service 兜底。
- 争议点三：重复接受已 accepted 的邀请如何处理？**结论**：幂等返回 200，不重复建成员（REQ-INV-008），避免客户端重试造成重复 Membership。
- 遗留项：生产认证需从 `X-Demo-User` 换成 OIDC/JWT（本 demo 不实现，正文须说明）。
