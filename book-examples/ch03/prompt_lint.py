#!/usr/bin/env python3
"""提示词结构检查器 prompt_lint —— 本书示例。"""
import re
import sys

# 四要素各自的触发词（命中任一即认为该要素"存在"）
ELEMENTS = {
    "目标": ["目标", "请", "帮我", "你要", "任务是", "实现", "完成", "生成", "写一个", "goal", "task"],
    "约束": ["约束", "不得", "不要", "必须", "禁止", "限制", "只能", "最多", "不超过", "constraint", "must", "only"],
    "示例": ["示例", "例如", "比如", "样例", "输入输出", "input", "output", "example", "<example", "e.g."],
    "输出格式": ["输出格式", "格式", "返回", "以 json", "用表格", "markdown", "纯文本", "字段", "schema", "format"],
}

# 常见互斥指令对（两侧都命中 -> 疑似矛盾）
CONFLICTS = [
    (["简洁", "精简", "简短", "一句话", "concise", "brief"],
     ["详细", "详尽", "展开", "逐步解释", "面面俱到", "detailed", "exhaustive"]),
    (["改动最小", "最小改动", "只改", "minimal"],
     ["顺手重构", "重构", "优化整体", "全面整理", "refactor"]),
    (["严格遵守", "严格按", "不得偏离", "strict"],
     ["灵活", "自由发挥", "随意", "酌情", "flexible"]),
    (["尽快", "越快越好", "立刻", "fast"],
     ["覆盖所有", "考虑所有", "穷尽", "exhaustive", "cover all"]),
]


def find_hits(text, words):
    return [w for w in words if w.lower() in text.lower()]


def lint(prompt: str) -> dict:
    report = {"elements": {}, "conflicts": [], "score": 0}
    for name, words in ELEMENTS.items():
        hits = find_hits(prompt, words)
        report["elements"][name] = hits
        if hits:
            report["score"] += 1
    for left, right in CONFLICTS:
        lh, rh = find_hits(prompt, left), find_hits(prompt, right)
        if lh and rh:
            report["conflicts"].append((lh[0], rh[0]))
    return report


def render(prompt: str, report: dict) -> str:
    lines = ["=" * 48, f"提示词长度：{len(prompt)} 字符", "-" * 48, "四要素检查："]
    for name in ELEMENTS:
        hits = report["elements"][name]
        mark = "✓" if hits else "✗"
        detail = f"命中 {hits[:3]}" if hits else "缺失"
        lines.append(f"  [{mark}] {name:<6}  {detail}")
    lines.append("-" * 48)
    if report["conflicts"]:
        lines.append(f"⚠ 疑似矛盾指令 {len(report['conflicts'])} 处：")
        for a, b in report["conflicts"]:
            lines.append(f"    “{a}” ↔ “{b}” 可能互斥，请明确优先级")
    else:
        lines.append("✓ 未发现明显矛盾指令")
    lines.append("-" * 48)
    verdict = "可以发送" if report["score"] == 4 and not report["conflicts"] else "建议修改"
    lines.append(f"结构完整度：{report['score']}/4   结论：{verdict}")
    lines.append("=" * 48)
    return "\n".join(lines)


SAMPLE_GOOD = """你是 TeamPulse 后端开发者。请实现 POST /invitations 接口：
约束：不得修改 tests/ 下已有断言；只允许改动 app/invitations/ 目录。
示例：输入 {"email":"a@b.com"} 应返回 201 和 {"id":"inv_x","status":"pending"}。
输出格式：返回 JSON，字段含 id、status、expires_at。验收：pytest tests/contract -q 全部通过。"""

SAMPLE_BAD = """帮我把邀请功能写完，要尽量简洁，但也要详尽覆盖所有边界情况并逐步解释每一步。
严格按规范来，同时灵活一点随意发挥。"""


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "-":
        prompt = sys.stdin.read()
        print(render(prompt, lint(prompt)))
        return
    for title, p in [("【好提示词】", SAMPLE_GOOD), ("【差提示词】", SAMPLE_BAD)]:
        print(title)
        print(render(p, lint(p)))
        print()


if __name__ == "__main__":
    main()
