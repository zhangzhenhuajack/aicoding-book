# 附录在线部分

《AI 编程实战：写出能上生产的代码》纸书为控制篇幅，以下附录小节只保留标题，正文全文在此。
仓库：https://github.com/zhangzhenhuajack/aicoding-book（建议 `git clone https://github.com/zhangzhenhuajack/aicoding-book.git teampulse-demo`）。附录 G.3 各章参考来源全文见 `docs/references.md`。

## 附录 A　范式与流派速查：关键事件时间线、能力对照与选型索引

### A.4 本附录对应的仓库与官方入口（核验于 2026-10）

速查时常要直接跳到一手仓库/文档，集中列此，全部经 `curl -L` 核验返回 200。

| 流派 / 主题 | 一手仓库 / 文档 |
|---|---|
| Anthropic（Claude Code） | [github.com/anthropics/claude-code](https://github.com/anthropics/claude-code) |
| Anthropic CI 集成 | [github.com/anthropics/claude-code-action](https://github.com/anthropics/claude-code-action) |
| OpenAI（Codex） | [github.com/openai/codex](https://github.com/openai/codex) |
| OpenAI CI 集成 | [github.com/openai/codex-action](https://github.com/openai/codex-action) |
| 开源 Harness：OpenHands | [github.com/All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands) |
| 开源 Harness：opencode | [github.com/sst/opencode](https://github.com/sst/opencode) |
| 开源 Harness：Aider（AI 占比统计） | [github.com/Aider-AI/aider](https://github.com/Aider-AI/aider) |
| 开源模型底座：DeepSeek | [github.com/deepseek-ai/DeepSeek-V3](https://github.com/deepseek-ai/DeepSeek-V3) |

## 附录 B　项目资料包：AGENTS.md 模板与 TeamPulse 规格、仓库结构及提示词

### B.2 TeamPulse 规格（requirements / design / tasks / ADR）

以下四份文件是第 21–23 章实战的权威依据，摘录自 `.kiro/specs/invitations/` 与 `docs/adr/`。追溯关系：**需求 → 设计/ADR → 任务 → 测试与门禁**。

### B.2.1 requirements.md（EARS 写法，全文）

**requirements.md（EARS 需求摘录）**

```markdown
# 需求：租户邀请（Invitation）

> 采用 EARS 写法。错误码与状态码与 `../../../contracts/openapi.yaml` 及 `TEAMPULSE-SPEC.md` 第 4/5 节逐字一致。
> 认证为演示简化：请求头 `X-Demo-User: <email>` 代表当前登录用户。

**REQ-INV-001｜创建权限**
当一个用户对某租户发起创建邀请的请求时，若该用户是该租户的 owner 或 admin，则系统应当创建邀请并返回 201；若该用户是 member，则系统应当拒绝并返回 403。

**REQ-INV-005｜token 生成与存储**
当创建邀请时，系统应当用 `secrets.token_urlsafe(32)` 生成明文 token，仅在创建响应中返回该明文一次，并且只持久化其 SHA-256 十六进制哈希；系统不应当将明文 token 落库。

**REQ-INV-010｜跨租户隔离**
当请求中的 `tenant_id` 与资源不匹配，或调用者不是该租户成员时，系统应当一律返回 404，不区分“无权限”与“不存在”，以避免泄露资源存在性。

# …（省略：REQ-INV-002 可邀请角色→422、003 重复 pending→409、004 已是成员→409、006 过期→410、007 邮箱不一致→403、008 接受幂等→200、009 撤销限 pending→409、011 未知 token→404，均见仓库 requirements.md）
```

需求另配一张“编号→场景→状态码→错误码→验证点”验收表（11 行，每行映射一个测试名），完整表见仓库 `requirements.md`。

### B.2.2 design.md（关键部分）

摘录 `design.md` 四部分：三方案对比、分层设计、STRIDE、隔离清单。

**design.md（三方案对比 + 分层设计）**

```markdown
# 设计：租户邀请（Invitation）

## 1. 三方案对比（关键决策：token 存储）

| 方案 | 做法 | 优点 | 缺点 | 结论 |
|---|---|---|---|---|
| A 明文存储 | token 明文落库 | 实现最简单，可直接查 | 库被读即全部邀请链接泄露 | 否决 |
| B 对称加密存储 | token 加密后落库，用时解密 | 可取回明文 | 需管理密钥，密钥泄露即全泄露；无取回需求 | 否决 |
| C 仅存哈希（选用） | 只存 SHA-256，明文仅返回一次 | 库泄露不等于 token 泄露；用哈希查询天然等时 | 明文丢了只能重发 | **采用**（REQ-INV-005/011） |

邀请 token 的使用模式是“创建时给用户一次、之后只做校验”，没有“服务端取回明文”的需求，因此选哈希存储（方案 C），与密码存储同理。
# …（省略：第 2 节分层设计 api/domain/repositories 三层职责，与第 21/23 章重复，见仓库 design.md）
```

**design.md（STRIDE + 隔离清单）**

```markdown
## 5. STRIDE 威胁模型

| 威胁 | 场景 | 缓解 |
|---|---|---|
| **S**poofing（伪装） | 冒充他人接受邀请 | 接受时校验登录邮箱与邀请邮箱一致（REQ-INV-007）；生产换 OIDC/JWT |
| **I**nformation disclosure（泄露） | 探测某租户/邀请是否存在 | 跨租户一律 404、不区分无权/不存在（REQ-INV-010）；列表不返回 token/token_hash |
| **E**levation of privilege（提权） | member 创建邀请、admin 邀请 owner | 创建限 owner/admin（REQ-INV-001）；schema 不接受 owner（REQ-INV-002） |
# …（省略：Tampering 行，与 token 只存哈希论点重复，见仓库）

## 6. 租户隔离检查清单

- [ ] service 所有入口先 `_require_tenant_member`，非成员抛 `INVITATION_NOT_FOUND`（404）。
- [ ] 列表响应不含 `token` / `token_hash`——契约测试 `test_list_omits_token_fields`。
# …（省略：api 层不直连 repositories/models 一条，见仓库）
```

### B.2.3 tasks.md（全文）

**tasks.md（T1–T10 摘录，含验证口径）**

```markdown
# 任务：租户邀请（Invitation）

> 每个任务的“完成”= 对应测试全绿 + 门禁全过。任务按依赖顺序排列，粒度对齐 PR 行数上限（100–300 行）。

- [x] T1 契约：在 `contracts/openapi.yaml`（OpenAPI 3.1）定义 4 个端点、请求/响应/错误码。
- [x] T2 领域层：`app/domain/invitation.py`（Role/状态/`compute_expiry`/`normalize_email`/`is_expired`/`DomainError`）。
- [x] T6 service·非期望行为：REQ-INV-003/004/006/007/009/010/011 的 If-Then 分支。
- [x] T9 测试与变异：单元/契约/架构（SQLite）+ 集成（Postgres）+ Playwright E2E + 变异测试演示。
# …（省略：T3 数据模型+迁移、T4 repository、T5 service 正常路径、T7 路由+鉴权、T8 前端、T10 部署，每任务含“验证”行，见仓库 tasks.md）
```

### B.2.4 ADR-0001（全文）

**docs/adr/0001-tenant-isolation.md（背景 + 决策）**

```markdown
# ADR-0001：租户隔离一律返回 404，查询强制带 tenant_id，token 只存哈希
# …（省略：状态 Accepted、关联需求 REQ-INV-005/010/011 两行元信息）

## 背景（Context）

TeamPulse 是多租户系统，一个用户只能看到自己所属租户的邀请。两类泄露风险必须堵死：

1. **资源存在性泄露**：若对“存在但无权访问”的邀请返回 403、对“不存在”的返回 404，攻击者可用 403/404 的差异枚举出哪些 `invitation_id`/`tenant_id` 真实存在。
2. **凭证泄露**：邀请 token 等价于一次性访问凭证。若明文落库，数据库一旦被读，所有未使用邀请即被接管。

## 决策（Decision）

1. **跨租户访问一律返回 404。** 当 `tenant_id` 与资源不匹配，或调用者不是该租户成员时，统一返回 404 `INVITATION_NOT_FOUND`，不区分“无权限（403）”与“不存在（404）”。实现上，service 每个入口先 `_require_tenant_member`，失败即抛 `INVITATION_NOT_FOUND`。
# …（省略：决策 2「查询强制带 tenant_id」，原文编号即由 1 跳至 3，见仓库 ADR-0001；另「为什么 404 优于 403」论点与此条同义，见正文第 13 章）
3. **token 只存 SHA-256 哈希。** 明文 token 用 `secrets.token_urlsafe(32)` 生成，仅在创建响应返回一次，从不落库；查询用哈希比对，使“token 是否存在”不改变数据库查询路径（抗时序侧信道）。
```

### B.3 仓库结构（真实目录树）

仓库骨架（`find` 整理，已折叠缓存与构建产物，完整树见随书仓库 `https://github.com/zhangzhenhuajack/aicoding-book`，clone 到 `teampulse-demo/` 目录）：根目录有 `AGENTS.md`、`VERIFY.md`、`docker-compose.yml`、`.github/workflows/ci.yml`、`contracts/openapi.yaml`、`.kiro/specs/invitations/`（见 B.2）、`docs/adr/`。`backend/app/` 按 api / services / domain / repositories / db / core 六层分包，含 `migrations/` 与 unit / contract / integration / architecture 四类测试；`frontend/` 为 Vite + React + TS；`infra/` 为 AWS CDK（VPC + ECS Fargate + ALB），含回滚脚本。

### B.5 本地复现步骤（与 VERIFY.md 一致）

以下命令与 `VERIFY.md` 的 2026-10-08 真实运行一致（Python 3.12、uv 0.10、Node 22、Docker 29、PostgreSQL 16），按“后端 → 迁移 → 前端 → 部署”顺序复现，均在 `teampulse-demo/` 内。

步骤 1　后端门禁（VERIFY §1）
```bash
cd teampulse-demo/backend
uv sync --all-extras --dev          # 按 uv.lock 还原依赖
uv run mypy --strict app            # 严格类型检查
uv run lint-imports                 # 分层契约（import-linter）
uv run pytest -m "not integration" --cov=app --cov-report=term-missing  # SQLite：单元/契约/架构
```

结果：`lint-imports: Contracts: 3 kept, 0 broken.`，`pytest: 23 passed`（覆盖率 92%，示意）。

步骤 2　迁移可逆性（VERIFY §2）
```bash
docker compose up -d postgres        # postgres:16，含 healthcheck
uv run alembic upgrade head          # -> 0001_initial
uv run alembic downgrade -1          # 0001_initial -> base（真实可逆，非空 pass）
uv run alembic upgrade head          # 再次升级
uv run pytest -m integration         # 部分唯一索引在 Postgres 真实生效
```

结果：up/down/up 成功；`pytest -m integration: 1 passed`。

步骤 3　前端（VERIFY §4）
```bash
cd teampulse-demo/frontend
npm ci                               # 按 package-lock.json 还原（约 211 包）
npm run gen:types                    # 由 ../contracts/openapi.yaml 生成 src/api/schema.d.ts
npm run build                        # tsc --noEmit && vite build
npx playwright test
```

结果：tsc 退出码 0；vitest 8 passed；playwright 1 passed。

步骤 4　部署与回滚（VERIFY §5）
```bash
docker build -t teampulse-backend:local backend/
npx cdk synth                         # 生成 cdk.out/TeampulseStack.template.json（VPC+ECS Fargate+ALB）
bash -n scripts/rollback.sh           # set -euo pipefail，语法 OK
```

结果：build 成功、`/docs` 返回 200、cdk synth 生成模板、rollback.sh 语法 OK。

偏离项（与 VERIFY §7 一致）
①**mutmut** 报错，改用手动变异（见 `docs/mutation-demo.md`）。②**Terraform** 未装，用 CDK 满足“至少一种 IaC”。③**pre-commit** 未装，其底层 ruff / import-linter 已单独验证。

### B.6 本资料包包含的文件清单

本附录收录/引用的 TeamPulse 文件：`AGENTS.md` 与通用模板（B.1）、`requirements.md` / `design.md`（§1/2/5/6）/ `tasks.md` 与 `0001-tenant-isolation.md`（B.2）、仓库结构（B.3）、14 条提示词（B.4）、与 `VERIFY.md` 一致的复现命令（B.5）。

## 附录 C　质量自动化参考：门禁清单、验证器与 Hooks 配置样例

### C.3 Hooks 与配置样例

四类真实可照抄的配置，地址核验于 2026-10。

### C.3.1 pre-commit：提交前秒级门禁

安装：pre-commit
仓库 [github.com/pre-commit/pre-commit](https://github.com/pre-commit/pre-commit)；密钥扫描器 [detect-secrets](https://github.com/Yelp/detect-secrets)、[gitleaks](https://github.com/gitleaks/gitleaks)。`pre-commit install` 装进 `.git/hooks`。

TeamPulse 的 `.pre-commit-config.yaml`（本书示例）：

```yaml
repos:
  - repo: local
    hooks:
      - id: secret-scan            # 密钥扫描，命中即阻断
      # …（省略：affected-unit-tests 只跑受影响的包、struct-test-frontend 结构测试）
```

纪律
hook 不许被 `--no-verify` 绕过；绕过率是门禁的失效信号。

### C.3.2 Claude Code hooks（事件触发的确定性动作）

安装：Claude Code
仓库 [github.com/anthropics/claude-code](https://github.com/anthropics/claude-code)，配置写在 `.claude/settings.json`。

hooks 把确定性命令挂在生命周期事件上，如 `PostToolUse` 在文件写入后自动跑格式化/lint：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "ruff format $CLAUDE_FILE_PATHS" },
          { "type": "command", "command": "ruff check --fix $CLAUDE_FILE_PATHS" }
        ]
      }
    ]
  }
}
```

格式化器 [ruff](https://github.com/astral-sh/ruff)。`PreToolUse` 可在执行 Bash 前准入，把 **Deny > Ask > Allow** 落到 hook 层。

### C.3.3 Kiro hooks（规格驱动下的自动化检查）

安装：Kiro
官方 [kiro.dev](https://kiro.dev/)。hooks 与 Steering/Specs 放在 `.kiro/` 目录，随代码版本化。

Kiro 的 hooks 与 `.kiro/steering`（约定）、`.kiro/specs` 配合，构成“告知 + 约束”：

```yaml
# .kiro/hooks/on-save-test.yaml（示意结构）
on: file.save
run:
  - command: "bun run test:affected"
```

### C.3.4 Codex 配置（沙箱、权限档、结构化输出）

安装：Codex CLI / codex-action
仓库 [github.com/openai/codex](https://github.com/openai/codex)、CI 用 [codex-action](https://github.com/openai/codex-action)。非交互 `codex exec` 默认只读沙箱。

把 Codex 接进 CI 的关键是**只读沙箱 + 权限档 + 结构化输出**（[openai/codex](https://github.com/openai/codex) 的 `issue-labeler.yml` 原文要点，核验于 2026-08）：

```yaml
- id: codex
  with:
    safety-strategy: drop-sudo      # 调用前撤销 sudo、清 capability
    sandbox: read-only              # agent 跑在只读沙箱
```

三个加固点：`drop-sudo`（降权）、`read-only`（只读文件系统）、`output-schema`（强制 JSON）。**永远不要把 Agent 的输出直接拼进 shell 命令**——让它输出结构化数据，校验后再动作。

### C.4 工具与官方地址索引（核验于 2026-10）

取自真实仓库原文的片段已标核验日期（2026-08-24）；标【本书示例】的技术真实可复现但不声称来自生产仓库；Kiro hook 字段为示意结构。

| 工具 | 地址 |
|---|---|
| pre-commit | [github.com/pre-commit/pre-commit](https://github.com/pre-commit/pre-commit) |
| detect-secrets | [github.com/Yelp/detect-secrets](https://github.com/Yelp/detect-secrets) |
| gitleaks | [github.com/gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) |
| ruff | [github.com/astral-sh/ruff](https://github.com/astral-sh/ruff) |
| cargo-shear | [github.com/Boshen/cargo-shear](https://github.com/Boshen/cargo-shear) |
| nextest | [github.com/nextest-rs/nextest](https://github.com/nextest-rs/nextest) |
| just | [github.com/casey/just](https://github.com/casey/just) |
| mutmut | [github.com/boxed/mutmut](https://github.com/boxed/mutmut) |
| Stryker | [github.com/stryker-mutator/stryker-js](https://github.com/stryker-mutator/stryker-js) |
| Playwright | [github.com/microsoft/playwright](https://github.com/microsoft/playwright) |
| axe-core | [github.com/dequelabs/axe-core](https://github.com/dequelabs/axe-core) |
| claude-code | [github.com/anthropics/claude-code](https://github.com/anthropics/claude-code) |
| codex / codex-action | [github.com/openai/codex](https://github.com/openai/codex) · [codex-action](https://github.com/openai/codex-action) |
| OpenHands / opencode | [OpenHands](https://github.com/All-Hands-AI/OpenHands) · [opencode](https://github.com/sst/opencode) |

## 附录 D　安全交付检查清单：CI/CD 加固、发布审批与回滚

### D.3 工具与官方地址索引（核验于 2026-10）

| 用途 | 工具 / 文档 | 地址 |
|---|---|---|
| Anthropic CI 集成（OIDC / fork 防护 / 成本字段） | claude-code-action | [github.com/anthropics/claude-code-action](https://github.com/anthropics/claude-code-action) |
| OpenAI CI 集成（读写分离 / 结构化输出） | codex-action | [github.com/openai/codex-action](https://github.com/openai/codex-action) |
| Codex CLI / 防注入 prompt 范本 | codex | [github.com/openai/codex](https://github.com/openai/codex) |
| Anthropic Claude Code | claude-code | [github.com/anthropics/claude-code](https://github.com/anthropics/claude-code) |
| 密钥隔离 / live E2E 凭证清单 | OpenHands | [github.com/All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands) |
| 外部确定性策略兜底（动作允许/拒绝） | Open Policy Agent | [github.com/open-policy-agent/opa](https://github.com/open-policy-agent/opa) |

标注说明
Rule of Two、OIDC/读写分离/fork 禁令等均为厂商官方原话或仓库原文，核验于 2026-08-24；标【本书示例】的 YAML/脚本技术真实可复现但不声称来自生产；跨厂商漏洞（Comment and Control / PromptPwnd）为社区安全媒体来源。本附录无仍标【未证实】的事实性数字。

## 附录 E　团队改进工具：Token 优化清单、回顾会模板与度量看板

### E.2　回顾会 2.0 模板（照着开）

传统 Sprint 回顾会在 AI 时代失效：**AI 没有 Sprint 之间的记忆，不会因为“上次被绊过”而自觉改正**。教训若没写成下个 Sprint 必然撞上的约束，同一个 AI 会把同样的坑再踩一遍。核心一句话（见第 29 章；闭环见图 E-1）：

唯一产出标准
每一条回顾结论都必须落地成一条机械约束——一条新 hook、一条新 Steering 规则，或一个新结构测试，否则等于没开这个会。

（图 E-1　回顾会 2.0 的闭环（见第 29 章）：见网页版）

### 六问议程（传统三问 + AI 时代三问）

| # | 问题 | 要点 |
|---|---|---|
| 一 | 什么进展顺利？ | 分清“真顺利”（交付稳、返工少）还是“速度幻觉”（产出多）。 |
| 二 | 什么出了问题？ | 聚焦事故、返工、被推翻的决策。 |
| 三 | 下一轮改进什么？ | 每条须能回答“变成哪条机械约束”。 |
| 四 ★ | **AI 在哪里出错了？** | 具体到失败模式（幻觉哪个 API？造哪个假测试？），**变成可积累的清单**——同类第二次出现就该有约束。 |
| 五 ★ | **为什么门禁没拦住它？** | 最关键一问。**坏产出进主干，第一追问对象是门禁，不是 AI。** |
| 六 | 规则/技能资产怎么调整？ | 哪条 Steering 过期？哪个 Skill 该归档？对应资产生命周期。 |

第五问有三种典型答案：

- **没覆盖这一类** → 新增一道门禁（结构测试 / 扫描 / lint）。
- **覆盖了但被绕过** → 查是否被大量 `--no-verify` 绕过或门禁有漏洞。
- **无法机械化** → 写进“人类终审必查项”清单。

### 把一条教训编译成一条约束

| 教训类型 | 落地形态 | 真实例子 |
|---|---|---|
| “AI 总在某类操作上出错” | 触发式 hook | 改迁移文件 → hook 要求配套回滚脚本。 |
| “AI 需要知道某个项目约定” | Steering 规则 | “禁止前端直连后端 endpoint”写进 Steering。 |
| “AI 违反架构不变量” | 结构测试 | 断言分层依赖方向，越界即红（如 OpenHands 的 `no-direct-agent-server-calls.test.ts`）。 |
| “AI 反复提交超大 PR” | Steering + 行数门禁 | “不要预先抽取只用一次的辅助函数”（opencode）+ “非机械变更不超过 800 行”（codex）。 |
| “AI 提交糊弄的绿测试” | agentStop hook | 提交后跑变异测试，存活率过高则阻断合并。 |

共同结构：**教训 → 找到能机械检查它的形态 → 写成下个 Sprint 强制生效的规则。**不能机械化的交给人类终审。

### 可照抄的回顾会 Markdown 模板

存成 `retro-YYYY-MM-DD.md` 逐格填。关键是最后两栏——指明“落地成哪条约束”和“负责人/期限”。

```markdown
# Sprint 回顾会 2.0 · {Sprint 编号} · {日期}

数据准备：返工率 ___% ｜ 门禁拦截率 ___% ｜ AI 提议采纳率 ___% ｜ 评审否决率 ___%
（以上为示意，开会前从看板取真实数据）

# …（省略：第一至三问为传统三问原样保留；完整模板见随书仓库 book-examples/appE/demo01.md）

## 四、★ AI 在哪里出错了？（归类，找出出现 ≥2 次的类别）
| 失败模式 | 出现次数 | 示例（PR/任务号） | 是否已有同类约束 |

## 五、★ 为什么门禁没拦住它？（第一追问对象是门禁，不是 AI）
| 溜进主干的坏产出 | 门禁缺哪一层？ | 修复：没覆盖→新增 / 被绕过→查 --no-verify / 无法机械化→写入人类必查清单 |

## 本次会议产出的机械约束（唯一验收标准：此表非空）
| 约束 | 形态（hook/steering/结构测试） | 对应第几问的教训 | 负责人 | 期限 | 验证方式 |
```

## 附录 F　术语表与延伸阅读

### F.2　延伸阅读（各附一句推荐理由）

按书籍 / 论文 / 官方文档三类列出。URL 均在 2026-10 核实可访问；少数出版社官网对爬虫返回 403 的书目改用作者页或出版方页，仍可打开。

### 书籍

- **《Accelerate》（Forsgren、Humble、Kim）**——DORA 四指标的理论根基，读懂第 2、30 章“用什么量交付效能”的源头。[https://itrevolution.com/product/accelerate/](https://itrevolution.com/product/accelerate/)
- **《Refactoring》（Martin Fowler）**——重构经典，第 27 章“先有测试再改遗留逻辑”的方法论母本。[https://martinfowler.com/books/refactoring.html](https://martinfowler.com/books/refactoring.html)
- **《Site Reliability Engineering》（Google，免费在线）**——SLO、告警、运维值守的权威读物，第 27 章背景支撑。[https://sre.google/books/](https://sre.google/books/)
- **《The Twelve-Factor App》（在线小书）**——配置、依赖、构建发布分离的十二条原则，第 26 章部署的基线。[https://12factor.net/](https://12factor.net/)
- **Martin Fowler 架构与方法论文集（在线）**——ADR、持续集成、演进式架构等短文集合，第 13、22 章常备参考。[https://martinfowler.com/](https://martinfowler.com/)

### 论文

- **Wei et al., “Chain-of-Thought Prompting”（arXiv:2201.11903）**——思维链奠基论文，第 3 章“推理引导”、第 34 章“思考量”的起点。[https://arxiv.org/abs/2201.11903](https://arxiv.org/abs/2201.11903)
- **Jimenez et al.，“SWE-bench”（arXiv:2310.06770）**——第 2 章“分数是模型和 Harness 合写的”必读原文。[https://arxiv.org/abs/2310.06770](https://arxiv.org/abs/2310.06770)
- **Chen et al., “Evaluating LLMs Trained on Code”（arXiv:2107.03374）**——HumanEval 与 Codex 的原始评测，看清代码模型评测口径。[https://arxiv.org/abs/2107.03374](https://arxiv.org/abs/2107.03374)
- **Brown et al., “Language Models are Few-Shot Learners”（arXiv:2005.14165）**——few-shot 概念来源，第 3 章 Prompt Engineering 的理论背景。[https://arxiv.org/abs/2005.14165](https://arxiv.org/abs/2005.14165)
- **GPT-4 Technical Report（arXiv:2303.08774）**——理解当代大模型能力边界与评测方式，配第 2 章“证据适用范围”读。[https://arxiv.org/abs/2303.08774](https://arxiv.org/abs/2303.08774)

### 官方文档

- **Anthropic “Building effective agents”**——朴素讲清代理怎么搭，第 5–7 章 Harness/Loop 的入门。[https://www.anthropic.com/engineering/building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents)
- **Anthropic “Prompt caching”**——第 34 章省 Token 一切数字的一手出处，务必亲读“断点反模式”那段。[https://docs.claude.com/en/docs/build-with-claude/prompt-caching](https://docs.claude.com/en/docs/build-with-claude/prompt-caching)
- **Kiro 官方文档**——规格驱动开发的完整能力说明，第 9 章与第 5 篇实战参考。[https://kiro.dev/docs/](https://kiro.dev/docs/)
- **Model Context Protocol 文档**——自己接工具/数据源给 AI 用，从这里开始。[https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)
- **GitHub CodeQL 文档**——把代码当数据库查漏洞的实操，第 17 章 Security Agent 落地参考。[https://codeql.github.com/](https://codeql.github.com/)
- **OWASP Top 10 for LLM Applications**——提示注入等 LLM 应用风险的权威清单，第 19 章 CI 安全治理必查。[https://genai.owasp.org/llm-top-10/](https://genai.owasp.org/llm-top-10/)
- **GitHub Docs: OIDC in AWS**——CI 里用短期凭证替代长期密钥的官方步骤，第 19 章身份与密钥实操。[https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)

## 附录 G　参考来源

### G.1　分级来源索引（URL 已核实可访问）

下面汇总全书主要的一手与权威来源，按本书的四级可信度标注分组。所有 URL 均在 2026-10 用 web_fetch / curl（超时 15 秒）核实可访问（HTTP 200）；核实中打不开或被反爬拦截的候选见本节末尾说明。

#### 【一手·官方】官方文档 / 官方工程博客 / 官方仓库

1. Anthropic，“Prompt caching”（缓存三类 Token 口径、1.25×/2× 写入与 0.1× 读取倍数、最小可缓存长度、失效层级与断点反模式——第 34 章成本章的核心一手来源），[https://docs.claude.com/en/docs/build-with-claude/prompt-caching](https://docs.claude.com/en/docs/build-with-claude/prompt-caching)。
2. Anthropic, “Building effective agents”（代理设计原则、生成-评判与反馈机制——第 7 章流派分析依据），[https://www.anthropic.com/engineering/building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents)。
3. Anthropic，“Claude Code overview”（Claude Code 的能力与 CLAUDE.md 约定文件），[https://docs.claude.com/en/docs/claude-code/overview](https://docs.claude.com/en/docs/claude-code/overview)。
4. OpenAI，“Prompt caching”（OpenAI 侧缓存机制与断点规则；本书对其具体折扣百分比不采用第三方说法，以此官方页为准——第 34 章），[https://platform.openai.com/docs/guides/prompt-caching](https://platform.openai.com/docs/guides/prompt-caching)。
5. Kiro 官方文档（Steering、Specs、Hooks、Skills、MCP 等能力——第 9 章依据），[https://kiro.dev/docs/](https://kiro.dev/docs/)。
6. Model Context Protocol 官方站（MCP 协议规范——第 9 章），[https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)。
7. GitHub，“github-mcp-server” 官方仓库（MCP Server 安装示例——第 5 篇安装块来源），[https://github.com/github/github-mcp-server](https://github.com/github/github-mcp-server)。
8. GitHub CodeQL 官方站（代码查询引擎与安全扫描——第 17 章 Security Agent 依据），[https://codeql.github.com/](https://codeql.github.com/)。
9. GitHub Docs, “Configuring OpenID Connect in Amazon Web Services”（OIDC 短期凭证实操——第 19 章身份与密钥），[https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)。
10. Aider，“Repository map”（repo map 用 tree-sitter 构建的机制——第 34 章省 Token 手册），[https://aider.chat/docs/repomap.html](https://aider.chat/docs/repomap.html)。
11. SWE-bench 官方站（评测基准构成与排行——第 2 章度量与证据），[https://www.swebench.com/](https://www.swebench.com/)。
12. SWE-agent 官方仓库（学术界代表性编码代理 Harness——第 10 章开源生态），[https://github.com/SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent)。
13. OpenHands 官方仓库（结构测试与开源代理框架——第 10、14 章），[https://github.com/All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands)。
14. agents.md（AGENTS.md 约定的社区规范站——第 4、14 章），[https://agents.md/](https://agents.md/)。
15. GitHub Copilot 官方页（代码补全与评审产品对照——第 16 章），[https://github.com/features/copilot](https://github.com/features/copilot)。

#### 【一手·研究】论文与研究机构报告

1. METR, “Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity”（资深开发者高估 AI 加速——第 2 章“证据的时间边界”关键依据），[https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)。
2. Jimenez et al., “SWE-bench: Can Language Models Resolve Real-World GitHub Issues?”（arXiv:2310.06770，SWE-bench 原始论文——第 2 章），[https://arxiv.org/abs/2310.06770](https://arxiv.org/abs/2310.06770)。
3. Chen et al., “Evaluating Large Language Models Trained on Code”（arXiv:2107.03374，HumanEval 与 Codex 原始评测——第 3 章范式起点），[https://arxiv.org/abs/2107.03374](https://arxiv.org/abs/2107.03374)。
4. Bavarian et al., “Efficient Training of Language Models to Fill in the Middle”（arXiv:2207.14255，FIM 代码补全——第 3 章 Prompt Engineering 技术背景），[https://arxiv.org/abs/2207.14255](https://arxiv.org/abs/2207.14255)。
5. Kocetkov et al., “The Stack: 3 TB of permissively licensed source code”（arXiv:2211.15533，代码训练数据集——第 10 章开源生态背景），[https://arxiv.org/abs/2211.15533](https://arxiv.org/abs/2211.15533)。

#### 【官方转述 / 社区】标准、框架与社区资源

1. DORA（DevOps Research and Assessment）官方站（交付周期/部署频率/变更失败率/恢复时间四指标定义——第 2、30 章），[https://dora.dev/](https://dora.dev/)。
2. OWASP, “Top 10 for Large Language Model Applications”（提示注入等 LLM 应用风险清单——第 19 章安全治理），[https://genai.owasp.org/llm-top-10/](https://genai.owasp.org/llm-top-10/)。

核实中被剔除/替换的 URL
以下候选未写入正文：OpenAI 的 `openai.com/index/introducing-codex/` 等营销页在 curl 下返回 403（Cloudflare 反爬），虽经 web_fetch 确认页面真实存在，但为保证读者可直接打开，已改用返回 200 的官方技术文档 `platform.openai.com/docs/guides/prompt-caching` 替代；GitHub OIDC 文档的旧路径 `.../actions/security-guides/.../configuring-openid-connect-in-amazon-web-services` 返回 404，已更正为现行路径（见上）。关于 OpenAI 缓存折扣的三个相互冲突的第三方数字（50%/75%/90%）按引用纪律一律不采用。
