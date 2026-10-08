"""架构结构测试：静态校验分层边界与多租户查询纪律。

这些测试与 import-linter 互补——import-linter 查模块级依赖方向，这里用 AST/源码扫描
查更细的约定（如 repository 的每个邀请查询是否带 tenant_id）。
"""

from __future__ import annotations

import ast
from pathlib import Path

APP = Path(__file__).resolve().parents[1].parent / "app"


def _module_source(rel: str) -> str:
    return (APP / rel).read_text(encoding="utf-8")


def test_domain_imports_no_framework() -> None:
    """domain 层不得 import fastapi / sqlalchemy / app.db / app.api。"""
    src = _module_source("domain/invitation.py")
    tree = ast.parse(src)
    banned = {"fastapi", "sqlalchemy", "app.db", "app.api"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in {"fastapi", "sqlalchemy"}
        elif isinstance(node, ast.ImportFrom) and node.module:
            assert not any(node.module == b or node.module.startswith(b + ".") for b in banned)


def test_api_does_not_import_repositories_or_models() -> None:
    """api 层不得直接 import app.repositories 或 app.db.models。"""
    for py in (APP / "api").glob("*.py"):
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith("app.repositories"), py.name
                assert node.module != "app.db.models", py.name


def test_repository_invitation_queries_carry_tenant_id() -> None:
    """InvitationRepository 中按租户查询的方法必须引用 tenant_id。

    例外：get_by_token_hash 按哈希查询（接受邀请时还不知道租户），由 service 做成员校验。
    """
    src = _module_source("repositories/invitation_repo.py")
    tree = ast.parse(src)
    repo = next(
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.ClassDef) and n.name == "InvitationRepository"
    )
    exempt = {"__init__", "add", "get_by_token_hash"}
    for fn in [n for n in repo.body if isinstance(n, ast.FunctionDef)]:
        if fn.name in exempt:
            continue
        fn_src = ast.get_source_segment(src, fn) or ""
        assert "tenant_id" in fn_src, f"{fn.name} 缺少 tenant_id 过滤"


def test_no_star_imports() -> None:
    """禁止星号导入（AGENTS.md 风格约定）。"""
    for py in APP.rglob("*.py"):
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert not any(a.name == "*" for a in node.names), str(py)
