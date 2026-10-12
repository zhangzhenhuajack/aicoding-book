#!/usr/bin/env bash
# trace.sh：变更追溯——双向查
#   trace.sh req  <REQ-ID>        正向：一个需求关联了哪些 commit
#   trace.sh line <file> <lineno> 反向：某行代码由哪个 commit 引入、关联哪个需求
set -euo pipefail
mode="${1:-}"
case "$mode" in
  req)
    reqid="$2"
    echo "需求 $reqid 关联的提交："
    git log --grep="$reqid" --pretty=format:'  %h  %s' --
    echo
    ;;
  line)
    file="$2"; lineno="$3"
    sha=$(git blame -L "${lineno},${lineno}" --porcelain -- "$file" | head -n1 | awk '{print $1}')
    echo "文件 $file 第 $lineno 行："
    echo "  引入提交：$(git log -1 --pretty='%h %s' "$sha")"
    reqid=$(git log -1 --pretty=%B "$sha" | grep -Eo '(TP|REQ)-[0-9]+' | head -n1 || true)
    if [ -n "$reqid" ]; then
      echo "  关联需求：$reqid"
      echo "  追溯链：$reqid → commit $(git rev-parse --short "$sha") → （PR/部署见 CI 元数据）"
    else
      echo "  ⚠ 该提交未关联需求编号——追溯链在此断裂"
    fi
    ;;
  *) echo "用法：trace.sh req <REQ-ID> | trace.sh line <file> <lineno>"; exit 2;;
esac
