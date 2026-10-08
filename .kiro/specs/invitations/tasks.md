# 任务：租户邀请（Invitation）

> 每个任务的“完成”= 对应测试全绿 + 门禁全过。任务按依赖顺序排列，粒度对齐 PR 行数上限（100–300 行）。

- [x] T1 契约：在 `contracts/openapi.yaml`（OpenAPI 3.1）定义 4 个端点、请求/响应/错误码。
      验证：契约文件可解析、`tests/contract::test_openapi_file_is_valid_31` 绿；前端 `openapi-typescript` 能生成 `schema.d.ts`。
- [x] T2 领域层：`app/domain/invitation.py`（Role/状态/`compute_expiry`/`normalize_email`/`is_expired`/`DomainError`）。
      验证：`tests/architecture::test_domain_imports_no_framework` 绿。
- [x] T3 数据模型 + 迁移：`app/db/models.py` + Alembic `0001_initial`（含部分唯一索引、真实 downgrade）。
      验证：`alembic upgrade head → downgrade -1 → upgrade head` 在 Postgres 可逆（CI `backend-integration`）。
- [x] T4 repository：`InvitationRepository` 等，所有邀请查询带 `tenant_id`。
      验证：`tests/architecture::test_repository_invitation_queries_carry_tenant_id` 绿。
- [x] T5 service·正常路径：`InvitationService.create`/`accept` happy path（REQ-INV-001/005/008）。
      验证：`test_owner_can_create_invitation`、`test_accept_success_and_idempotent` 绿。
- [x] T6 service·非期望行为：REQ-INV-003/004/006/007/009/010/011 的 If-Then 分支。
      验证：每条 REQ-INV-00x 至少一个异常路径单测绿（见 requirements.md 验收表）。
- [x] T7 路由 + 鉴权 + 错误映射：`app/api/invitations.py` + `deps.py`（`X-Demo-User` 登录、错误码→状态）。
      验证：`tests/contract/*` 端到端绿；import-linter 三契约 KEPT。
- [x] T8 前端：`features/invitations/{api.ts,InviteForm,InvitationList,AcceptInvitePage}` + `schema.d.ts`。
      验证：`tsc --noEmit` 0 错；Vitest 全绿。
- [x] T9 测试与变异：单元/契约/架构（SQLite）+ 集成（Postgres）+ Playwright E2E + 变异测试演示。
      验证：`pytest` 全绿；`docs/mutation-demo.md` 记录“假测试被揭穿→补强→杀死变异体”。
- [x] T10 部署：`backend/Dockerfile`、`infra/`（CDK）、`scripts/rollback.sh`。
      验证：`cdk synth` 通过；`docker build` 通过（或记录原因）。
