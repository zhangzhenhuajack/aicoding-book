# 设计：租户邀请（Invitation）

## 1. 三方案对比（关键决策：token 存储）

| 方案 | 做法 | 优点 | 缺点 | 结论 |
|---|---|---|---|---|
| A 明文存储 | token 明文落库 | 实现最简单，可直接查 | 库被读即全部邀请链接泄露 | 否决 |
| B 对称加密存储 | token 加密后落库，用时解密 | 可取回明文 | 需管理密钥，密钥泄露即全泄露；无取回需求 | 否决 |
| C 仅存哈希（选用） | 只存 SHA-256，明文仅返回一次 | 库泄露不等于 token 泄露；用哈希查询天然等时 | 明文丢了只能重发 | **采用**（REQ-INV-005/011） |

邀请 token 的使用模式是“创建时给用户一次、之后只做校验”，没有“服务端取回明文”的需求，因此选哈希存储（方案 C），与密码存储同理。

## 2. 分层设计（import-linter 强制）

```
api  ──▶ services ──▶ domain
             │
             └──▶ repositories ──▶ db
```

- `app.api`（路由 + deps）：只做 HTTP ↔ service 翻译与错误码映射；**不得** import `app.repositories` / `app.db.models`。
- `app.services`：业务规则（REQ-INV-001~011）、租户成员校验、组合根 `build_service`。
- `app.domain`：纯领域对象与规则（Role/状态/过期/邮箱规范化）；**不得** import `fastapi` / `sqlalchemy` / `app.db` / `app.api`。
- `app.repositories`：唯一访问 `app.db.models` 的层；所有邀请查询必带 `tenant_id`（按 token 哈希查询除外，由 service 补成员校验）。
- `app.db`：SQLAlchemy 模型与会话。

分层由 `pyproject.toml` 的 `[tool.importlinter]` 三条契约机械守护（layers + 两条 forbidden）。

## 3. 数据模型（与 `app/db/models.py` 一致）

- `Tenant(id uuid, name)`
- `User(id uuid, email unique lower-case)`
- `Membership(tenant_id, user_id, role∈{owner,admin,member})`，主键 `(tenant_id, user_id)`
- `Invitation`：
  - `id uuid`、`tenant_id`、`email`（存小写）、`role∈{admin,member}`
  - `token_hash`（SHA-256 十六进制，带索引）
  - `status∈{pending,accepted,revoked,expired}`
  - `expires_at`（创建 + 7 天 UTC）、`created_by`、`created_at`、`accepted_at`
  - 部分唯一索引：`UNIQUE(tenant_id, email) WHERE status='pending'`（Postgres 真实部分索引；SQLite 退化为应用层查 pending 保证）

## 4. API（与 `openapi.yaml` 一致）

| 方法 | 路径 | 成功码 |
|---|---|---|
| POST | `/api/tenants/{tenant_id}/invitations` | 201（含一次性 `token`） |
| GET | `/api/tenants/{tenant_id}/invitations?status=pending` | 200（不含 token/token_hash） |
| POST | `/api/tenants/{tenant_id}/invitations/{invitation_id}/revoke` | 200 |
| POST | `/api/invitations/accept` | 200 |

错误体统一：`{"error": {"code": "...", "message": "..."}}`。错误码→状态映射见 `app/api/invitations.py::_CODE_TO_STATUS`。

## 5. STRIDE 威胁模型

| 威胁 | 场景 | 缓解 |
|---|---|---|
| **S**poofing（伪装） | 冒充他人接受邀请 | 接受时校验登录邮箱与邀请邮箱一致（REQ-INV-007）；生产换 OIDC/JWT |
| **T**ampering（篡改） | 篡改 token 猜测有效邀请 | token 256-bit 随机、只存哈希、未知返回 404（REQ-INV-005/011） |
| **R**epudiation（抵赖） | 否认创建/撤销 | 记录 `created_by`、`created_at`、`accepted_at` 审计字段 |
| **I**nformation disclosure（泄露） | 探测某租户/邀请是否存在 | 跨租户一律 404、不区分无权/不存在（REQ-INV-010）；列表不返回 token/token_hash |
| **D**enial of service | 暴力枚举 token | token 空间大 + 哈希查询等时；（生产补限流） |
| **E**levation of privilege（提权） | member 创建邀请、admin 邀请 owner | 创建限 owner/admin（REQ-INV-001）；schema 不接受 owner（REQ-INV-002） |

## 6. 租户隔离检查清单

- [ ] repository 每个邀请查询（除按 token 哈希）都带 `tenant_id`——由 `tests/architecture::test_repository_invitation_queries_carry_tenant_id` 静态校验。
- [ ] service 所有入口先 `_require_tenant_member`，非成员抛 `INVITATION_NOT_FOUND`（404）。
- [ ] 跨租户撤销/读取返回 404——单测 + 契约测试覆盖。
- [ ] 列表响应不含 `token` / `token_hash`——契约测试 `test_list_omits_token_fields`。
- [ ] api 层不直连 repositories/models——import-linter 契约守护。
