import os
import pytest

# 用环境变量切换被测实现：默认测 buggy 版，IMPL=fixed 测修复版
if os.environ.get("IMPL") == "fixed":
    from in_range_fixed import in_range
else:
    from counterexample import in_range


@pytest.mark.parametrize("x,lo,hi,expected", [
    (1, 1, 5, True),    # 下界（反例：buggy 版会错）
    (5, 1, 5, True),    # 上界（反例：buggy 版会错）
    (3, 5, 1, False),   # 空区间
    (3, 1, 5, True),    # 内部值（守住正常情况）
])
def test_in_range(x, lo, hi, expected):
    assert in_range(x, lo, hi) == expected
