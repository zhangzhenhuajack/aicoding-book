"""Demo 34-1：Token 成本计算器（本书示例）

输入/输出/缓存读/缓存写分别计价。价格做成参数，默认值取自
Anthropic 官方 Prompt caching / Pricing 文档，核验于 2026-10-08：
  - 基础输入、输出：各模型价目（$/MTok）
  - 5 分钟缓存写入 = 1.25 × 基础输入价
  - 1 小时缓存写入 = 2 × 基础输入价
  - 缓存读取（命中/刷新）= 0.1 × 基础输入价（标准倍数；部分新模型更低，见文档脚注）
来源：https://docs.claude.com/en/docs/build-with-claude/prompt-caching
"""
from dataclasses import dataclass


@dataclass
class Price:
    """每百万 token（MTok）美元价。倍数遵循官方口径，核验 2026-10-08。"""
    input_per_mtok: float          # 基础输入价
    output_per_mtok: float         # 输出价（含思考 token）
    cache_write_mult_5m: float = 1.25   # 官方：5 分钟写入 1.25×
    cache_write_mult_1h: float = 2.0    # 官方：1 小时写入 2×
    cache_read_mult: float = 0.1        # 官方：读取 0.1×（标准）


# 默认价目：Claude Opus 4.5（$5/$25 每 MTok），仅作演示，使用前请以官方定价页为准
OPUS_45 = Price(input_per_mtok=5.0, output_per_mtok=25.0)


@dataclass
class Usage:
    """一次交互的 token 用量，对应官方 usage 字段口径：
    total_input = input + cache_creation + cache_read"""
    input_tokens: int = 0          # 未缓存输入（基础价）
    cache_write_tokens: int = 0    # 缓存写入（有溢价）
    cache_read_tokens: int = 0     # 缓存读取（0.1×）
    output_tokens: int = 0         # 普通输出 + 思考输出


def cost_usd(u: Usage, p: Price, ttl: str = "5m") -> dict:
    write_mult = p.cache_write_mult_5m if ttl == "5m" else p.cache_write_mult_1h
    per = 1_000_000
    c_input = u.input_tokens / per * p.input_per_mtok
    c_write = u.cache_write_tokens / per * p.input_per_mtok * write_mult
    c_read = u.cache_read_tokens / per * p.input_per_mtok * p.cache_read_mult
    c_output = u.output_tokens / per * p.output_per_mtok
    total = c_input + c_write + c_read + c_output
    return {
        "未缓存输入": round(c_input, 6),
        "缓存写入": round(c_write, 6),
        "缓存读取": round(c_read, 6),
        "输出(含思考)": round(c_output, 6),
        "合计": round(total, 6),
    }


def _fmt(d: dict) -> str:
    return "  ".join(f"{k}=${v}" for k, v in d.items())


if __name__ == "__main__":
    big_prefix = 100_000   # 一大段稳定上下文（系统提示+规则+文档）
    question = 500         # 每次变化的用户问题
    answer = 800           # 模型回答

    # 场景 A：不用缓存——每次都把大前缀按基础价重算
    a = Usage(input_tokens=big_prefix + question, output_tokens=answer)
    # 场景 B：正确用缓存——第 1 次写入前缀，之后每次 0.1× 读取
    b1 = Usage(cache_write_tokens=big_prefix, input_tokens=question, output_tokens=answer)
    b2 = Usage(cache_read_tokens=big_prefix, input_tokens=question, output_tokens=answer)
    # 场景 C：反模式（见 34.4）——断点设在每次变的内容上，每次写入、永不命中
    c = Usage(cache_write_tokens=big_prefix, input_tokens=question, output_tokens=answer)

    print("价目：Opus 4.5 $5/$25 每 MTok；写入 1.25×、读取 0.1×（核验 2026-10-08）\n")
    print("场景 A 不用缓存（单次）：     ", _fmt(cost_usd(a, OPUS_45)))
    print("场景 B 正确缓存 第1次(写入)： ", _fmt(cost_usd(b1, OPUS_45)))
    print("场景 B 正确缓存 第2次(命中)： ", _fmt(cost_usd(b2, OPUS_45)))
    print("场景 C 反模式 每次都写入：    ", _fmt(cost_usd(c, OPUS_45)))

    # 10 次交互横向对比
    n = 10
    cost_a = cost_usd(a, OPUS_45)["合计"] * n
    cost_b = cost_usd(b1, OPUS_45)["合计"] + cost_usd(b2, OPUS_45)["合计"] * (n - 1)
    cost_c = cost_usd(c, OPUS_45)["合计"] * n
    print(f"\n连续 {n} 次相同前缀的交互合计：")
    print(f"  A 不缓存         = ${round(cost_a, 4)}")
    print(f"  B 正确缓存       = ${round(cost_b, 4)}  （省 {round((1-cost_b/cost_a)*100,1)}%）")
    print(f"  C 缓存反模式     = ${round(cost_c, 4)}  （比不缓存还贵 {round((cost_c/cost_a-1)*100,1)}%）")
