---
inclusion: fileMatch
fileMatchPattern: "backend/app/api/**"
---

# 后端 API 约定（仅在改 backend/app/api/** 时加载）

本文件是 Kiro Steering 的按文件触发规范：只有改到 API 层代码时才加载，
避免无关上下文（渐进式披露，见第 9 章）。与 AGENTS.md、contracts/openapi.yaml 为同一事实源。

## 错误响应

- 一律用统一错误信封：`{"error": {"code": "...", "message": "..."}}`（见 openapi.yaml 的 ErrorEnvelope）。
- `code` 取 openapi.yaml 枚举值，不得自造；`message` 面向调用方，可读但不泄露内部细节。

## 多租户与安全

- 跨租户访问（tenant_id 不匹配，或调用者非该租户成员）一律返回 404，不得返回 403，不得泄露资源是否存在（REQ-INV-010）。
- 邀请 token 用 secrets.token_urlsafe(32) 生成，只存 SHA-256 哈希；明文 token 只在创建响应里返回一次，从不落库（REQ-INV-005）。

## 分层边界

- API 路由只调用 service 层，严禁直接 import 或调用 repositories / db.models（由 import-linter 强制）。
- 所有数据查询必须带 tenant_id，裸写跨租户查询属违规。

## 状态码口径

- 创建成功 201；列表/撤销/接受成功 200；输入冲突 409；过期 410；无权限/找不到 404。
