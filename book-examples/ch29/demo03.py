"""结构测试形态：同一条教训写成一个 pytest 断言。"""
import ast
from pathlib import Path

DOMAIN = Path(__file__).resolve().parent.parent / "domain"
BANNED_TOPS = {"fastapi", "sqlalchemy", "starlette"}


def _imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                yield a.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom):
            yield (node.module or "").split(".")[0]


def test_domain_has_no_framework_imports():
    offenders = {}
    for py in DOMAIN.rglob("*.py"):
        bad = BANNED_TOPS & set(_imports(py))
        if bad:
            offenders[py.name] = sorted(bad)
    assert not offenders, f"domain 层出现框架依赖：{offenders}"
