#!/usr/bin/env python3
"""lint 规则形态：检查 domain 层是否 import 了框架。"""
import ast
import sys
from pathlib import Path

BANNED = ("fastapi", "sqlalchemy", "app.db", "app.api")


def offending_imports(tree):
    hits = []
    banned_tops = {b.split(".")[0] for b in BANNED}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in banned_tops:
                    hits.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod.split(".")[0] in banned_tops:
                hits.append((node.lineno, mod))
    return hits


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    violations = 0
    for py in sorted(root.rglob("*.py")):
        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        for lineno, name in offending_imports(tree):
            print(f"{py}:{lineno}: TP001 domain 层禁止 import 框架 '{name}'")
            violations += 1
    if violations:
        print(f"\n发现 {violations} 处违规。domain 必须保持纯净（无框架依赖）。")
        return 1
    print("domain 层干净：未发现框架 import。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
