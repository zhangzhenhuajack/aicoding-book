from dataclasses import dataclass, field
import re

# ---- 约束：工具白名单 + 禁改路径 ----
ALLOWED_TOOLS = {"read", "write", "run_tests"}
PROTECTED = ("tests/",)  # 这些路径下的文件，agent 不许改

class HarnessError(Exception):
    """被缰绳拦下时抛出。"""

@dataclass
class Workspace:
    files: dict = field(default_factory=dict)
    history: list = field(default_factory=list)  # 状态保存：每步都记下来

    def write(self, path, content):
        if path.startswith(PROTECTED):                 # 约束
            raise HarnessError(f"拒绝写入受保护路径：{path}")
        self.files[path] = content

    def run_tests(self):
        """假的验收：src/add.py 里必须有正确实现的 add(a,b)。"""
        code = self.files.get("src/add.py", "")
        m = re.search(r"return\s+a\s*([+\-*])\s*b", code)
        if not m:
            return False, "FAIL: 没找到 return a <op> b 形式的实现"
        if m.group(1) != "+":
            return False, f"FAIL: add 用了 '{m.group(1)}'，add(2,3)==5 不通过"
        return True, "PASS: 1 passed（add(2,3)==5）"

def run(model, ws, max_steps=20, loop_threshold=3):
    # ---- 告知：启动时把环境映射一次性喂给模型 ----
    print("[告知] 工具=%s；受保护=%s" % (sorted(ALLOWED_TOOLS), PROTECTED))
    repeat = {}                                        # 循环检测计数
    obs = "实现 src/add.py 使 add(2,3)==5。不要修改 tests/。"
    for step in range(1, max_steps + 1):
        action = model.next_action(obs)
        tool = action.get("tool", "")
        ws.history.append(f"step{step}:{tool}")        # 状态保存

        if tool not in ALLOWED_TOOLS and tool != "finish":   # 约束
            obs = f"[约束] 工具 '{tool}' 不在白名单，已拒绝"
            print(f"步 {step}: {obs}"); continue

        if tool == "finish":                           # 验证：退出前强制核对
            ok, msg = ws.run_tests()
            print(f"步 {step}: [验证] 退出前强制核对 -> {msg}")
            if ok:
                print(f"✅ 完成，共 {step} 步"); return True
            obs = f"[纠正] 验证未通过：{msg}。继续修。"
            print(f"步 {step}: {obs}"); continue

        if tool == "write":
            try:
                ws.write(action["path"], action["content"])
            except HarnessError as e:
                obs = f"[约束] {e}"; print(f"步 {step}: {obs}"); continue
            key = (action["path"], action["content"])  # 纠正：循环检测
            repeat[key] = repeat.get(key, 0) + 1
            if repeat[key] >= loop_threshold:
                obs = f"[纠正] doom loop：相同内容已提交 {repeat[key]} 次，换个思路！"
                print(f"步 {step}: {obs}"); continue
            ok, msg = ws.run_tests()                   # 验证：失败回灌
            obs = f"写入 {action['path']}；验证：{msg}"
            print(f"步 {step}: {obs}")
    print("⛔ 到达最大步数（终止条件兜底）"); return False
