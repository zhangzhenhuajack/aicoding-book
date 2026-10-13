"""纯 Python AST 版结构测试：守住 api > service > repo 的分层方向。
不依赖任何第三方库，只用标准库 ast + pathlib。"""
import ast
from pathlib import Path

PKG = Path(__file__).resolve().parent / "shop"

# 层级从高到低：序号越小越靠上层。规则：只能依赖同层或更下层（序号 >= 自己）。
LAYERS = {"shop.api": 0, "shop.service": 1, "shop.repo": 2}


def _module_name(py: Path) -> str:
    rel = py.relative_to(PKG.parent).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _layer_of(mod: str):
    for layer, rank in LAYERS.items():
        if mod == layer or mod.startswith(layer + "."):
            return layer, rank
    return None, None


def _imports(py: Path):
    tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            yield node.module, node.lineno
        elif isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name, node.lineno


def test_no_upward_dependency():
    violations = []
    for py in PKG.rglob("*.py"):
        src_mod = _module_name(py)
        src_layer, src_rank = _layer_of(src_mod)
        if src_rank is None:
            continue
        for imported, lineno in _imports(py):
            dst_layer, dst_rank = _layer_of(imported)
            if dst_rank is None:
                continue  # 外部依赖，不管
            if dst_rank < src_rank:  # 导入了更上层 -> 违规
                violations.append(
                    f"{src_mod} (第{lineno}行) 非法依赖上层 {imported}: "
                    f"{src_layer} -> {dst_layer}"
                )
    assert not violations, "发现分层违规:\n" + "\n".join(violations)
