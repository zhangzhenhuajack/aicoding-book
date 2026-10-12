def in_range(x, lo, hi):
    # “看起来对”的实现：遗漏了闭区间语义，
    # 用严格小于，边界值被错误地判为不在区间内。
    return lo < x < hi


def demo_counterexamples():
    cases = [
        # (x, lo, hi, 期望, 说明)
        (1, 1, 5, True,  "边界下界：x 等于 lo 应算在区间内"),
        (5, 1, 5, True,  "边界上界：x 等于 hi 应算在区间内"),
        (3, 5, 1, False, "空区间：lo>hi 时任何 x 都不该在内"),
        (3, 1, 5, True,  "普通内部值：正常情况必须仍然对"),
    ]
    results = []
    for x, lo, hi, expected, note in cases:
        got = in_range(x, lo, hi)
        results.append((x, lo, hi, expected, got, expected == got, note))
    return results


if __name__ == "__main__":
    print(f"{'x':>3} {'lo':>3} {'hi':>3} | {'期望':>5} {'实际':>5} {'通过':>4}  说明")
    for x, lo, hi, exp, got, ok, note in demo_counterexamples():
        flag = "OK" if ok else "FAIL"
        print(f"{x:>3} {lo:>3} {hi:>3} | {str(exp):>5} {str(got):>5} {flag:>4}  {note}")
