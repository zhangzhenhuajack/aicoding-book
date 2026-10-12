#!/usr/bin/env bash
# TeamPulse 灰度回滚脚本（示例）。
#
# 用途：把 ECS 服务回滚到上一个（或指定的）稳定 task definition。
# 这是部署出问题时的“快速止血”动作，不触碰数据库（破坏性迁移回滚另见 AGENTS.md 迁移护栏）。
#
# 用法：
#   ./scripts/rollback.sh <cluster> <service> [target-task-def-arn]
# 不传第三个参数时，回滚到该服务当前任务定义家族的上一个 revision。
#
# 需要：aws cli 已配置凭证（aws configure / aws sso login），有 ecs:UpdateService 等权限。

set -euo pipefail

CLUSTER="${1:?需要 cluster 名}"
SERVICE="${2:?需要 service 名}"
TARGET_TD="${3:-}"

echo "[rollback] cluster=$CLUSTER service=$SERVICE"

if [[ -z "$TARGET_TD" ]]; then
  # 取当前 task definition family，推算上一个 revision
  CURRENT_TD=$(aws ecs describe-services \
    --cluster "$CLUSTER" --services "$SERVICE" \
    --query 'services[0].taskDefinition' --output text)
  FAMILY="${CURRENT_TD##*/}"; FAMILY="${FAMILY%:*}"
  CURRENT_REV="${CURRENT_TD##*:}"
  PREV_REV=$((CURRENT_REV - 1))
  if (( PREV_REV < 1 )); then
    echo "[rollback] 没有可回滚的上一个 revision（当前已是 revision 1）" >&2
    exit 1
  fi
  TARGET_TD="${FAMILY}:${PREV_REV}"
  echo "[rollback] 当前=$CURRENT_TD，回滚目标=$TARGET_TD"
fi

read -r -p "确认把 $SERVICE 回滚到 $TARGET_TD ？[y/N] " ans
if [[ "${ans,,}" != "y" ]]; then
  echo "[rollback] 已取消"; exit 0
fi

# 幂等：重复执行同一回滚会把服务稳定在同一 task def，不会产生副作用。
aws ecs update-service \
  --cluster "$CLUSTER" --service "$SERVICE" \
  --task-definition "$TARGET_TD" \
  --force-new-deployment >/dev/null

echo "[rollback] 已触发回滚，等待服务稳定…"
aws ecs wait services-stable --cluster "$CLUSTER" --services "$SERVICE"
echo "[rollback] 完成：$SERVICE 现运行 $TARGET_TD"
