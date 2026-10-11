signal = "SPEC: 过期后 accept 必须报错"          # 唯一的关键句
noise = ["# 无关日志行 %d" % i for i in range(40)]  # 噪声

def build(selected: bool):
    if selected:
        ctx = [signal, "src/invite.py: accept_invite(token)"]       # 精选：只放相关
    else:
        ctx = noise[:20] + [signal] + noise[20:]                    # 塞满：关键句埋中间
    return ctx

for selected in (True, False):
    ctx = build(selected)
    pos = ctx.index(signal)
    pct = (pos + 1) / len(ctx) * 100
    tag = "精选" if selected else "塞满"
    print(f"[{tag}] 共 {len(ctx):2d} 行，关键句在第 {pos+1:2d} 行"
          f"（相对位置 {pct:4.0f}% {'头部' if pct<=33 else '中部盲区' if pct<=66 else '尾部'}）")
