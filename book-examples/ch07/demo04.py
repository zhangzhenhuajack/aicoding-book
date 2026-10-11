#!/usr/bin/env python3
"""Claude Code PreToolUse hook：拦截危险命令、保护 tests/ 目录。本书示例，核验 2026-10。

Claude Code 每次工具调用前，把一段 JSON 从 stdin 传入：
  Bash： {"tool_name":"Bash","tool_input":{"command":"..."}}
  Edit： {"tool_name":"Edit","tool_input":{"file_path":"/abs/path", ...}}
拦截 → 打印 permissionDecision=deny（exit 0）；放行 → exit 0 且不打印（不表态）。
"""
import json
import re
import sys

DANGER_PATTERNS = [
    (r"\brm\s+-rf?\b", "递归强删"),
    (r":\(\)\s*\{.*\}\s*;", "fork 炸弹"),
    (r"\bgit\s+push\b.*\s--force\b", "强制推送"),
    (r"\bchmod\s+-R\s+777\b", "递归 777 授权"),
]
PROTECTED_DIRS = ("/tests/", "/test/")
WRITE_TOOLS = ("Edit", "Write", "NotebookEdit", "MultiEdit")

def deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}, ensure_ascii=False))
    sys.exit(0)

def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # 读不到合法 JSON：不表态
    tool = data.get("tool_name", "")
    ti = data.get("tool_input", {}) or {}

    if tool in ("Bash", "PowerShell"):
        cmd = ti.get("command", "")
        for pat, desc in DANGER_PATTERNS:
            if re.search(pat, cmd):
                deny(f"危险命令被 hook 拦截：{desc}。命令：{cmd}")

    if tool in WRITE_TOOLS:
        # 官方保证 file_path 恒为绝对路径；统一斜杠以兼容 Windows
        fp = (ti.get("file_path", "") or "").replace("\\", "/")
        if any(seg in "/" + fp for seg in PROTECTED_DIRS):  # 前补 "/"，相对路径 tests/x.py 也能命中
            deny(f"tests/ 目录受保护，禁止 AI 直接改测试：{fp}")

    sys.exit(0)  # 其余放行（不打印 = 不表态，交回正常权限流程）

if __name__ == "__main__":
    main()
