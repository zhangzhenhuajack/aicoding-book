#!/usr/bin/env bash
# pr_size_check.sh：统计一个变更范围的非机械改动行数，超阈值报警
# 用法：pr_size_check.sh <base> <head>
BASE="${1:-HEAD~1}"; HEAD="${2:-HEAD}"
WARN=500; HARD=800
# 机械变更：锁文件、生成文件、快照——评审成本低，排除在阈值外
IGNORE=(':(exclude)*.lock' ':(exclude)*.snap' ':(exclude)*_pb2.py' ':(exclude)dist/*')
total=0
while read -r add del path; do
  [ "$add" = "-" ] && continue          # 二进制文件跳过
  total=$((total + add + del))
done < <(git diff --numstat "$BASE" "$HEAD" -- . "${IGNORE[@]}")
echo "变更范围 $BASE..$HEAD 非机械改动行数：$total（warn=$WARN hard=$HARD）"
if [ "$total" -gt "$HARD" ]; then
  echo "✗ 超过硬上限 $HARD 行：请拆成可独立评审的阶段，或在 PR 描述显式说明为何不可拆"
  exit 1
elif [ "$total" -gt "$WARN" ]; then
  echo "⚠ 超过软上限 $WARN 行：复杂逻辑建议进一步拆分"
  exit 0
else
  echo "✓ 落在人类评审带宽内"
  exit 0
fi
