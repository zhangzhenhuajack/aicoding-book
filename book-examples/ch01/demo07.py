from unittest.mock import patch

RATES = {("USD", "CNY"): 7.2}

def get_rate(base, quote):          # 外部依赖（示意：平时从汇率服务取数）
    return RATES[(base, quote)]

def correct(base, quote, amount):
    return amount * get_rate(base, quote)

def mutant(base, quote, amount):
    # 注入 bug：正常路径上就把汇率静默当成 1.0，根本没去查真实汇率
    rate = 1.0
    return amount * rate

def fake_test(convert):
    # 造假：把真正承载逻辑的 get_rate 整个 mock 掉，再只断言"返回非空"
    with patch(f"{__name__}.get_rate", return_value=1.0):
        result = convert("USD", "CNY", 100)
    assert result is not None            # 弱断言：永远成立
    return

def strong_test(convert):
    # 真测：不碰核心依赖，直接断言具体数值
    result = convert("USD", "CNY", 100)
    assert result == 720.0, f"期望 720.0，实际 {result}"
    return

def run(test_name, test, impl):
    try:
        test(impl)
        print(f"[绿] {test_name:11s} 对 {impl.__name__+'()':9s} —— 通过")
    except AssertionError as e:
        print(f"[红] {test_name:11s} 对 {impl.__name__+'()':9s} —— 失败：{e}")

for impl in (correct, mutant):
    run("fake_test", fake_test, impl)
    run("strong_test", strong_test, impl)
