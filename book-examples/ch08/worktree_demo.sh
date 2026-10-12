#!/usr/bin/env bash
set -e
git init -q demo-repo && cd demo-repo
git config user.email demo@book.local; git config user.name "Book Demo"

mkdir -p ops tests && touch ops/__init__.py
printf 'def add(a, b):\n    return a + b\n' > ops/add.py
cat > tests/test_add.py <<'PY'
import unittest
from ops.add import add
class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
PY
cat > AGENTS.md <<'MD'
# AGENTS.md —— 给代理的操作地图
## 测试命令
python3 -m unittest discover -s tests -q
## 约束
- 每个任务只新增自己的模块文件（ops/<name>.py）与对应测试，不改他人文件
MD
git add -A && git commit -qm "init: ops.add + 契约测试 + AGENTS.md"

# 为两个并行任务各建一个 worktree：独立工作树 + 独立分支，共享同一个 .git
git worktree add -q -b task/sub ../wt-sub
git worktree add -q -b task/mul ../wt-mul
git worktree list

# 任务A @ wt-sub：只新增 ops/sub.py
cd ../wt-sub
printf 'def subtract(a, b):\n    return a - b\n' > ops/sub.py
printf 'import unittest\nfrom ops.sub import subtract\nclass T(unittest.TestCase):\n    def test(self): self.assertEqual(subtract(5,3),2)\n' > tests/test_sub.py
git add -A && git commit -qm "feat: ops.subtract"
python3 -m unittest discover -s tests -q      # 自测

# 任务B @ wt-mul：只新增 ops/mul.py（与任务A完全隔离）
cd ../wt-mul
printf 'def multiply(a, b):\n    return a * b\n' > ops/mul.py
printf 'import unittest\nfrom ops.mul import multiply\nclass T(unittest.TestCase):\n    def test(self): self.assertEqual(multiply(4,3),12)\n' > tests/test_mul.py
git add -A && git commit -qm "feat: ops.multiply"
python3 -m unittest discover -s tests -q      # 自测

# 隔离性验证：主检出自始至终只有 add.py
cd ../demo-repo
ls ops                                        # 预期：__init__.py add.py（未被污染）

# 集成：按顺序合并两个分支（写入集中到合并点，串行解决）
git merge --no-edit -q task/sub
git merge --no-edit -q task/mul
python3 -m unittest discover -s tests -v      # 一次性跑全部测试
