# aicoding-book

《AI 编程实战：写出能上生产的代码》（Prompt → Context → Harness 三代方法 + FastAPI/React 完整项目）的随书仓库。书中写“随书仓库 teampulse-demo/<路径>”或“随书仓库 book-examples/…”时，均指本仓库根目录下的对应路径。

| 目录 / 文件 | 内容 |
|---|---|
| `backend/` | TeamPulse 后端：FastAPI + SQLAlchemy + Alembic + PostgreSQL（第 20–27 章） |
| `frontend/` | TeamPulse 前端：React + TypeScript + Vite，含 Vitest / Playwright / axe 测试（第 24 章） |
| `contracts/` | OpenAPI 契约（第 22–23 章） |
| `infra/`、`scripts/` | 部署（CDK）与回滚脚本（第 26–27 章） |
| `.kiro/specs/invitations/` | 邀请功能的 requirements / design / tasks（第 21–23 章） |
| `AGENTS.md`、`VERIFY.md`、`.pre-commit-config.yaml`、`.github/workflows/ci.yml` | 给 Agent 的项目约定、验证清单、提交前门禁与 CI（第 20 章） |
| `book-examples/<章>/demoNN.*` | 书中“本书示例”类 Demo 的完整可运行代码（书里只印核心片段） |
| `docs/references.md` | 附录 G.3 各章参考来源全文（纸书只印 G.1、G.2） |
| `docs/adr/` | 架构决策记录样例（附录 B） |

快速开始与验证步骤见 `VERIFY.md`。
