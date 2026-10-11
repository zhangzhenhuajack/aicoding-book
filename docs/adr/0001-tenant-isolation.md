# ADR-0001：租户隔离一律返回 404，查询强制带 tenant_id，token 只存哈希

- 状态（Status）：Accepted（2026-10-08）
- 关联需求：REQ-INV-005、REQ-INV-010、REQ-INV-011

## 背景（Context）

TeamPulse 是多租户系统，一个用户只能看到自己所属租户的邀请。两类泄露风险必须堵死：

1. **资源存在性泄露**：若对“存在但无权访问”的邀请返回 403、对“不存在”的返回 404，攻击者可用 403/404 的差异枚举出哪些 `invitation_id`/`tenant_id` 真实存在。
2. **凭证泄露**：邀请 token 等价于一次性访问凭证。若明文落库，数据库一旦被读，所有未使用邀请即被接管。

## 决策（Decision）

1. **跨租户访问一律返回 404。** 当 `tenant_id` 与资源不匹配，或调用者不是该租户成员时，统一返回 404 `INVITATION_NOT_FOUND`，不区分“无权限（403）”与“不存在（404）”。实现上，service 每个入口先 `_require_tenant_member`，失败即抛 `INVITATION_NOT_FOUND`。
2. **所有 repository 邀请查询强制带 `tenant_id`。** 唯一例外是接受邀请时按 token 哈希查询（此时还不知道租户），但随后由 service 校验成员关系与邮箱一致性。该约束由架构测试静态校验（`test_repository_invitation_queries_carry_tenant_id`）与 import-linter 分层契约共同守护。
3. **token 只存 SHA-256 哈希。** 明文 token 用 `secrets.token_urlsafe(32)` 生成，仅在创建响应返回一次，从不落库；查询用哈希比对，使“token 是否存在”不改变数据库查询路径（抗时序侧信道）。

## 为什么 404 优于 403

403 对调用者说“这东西存在，但你不能看”；404 说“没有这东西”。对**跨租户**场景，前者会把“资源存在”这一信息泄露给无权者。统一 404 把“无权”与“不存在”压成同一个不可区分的响应，攻击者无法据此枚举他租户的资源。代价是：合法用户偶尔会把“自己确实无权”误读为“资源不存在”——在多租户安全语境下，这个可用性代价是可接受的、也是业界常见取舍（如 GitHub 对私有仓库返回 404）。

## 后果（Consequences）

- 正面：资源存在性与凭证两类泄露被结构性堵死；隔离规则由机械门禁（架构测试 + import-linter）持续守护，而非靠约定。
- 负面：404 会掩盖部分“本可提示无权”的场景，调试时需结合服务端日志区分“真不存在”与“跨租户命中”。
- 关联：错误码/状态映射见 `contracts/openapi.yaml` 与 `app/api/invitations.py::_CODE_TO_STATUS`；威胁模型见 `.kiro/specs/invitations/design.md` 第 5 节。
