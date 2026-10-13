# AGENTS.md — TeamPulse

本文件是本仓库对所有 AI 代理（以及人类贡献者）的**硬约束**。约束靠门禁强制，不靠嘱咐（见第 2 章）。

## 项目一句话

TeamPulse 是一个多租户团队协作看板。本仓库只实现一个功能：**租户邀请（Invitation）**，用于演示规格驱动、契约驱动与分层门禁的完整工程闭环。权威规格见 `../TEAMPULSE-SPEC.md`。

## 技术栈（固定，不得擅自更换）

- 后端：Python 3.12 / FastAPI / Pydantic v2 / SQLAlchemy 2.0（同步 ORM）/ Alembic / pytest / httpx TestClient / 依赖用 **uv** 管理。
- 数据库：PostgreSQL 16（docker compose）；单元/契约/架构测试用 SQLite 内存库，集成测试用 Postgres。
- 前端：Vite + React 18 + TypeScript（strict）/ Vitest + Testing Library / Playwright。
- 契约：`contracts/openapi.yaml`（OpenAPI 3.1），前端类型由 `openapi-typescript` 生成到 `src/api/schema.d.ts`。

## 分层架构（import-linter 强制）

依赖方向只能是：

```
api → services → domain
services → repositories → db
```

硬规则：

- `app.domain` 不得 import `fastapi` / `sqlalchemy` / `app.db` / `app.api`（纯领域，无框架）。
- `app.api` 不得直接 import `app.repositories` 或 `app.db.models`（必须经 service）。
- 所有数据查询必须带 `tenant_id`（在 repository 层强制），严禁裸写跨租户查询。

违反以上任意一条，`lint-imports` 或架构测试会红。

## 多租户隔离（安全硬约束）

- 跨租户访问（`tenant_id` 与资源不匹配，或调用者不是该租户成员）**一律返回 404**，不得返回 403 或泄露资源存在性（REQ-INV-010）。
- 邀请 token 用 `secrets.token_urlsafe(32)` 生成，**只存 SHA-256 哈希**；明文 token 只在创建响应里返回一次，从不落库（REQ-INV-005）。

## 迁移护栏（硬约束）

- `migrations/` 里涉及 `DROP COLUMN` / `DROP TABLE` / `ALTER COLUMN` 改类型的属于破坏性变更：必须停下来、在 PR 描述说明影响并请人确认，不要自行执行。
- 每个迁移必须同时提供可用的 `upgrade` 和 `downgrade`。`downgrade` 不许是空的 `pass`。
- 破坏性变更走 expand-contract 两阶段（见第 23 章），PR 需说明属于 expand 还是 contract 阶段。

## 代码风格

- 不预先抽取只用一次的 helper（借鉴 codex / opencode 的 AGENTS.md）。
- 禁止 `from x import *`（星号导入）。
- 公开函数必须有类型注解；`mypy --strict` 必须绿。
- 单个非机械变更 PR 不超过 500 行。

## 测试纪律

- 失败测试由人写或人严格审定，**不让 AI 顺手生成**（防弱断言自测）。
- service 层测试用真实的内存/临时数据库，只对真正的外部边界做替身，不要用 mock 掉核心依赖。
- 必须覆盖非期望行为（If-Then 分支），不能只测 happy path。
- 本仓库必含三个安全断言：跨租户访问返回 404、token 只存哈希、过期邀请返回 410。

## 认证（演示简化）

demo 用请求头 `X-Demo-User: <email>` 模拟登录。**生产环境必须换成 OIDC/JWT 校验，这只是教学简化。** 测试用 `app.dependency_overrides` 注入用户。

## 前端约定

- 新组件先查 `frontend/src/features/` 里已有组件与设计系统，能复用就不新写。
- 颜色只用 `frontend/src/tokens.css` 的语义令牌（`var(--color-*)`），组件与样式里不得硬编码色值；ESLint 规则会拦。
- 提交前在 `frontend/` 下跑：`npm run lint`、`npx vitest run`、`npx tsc --noEmit`。

## 本地门禁命令（提交前自检）

```bash
cd backend
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict app
uv run lint-imports
uv run pytest
```
