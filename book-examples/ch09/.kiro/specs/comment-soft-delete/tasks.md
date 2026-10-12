# Tasks: 评论软删除

- [ ] 1. 数据库迁移：给 comments 加 deleted_at、deleted_by 两列
  - _需求: R1.1_
- [ ] 2. 软删除逻辑：DELETE /comments/{id} 设置 deleted_at/deleted_by
  - _需求: R1.1, R3.1_
- [ ] 3. 权限校验：非作者非管理员返回 403
  - _需求: R1.3_
- [ ] 4. 普通列表过滤：GET /cards/{id}/comments 排除 deleted_at 非空的行
  - _需求: R1.2_
- [ ] 5. 审计视图：GET /admin/comments 返回含 deleted_at/deleted_by 的完整列表
  - _需求: R2.1_
- [ ] 6. 字段脱敏：非管理员响应中不含 deleted_by
  - _需求: R2.2_
- [ ] 7. 幂等测试：对已删除评论二次删除返回 200 且不改变 deleted_at
  - _需求: R3.1_
