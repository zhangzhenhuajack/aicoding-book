# Requirements: 评论软删除（Comment Soft-Delete）

## 简介
TeamPulse 的看板卡片支持评论。本功能为评论增加「软删除」：删除后评论从普通视图消失，
但记录保留，管理员可在审计视图看到谁、何时删除了它。

## 需求

### 需求 1：作者删除自己的评论
**用户故事**：作为评论作者，我想删除自己的评论，以便移除写错的内容。

验收标准（EARS）：
- R1.1 WHEN 作者对自己的评论发起删除 THE SYSTEM SHALL 把该评论标记为 deleted（设置 deleted_at 时间戳）而不物理删除行。
- R1.2 WHEN 一条评论已被标记 deleted THE SYSTEM SHALL 在普通评论列表中不返回该评论。
- R1.3 IF 发起删除的用户不是该评论的作者且不是管理员 THEN THE SYSTEM SHALL 拒绝删除并返回 403。

### 需求 2：管理员审计视图
**用户故事**：作为管理员，我想看到被删除的评论及删除者，以便追责与合规审计。

验收标准（EARS）：
- R2.1 WHEN 管理员请求审计视图 THE SYSTEM SHALL 返回包含已删除评论的完整列表，含 deleted_at 与 deleted_by。
- R2.2 WHILE 用户不是管理员 THE SYSTEM SHALL 不在任何接口暴露 deleted_by 字段。

### 需求 3：防止重复删除
**用户故事**：作为系统，我要保证删除操作幂等，以便前端重试不出错。

验收标准（EARS）：
- R3.1 WHEN 对一条已 deleted 的评论再次发起删除 THE SYSTEM SHALL 返回 200 且不改变 deleted_at（幂等）。
