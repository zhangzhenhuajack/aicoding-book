#!/usr/bin/env python3
"""资产过期检查器：扫描 steering / Skills 引用的文件和命令是否还存在。"""
import os
import re
import shutil
import sys
from pathlib import Path

SHELL_BUILTINS = {"cd", "echo", "export", "set", "source", ".", "exit",
                  "true", "false", "test", "[", ":"}  # 省略部分
INLINE_PATH = re.compile(r"`([\w./-]+\.[\w]+)`")   # 反引号里带扩展名的路径
BASH_BLOCK = re.compile(r"```bash\n(.*?)```", re.S)  # bash 代码块


def _resolvable(cmd, extra_bins):
    """命令能否解析：先查系统 PATH，再查项目 venv 的 bin。"""
    if shutil.which(cmd) is not None:
        return True
    return any((b / cmd).exists() for b in extra_bins)


def check_asset(md, repo_root, extra_bins):
    text = md.read_text(encoding="utf-8")
    problems = []
    for rel in set(INLINE_PATH.findall(text)):
        if rel.startswith(("http", "www")):
            continue
        if not any((p / rel).exists() for p in (md.parent, repo_root)):
            problems.append(("DEAD-FILE", rel))
    for block in BASH_BLOCK.findall(text):
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            cmd = line.split()[0]
            if cmd in SHELL_BUILTINS or "=" in cmd or cmd.startswith(("$", "./", "/")):
                continue
            if not _resolvable(cmd, extra_bins):
                problems.append(("DEAD-CMD", cmd))
    return problems


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    repo_root = root.parent
    extra_bins = [p for p in [repo_root / ".venv" / "bin",
                              repo_root / "backend" / ".venv" / "bin",
                              Path(os.environ.get("VIRTUAL_ENV", "")) / "bin"]
                  if p.exists()]
    total = 0
    for md in sorted(root.rglob("*.md")):
        for kind, ref in check_asset(md, repo_root, extra_bins):
            print(f"{md}: {kind} 引用 '{ref}' 已失效")
            total += 1
    if total:
        print(f"\n发现 {total} 处失效引用，这些资产可能已 Stale，需在回顾会第六问处置。")
        return 1
    print("所有资产引用均有效。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
