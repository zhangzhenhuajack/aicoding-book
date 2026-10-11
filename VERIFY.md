# VERIFY.md — TeamPulse demo 验证记录

> 所有命令与输出摘要均来自本仓库在 2026-10-08 的真实运行。环境：Python 3.12.3、uv 0.10.0、
> Node v22、npm 10、Docker 29、Postgres 16（docker compose）。无 terraform（故 IaC 用 AWS CDK）。

## 1. 后端门禁（backend/，均通过）

| 命令 | 结果 |
|---|---|
| `uv run ruff check .` | `All checks passed!` |
| `uv run ruff format --check .` | `29 files already formatted` |
| `uv run mypy --strict app` | `Success: no issues found in 16 source files` |
| `uv run lint-imports` | `Contracts: 3 kept, 0 broken.`（分层 layers + domain 纯净 + api 不直连 repo/model） |
| `uv run pytest -m "not integration"` | `23 passed, 1 deselected`（unit/contract/architecture，SQLite） |
| `uv run pytest -m integration`（Postgres） | `1 passed, 23 deselected`（部分唯一索引在 Postgres 真实生效） |

三条强制安全测试（均在 `tests/unit/test_invitation_rules.py`）：
- `test_cross_tenant_access_returns_404` —— 跨租户访问返回 404（REQ-INV-010）。
- `test_token_only_stored_as_hash` —— token 只存 SHA-256，明文不落库（REQ-INV-005）。
- `test_accept_expired_returns_410` —— 过期邀请返回 410（REQ-INV-006）。

覆盖率（`--cov=app`）：TOTAL 92%（repositories/models/security/domain 均 ≥98%）。

## 2. Alembic 迁移可逆性（Postgres 16）

```
uv run alembic upgrade head      -> Running upgrade  -> 0001_initial
uv run alembic downgrade -1      -> Running downgrade 0001_initial -> (base)
uv run alembic upgrade head      -> Running upgrade  -> 0001_initial
```

三步全部成功，证明 `0001_initial` 的 `downgrade` 为真实可逆（非空 `pass`），满足 AGENTS.md 迁移护栏与 CI `backend-integration` 作业。

## 3. 变异测试

- 声明依赖 `mutmut`，实际装到 `mutmut==3.8.0`。3.x 把源码复制进 `mutants/` 再隔离跑 pytest，
  在本环境 stats-collection 阶段报 `BadTestExecutionCommandsException`（见 `docs/mutation-demo.md`）。
- 故采用**手动变异**（规格允许的 fallback，也是第 34/36 章描述的手动版）。真实过程、命令与输出
  完整记录在 `docs/mutation-demo.md`：
  - 弱断言假测试 `assert result is not None` 在 `is_expired` 的 `>=`→`>` 变异下**仍然全绿**（变异存活）。
  - 按 REQ-INV-006 补强为边界断言后，对变异代码**变红**（`assert False is True`，变异被杀死），对正确代码转绿。

## 4. 前端（frontend/，均通过）

| 命令 | 结果 |
|---|---|
| `npm install` | `added 211 packages`（成功；npm audit 报若干传递依赖告警，非阻塞） |
| `npx openapi-typescript ../contracts/openapi.yaml -o src/api/schema.d.ts` | 生成成功 |
| `npx tsc --noEmit` | 退出码 0，无类型错误（strict） |
| `npx vitest run` | `Test Files 3 passed (3) / Tests 8 passed (8)` |
| `npx playwright install chromium` + `npx playwright test` | `1 passed (11.9s)` —— 真实 Chromium 跑通“创建→列表出现→撤销”E2E（后端用 route mock） |

E2E 说明：`e2e/invitations.spec.ts` 用 Playwright `page.route("**/api/tenants/**")` 拦截后端，
使 E2E 不依赖真实后端即可验证关键 UI 流程；对接真实后端时去掉 route mock 即可。

## 5. 部署

| 项 | 命令 | 结果 |
|---|---|---|
| 后端镜像 | `docker build -t teampulse-backend:local backend/` | 成功（多阶段、非 root、uv 装依赖） |
| 容器冒烟 | `docker run ... ; curl /docs` | HTTP 200，`/openapi.json` 含 3 条邀请端点 |
| IaC（CDK） | `cd infra && npm install && npx cdk synth` | 成功，生成 `cdk.out/TeampulseStack.template.json`（VPC + ECS Fargate + ALB） |
| 回滚脚本 | `bash -n scripts/rollback.sh` | 语法 OK（`set -euo pipefail`，带确认与 `wait services-stable`） |
| IaC（Terraform） | — | 环境无 terraform，未做；已用 CDK 满足“至少一种通过” |

## 6. 第三方工具 GitHub 地址（逐个 `curl -s -o /dev/null -w '%{http_code}' -L`，全部 200）

| 工具 | 地址 | HTTP |
|---|---|---|
| uv | https://github.com/astral-sh/uv | 200 |
| ruff | https://github.com/astral-sh/ruff | 200 |
| ruff-pre-commit | https://github.com/astral-sh/ruff-pre-commit | 200 |
| gitleaks | https://github.com/gitleaks/gitleaks | 200 |
| pre-commit-hooks | https://github.com/pre-commit/pre-commit-hooks | 200 |
| mypy | https://github.com/python/mypy | 200 |
| import-linter | https://github.com/seddonym/import-linter | 200 |
| mutmut | https://github.com/boxed/mutmut | 200 |
| pytest | https://github.com/pytest-dev/pytest | 200 |
| alembic | https://github.com/sqlalchemy/alembic | 200 |
| fastapi | https://github.com/fastapi/fastapi | 200 |
| pydantic | https://github.com/pydantic/pydantic | 200 |
| sqlalchemy | https://github.com/sqlalchemy/sqlalchemy | 200 |
| vite | https://github.com/vitejs/vite | 200 |
| vitest | https://github.com/vitest-dev/vitest | 200 |
| playwright | https://github.com/microsoft/playwright | 200 |
| testing-library/react | https://github.com/testing-library/react-testing-library | 200 |
| openapi-typescript | https://github.com/openapi-ts/openapi-typescript | 200 |
| aws-cdk | https://github.com/aws/aws-cdk | 200 |

## 7. 未跑通 / 偏离项

- **mutmut 自动化**：3.8.0 隔离执行报错，改用手动变异（规格允许的 fallback），过程真实可复现。
- **Terraform**：环境未安装，用 AWS CDK 满足 IaC 验证（规格要求“至少通过一种”）。
- **pre-commit / gitleaks 实际执行**：`.pre-commit-config.yaml` 已配真实 tag，但未在本环境 `pre-commit run`
  （未安装 pre-commit 可执行）；其底层工具 ruff / import-linter 已单独验证通过。
