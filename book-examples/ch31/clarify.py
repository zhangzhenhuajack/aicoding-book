#!/usr/bin/env python3
"""clarify.py：把一次任务澄清的结果结构化，并机械校验它是否"可验收"。

真实用法是把 PROMPT 发给编码助手，让它产出 answers 里这样的结构；
这里用固定数据演示"一条合格的澄清结果长什么样"以及如何自动校验它。
"""

PROMPT = """你是我的结对工程师。我给你一个需求，你先不要写任何代码。
请只做一件事：把它澄清成一个"可验收的任务描述"，输出下面五个字段：
1. 目标：这个需求真正要解决的问题（不是我提的解法）
2. 范围：这次做什么
3. 不做：这次明确不做什么
4. 验收依据：如何机械判定完成（命令/测试/可观测指标，不要用"写好"这种词）
5. 待我确认的假设：你为了填上面四项所做的、需要我拍板的假设
如果信息不足以填满这五项，先向我提问，不要猜。"""

# 模糊需求：
VAGUE = "给用户加个通知功能"

# 一条合格的澄清结果（真实场景由 AI 产出，这里固定下来便于校验）
answers = {
    "目标": "用户错过了与自己相关的重要状态变化（任务被指派、评论被回复），"
            "导致响应变慢；要解决的是'及时知道',而不一定是'收到推送'",
    "范围": "站内通知中心：被指派任务、评论被回复两类事件入库并在页面红点展示",
    "不做": "暂不做邮件/短信/App 推送；不做通知偏好设置；不做历史全量回填",
    "验收依据": [
        "pytest tests/notify -q 全部通过",
        "触发一次'指派'事件后 GET /api/notifications 返回条数 +1",
        "已读后红点数归零（前端 e2e: notifications.spec.ts 通过)",
    ],
    "待确认假设": [
        "只覆盖两类事件（指派/回复），其余事件本期不接入",
        "通知只做站内，渠道扩展留到下一期",
    ],
}


def validate(a: dict) -> list:
    """机械校验：五个字段齐全、验收依据可执行、留了待确认假设。"""
    problems = []
    for k in ("目标", "范围", "不做", "验收依据", "待确认假设"):
        if not a.get(k):
            problems.append(f"缺字段：{k}")
    acc = a.get("验收依据") or []
    if not isinstance(acc, list) or len(acc) == 0:
        problems.append("验收依据必须是可执行的列表（命令/测试）")
    for item in acc:
        if any(w in item for w in ("写好", "完善", "优化一下", "差不多")):
            problems.append(f"验收依据不可机械判定：{item!r}")
    if not a.get("待确认假设"):
        problems.append("没有列出待确认假设——AI 可能在偷偷替你拍板")
    return problems


if __name__ == "__main__":
    print("模糊需求：", VAGUE)
    print("-" * 48)
    for k, v in answers.items():
        if isinstance(v, list):
            print(f"{k}：")
            for it in v:
                print(f"    - {it}")
        else:
            print(f"{k}：{v}")
    print("-" * 48)
    problems = validate(answers)
    if problems:
        print("澄清不合格，需继续追问：")
        for p in problems:
            print("  !", p)
    else:
        print("澄清合格：这是一条可委派、可验收的任务描述。")
