"""架构适应度函数集：用标准库 ast 守住三条可自动验证的架构特征。
用法：python3 fitness.py <包目录>
返回码非 0 表示有适应度函数失败（可直接用于 CI 门禁）。
"""
import ast
import sys
from pathlib import Path

# ---- 阈值（团队按项目调；这是"把架构判断写成数字"的地方）----
MAX_COMPLEXITY = 10      # 单函数圈复杂度上限
MAX_MODULE_LOC = 150     # 单模块非空行数上限（规模漂移）


def iter_modules(pkg: Path):
    for py in sorted(pkg.rglob("*.py")):
        src = py.read_text(encoding="utf-8")
        yield py, ast.parse(src), src


# ---- 适应度函数 1：模块循环依赖 ----
def build_import_graph(pkg: Path):
    graph = {}
    for py, tree, _ in iter_modules(pkg):
        deps = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                parts = node.module.split(".")
                # 只关心包内依赖：from app import billing
                if parts[0] == pkg.name and len(parts) > 1:
                    deps.add(parts[1])
                if parts[0] == pkg.name and len(parts) == 1:
                    for alias in node.names:
                        deps.add(alias.name)
        graph[py.stem] = deps
    return graph


def find_cycles(graph):
    cycles, WHITE, GRAY, BLACK = [], 0, 1, 2
    color = {n: WHITE for n in graph}

    def dfs(node, stack):
        color[node] = GRAY
        stack.append(node)
        for nxt in graph.get(node, ()):
            if nxt not in graph:
                continue
            if color[nxt] == GRAY:            # 遇到灰节点 → 成环
                i = stack.index(nxt)
                cycles.append(stack[i:] + [nxt])
            elif color[nxt] == WHITE:
                dfs(nxt, stack)
        stack.pop()
        color[node] = BLACK

    for n in graph:
        if color[n] == WHITE:
            dfs(n, [])
    return cycles


# ---- 适应度函数 2：圈复杂度（McCabe，用 ast 近似）----
class ComplexityVisitor(ast.NodeVisitor):
    """圈复杂度 = 1 + 决策点数。"""

    def __init__(self):
        self.score = 1

    def visit_If(self, n): self.score += 1; self.generic_visit(n)
    def visit_For(self, n): self.score += 1; self.generic_visit(n)
    def visit_While(self, n): self.score += 1; self.generic_visit(n)
    def visit_ExceptHandler(self, n): self.score += 1; self.generic_visit(n)
    def visit_BoolOp(self, n): self.score += len(n.values) - 1; self.generic_visit(n)
    def visit_IfExp(self, n): self.score += 1; self.generic_visit(n)


def complexity_of(func_node):
    v = ComplexityVisitor()
    for child in func_node.body:
        v.visit(child)
    return v.score


# ---- 主流程 ----
def main(pkg_path):
    pkg = Path(pkg_path)
    failures = []

    # FF1 循环依赖
    for cyc in find_cycles(build_import_graph(pkg)):
        failures.append(f"[循环依赖] {' -> '.join(cyc)}")

    # FF2 圈复杂度 + FF3 模块规模
    graph_size = 0
    for py, tree, src in iter_modules(pkg):
        graph_size += 1
        loc = len([ln for ln in src.splitlines() if ln.strip()])
        if loc > MAX_MODULE_LOC:
            failures.append(f"[规模漂移] {py.name}: {loc} 行 > 上限 {MAX_MODULE_LOC}")
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                c = complexity_of(node)
                if c > MAX_COMPLEXITY:
                    failures.append(
                        f"[圈复杂度] {py.name}:{node.lineno} {node.name}() = {c} > 上限 {MAX_COMPLEXITY}")

    print(f"扫描包 '{pkg.name}'：{graph_size} 个模块\n")
    if failures:
        print(f"适应度函数失败 {len(failures)} 项：")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print("✓ 所有适应度函数通过")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "app"))
