from dataclasses import dataclass, field

# ---------- 验证器：对候选代码做断言式检查，返回 (通过?, 失败清单) ----------
def verify(impl: dict) -> tuple[bool, list[str]]:
    """验证器 = 一组断言。检查 parse_duration 实现应满足的契约。"""
    failures: list[str] = []
    cases = [("10s", 10), ("2m", 120), ("1h", 3600), ("0s", 0)]
    fn = impl.get("fn")
    if fn is None:
        return False, ["未提供实现 fn"]
    for text, expected in cases:
        try:
            got = fn(text)
        except Exception as e:
            failures.append(f"parse_duration({text!r}) 抛异常 {type(e).__name__}")
            continue
        if got != expected:
            failures.append(f"parse_duration({text!r})={got!r}，期望 {expected!r}")
    return (not failures), failures

# ---------- "模型"桩：按回合逐步修正，模拟真实循环的几种形态 ----------
def make_model():
    state = {"round": 0}
    def parse_v1(_):            return 0                       # 全错
    def parse_v2(text):                                        # 修了秒
        return int(text[:-1]) if text.endswith("s") else 0
    def parse_v3(text):                                        # 全部正确
        n = int(text[:-1]); return {"s":1,"m":60,"h":3600}[text[-1]] * n
    seq = [parse_v1, parse_v2, parse_v3]
    def generate(feedback):
        i = min(state["round"], len(seq) - 1)
        state["round"] += 1
        return {"fn": seq[i], "note": f"第{state['round']}轮，收到{len(feedback)}条反馈"}
    return generate

# ---------- 循环引擎：目标 / 执行 / 验证 / 终止条件 ----------
@dataclass
class LoopResult:
    status: str; rounds: int; history: list = field(default_factory=list)

MAX_ROUNDS = 8          # 预算停：硬上限
NO_PROGRESS_LIMIT = 3   # 失败停：连续多少轮不下降就认输

def run_loop(generate, verify_fn):
    feedback, history, stale = [], [], 0
    for rnd in range(1, MAX_ROUNDS + 1):
        impl = generate(feedback)                 # 执行
        ok, failures = verify_fn(impl)            # 验证
        history.append(len(failures))
        print(f"[轮 {rnd}] 失败 {len(failures)} 条  {impl['note']}")
        for f in failures:
            print(f"         · {f}")
        if ok:                                    # 成功停
            return LoopResult("success", rnd, history)
        if len(history) >= 2 and history[-1] > history[-2]:   # 目标偏移检测
            print("         ⚠ 目标偏移：失败数不降反升，停止")
            return LoopResult("fail_drift", rnd, history)
        stale = stale + 1 if len(history) >= 2 and history[-1] >= history[-2] else 0
        if stale >= NO_PROGRESS_LIMIT:            # 无进展检测
            print(f"         ⚠ 无进展：连续 {NO_PROGRESS_LIMIT} 轮未下降，认输")
            return LoopResult("fail_no_progress", rnd, history)
        feedback = failures                        # 纠正回灌
    return LoopResult("budget", MAX_ROUNDS, history)   # 预算停

if __name__ == "__main__":
    print("=== 场景 A：循环能收敛（成功停）===")
    print(run_loop(make_model(), verify))
    print("=== 场景 B：验证器永不满足（无进展 → 失败停）===")
    def bad_verify(impl):
        return False, ["永远红：验证器要求一个不可能达成的条件"]
    print(run_loop(make_model(), bad_verify))
