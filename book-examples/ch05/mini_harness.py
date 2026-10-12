#!/usr/bin/env python3
"""本书示例：最小 Harness（不调用真实 LLM）。

用一个"脚本化的假模型"回放一串预先写好的动作，来演示 Harness 的四要素：
  约束(constrain) 白名单工具 + 禁改路径
  告知(inform)   启动时把环境映射喂给"模型"
  验证(verify)   退出前强制跑验收脚本
  纠正(correct)  失败回灌 + 循环检测打断 doom loop

它不需要网络、不需要 API key，可直接 `python3 mini_harness.py` 跑通。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# 1) 约束：工具白名单 + 禁改路径
# ---------------------------------------------------------------------------
ALLOWED_TOOLS = {"read", "write", "run_tests"}
PROTECTED = ("tests/",)  # 这些路径下的文件，agent 不许改


class HarnessError(Exception):
    """被缰绳拦下时抛出。"""


# ---------------------------------------------------------------------------
# 2) 一个假的"工作区"：内存里的文件系统 + 一个假的验收脚本
# ---------------------------------------------------------------------------
@dataclass
class Workspace:
    files: dict[str, str] = field(default_factory=dict)
    history: list[str] = field(default_factory=list)  # 状态保存：每一步都记下来

    def read(self, path: str) -> str:
        return self.files.get(path, "")

    def write(self, path: str, content: str) -> None:
        # —— 约束：禁改保护路径 ——
        if path.startswith(PROTECTED):
            raise HarnessError(f"拒绝写入受保护路径：{path}")
        self.files[path] = content

    def run_tests(self) -> tuple[bool, str]:
        """假的验收：src/add.py 里必须有一个正确实现的 add(a, b)。"""
        code = self.files.get("src/add.py", "")
        m = re.search(r"return\s+a\s*([+\-*])\s*b", code)
        if not m:
            return False, "FAIL: 没找到 `return a <op> b` 形式的实现"
        if m.group(1) != "+":
            return False, f"FAIL: add 用了 '{m.group(1)}'，断言 add(2,3)==5 不通过"
        return True, "PASS: 1 passed（add(2,3)==5）"


# ---------------------------------------------------------------------------
# 3) 脚本化的"假模型"：按剧本吐动作，模拟一次会犯错、被纠正的真实轨迹
# ---------------------------------------------------------------------------
class ScriptedModel:
    """真实模型在这里会根据 prompt 生成动作；本 Demo 用固定剧本代替。"""

    def __init__(self) -> None:
        self._script = [
            # 第 1 步：先踩约束——想改测试文件（典型越界行为）
            {"tool": "write", "path": "tests/test_add.py", "content": "assert True"},
            # 第 2 步：写了个错的实现（用了减法）——会被验证拦下
            {"tool": "write", "path": "src/add.py", "content": "def add(a, b):\n    return a - b"},
            # 第 3-5 步：doom loop——反复提交同一个错误实现
            {"tool": "write", "path": "src/add.py", "content": "def add(a, b):\n    return a - b"},
            {"tool": "write", "path": "src/add.py", "content": "def add(a, b):\n    return a - b"},
            {"tool": "write", "path": "src/add.py", "content": "def add(a, b):\n    return a - b"},
            # 第 6 步：收到"换个思路"的纠正后，改对了
            {"tool": "write", "path": "src/add.py", "content": "def add(a, b):\n    return a + b"},
            # 第 7 步：宣布完成（触发退出前强制验证）
            {"tool": "finish"},
        ]
        self._i = 0

    def next_action(self, observation: str) -> dict:
        if self._i >= len(self._script):
            return {"tool": "finish"}
        action = self._script[self._i]
        self._i += 1
        return action


# ---------------------------------------------------------------------------
# 4) Harness 主循环：把四要素装进去
# ---------------------------------------------------------------------------
def run(model: ScriptedModel, ws: Workspace, max_steps: int = 20, loop_threshold: int = 3) -> bool:
    # —— 告知：启动时把环境映射一次性喂给模型（这里打印出来示意）——
    print("[告知] 环境映射：工具=%s；受保护路径=%s；验收=run_tests" % (sorted(ALLOWED_TOOLS), PROTECTED))

    # 循环检测：按"同一文件写入同样的内容"计数（反复提交同一错解才算 doom loop）
    repeat_counts: dict[tuple[str, str], int] = {}
    obs = "开始任务：实现 src/add.py 使 add(2,3)==5。不要修改 tests/。"

    for step in range(1, max_steps + 1):
        action = model.next_action(obs)
        tool = action.get("tool", "")
        ws.history.append(f"step{step}:{tool}")  # 状态保存

        # —— 约束：工具必须在白名单内 ——
        if tool not in ALLOWED_TOOLS and tool != "finish":
            obs = f"[约束] 工具 '{tool}' 不在白名单，已拒绝"
            print(f"步 {step}: {obs}")
            continue

        if tool == "finish":
            # —— 验证：退出前强制跑验收，不达标不许退出 ——
            ok, msg = ws.run_tests()
            print(f"步 {step}: [验证] 退出前强制核对 -> {msg}")
            if ok:
                print(f"✅ 任务完成，共 {step} 步。轨迹：{' > '.join(ws.history)}")
                return True
            obs = f"[纠正] 验证未通过：{msg}。继续修。"
            print(f"步 {step}: {obs}")
            continue

        if tool == "write":
            path, content = action["path"], action["content"]
            try:
                ws.write(path, content)
            except HarnessError as e:
                obs = f"[约束] {e}"
                print(f"步 {step}: {obs}")
                continue

            # —— 纠正：循环检测，反复提交"同一个错解"就打断 ——
            key = (path, content)
            repeat_counts[key] = repeat_counts.get(key, 0) + 1
            if repeat_counts[key] >= loop_threshold:
                obs = f"[纠正] 检测到 doom loop：对 {path} 提交了 {repeat_counts[key]} 次相同内容，强制提示：换个思路！"
                print(f"步 {step}: {obs}")
                continue

            # —— 验证：每次写完立刻跑一遍，把失败回灌给模型 ——
            ok, msg = ws.run_tests()
            obs = f"写入 {path}；验证：{msg}"
            print(f"步 {step}: {obs}")

    print("⛔ 到达最大步数仍未完成（终止条件兜底）")
    return False


if __name__ == "__main__":
    run(ScriptedModel(), Workspace())
