def in_range(x, lo, hi):
    # 修复一：空区间语义显式表达——lo>hi 直接返回 False。
    if lo > hi:
        return False
    # 修复二：闭区间——边界值 x==lo 或 x==hi 都算在内。
    return lo <= x <= hi
