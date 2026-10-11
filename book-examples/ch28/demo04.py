import random
import statistics

HOURS_PER_SPRINT = 2 * 5 * 8  # 两周 × 5 工作日 × 8 小时 = 80 小时


def mm1_metrics(lam: float, mu: float) -> dict:
    """M/M/1 稳态：lam=到达率(PR/小时)，mu=单评审者服务率(PR/小时)。"""
    if lam >= mu:
        return {"rho": lam / mu, "stable": False, "Wq_h": float("inf"), "Lq": float("inf")}
    rho = lam / mu
    Lq = rho * rho / (1 - rho)          # 队列中平均 PR 数
    Wq = rho / (mu - lam)               # 平均排队等待(小时)
    return {"rho": rho, "stable": True, "Wq_h": Wq, "Lq": Lq}


def simulate(lam: float, mu: float, hours: int = HOURS_PER_SPRINT, seed: int = 42) -> dict:
    """离散事件仿真：PR 按泊松到达，单评审者 FIFO 处理，服务时间指数分布。"""
    rng = random.Random(seed)
    t, server_free, waits, done = 0.0, 0.0, [], 0
    arrivals = []
    while t < hours:
        t += rng.expovariate(lam)
        if t < hours:
            arrivals.append(t)
    for a in arrivals:
        start = max(a, server_free)
        wait = start - a
        server_free = start + rng.expovariate(mu)
        if start < hours:
            waits.append(wait)
            if server_free <= hours:
                done += 1
    created = len(arrivals)
    return {"created": created, "merged": done, "backlog": created - done,
            "avg_wait_h": statistics.mean(waits) if waits else 0.0}


def row(label: str, lam: float, mu: float) -> None:
    m, s = mm1_metrics(lam, mu), simulate(lam, mu)
    rho = f"{m['rho']*100:5.1f}%"
    wq = "∞" if not m["stable"] else f"{m['Wq_h']:5.2f}h"
    print(f"{label:14s} 到达{lam:4.1f}/h 利用率{rho}  理论等待{wq:>7s} "
          f"| 仿真: 开{s['created']:3d} 合{s['merged']:3d} 积压{s['backlog']:3d} "
          f"均等待{s['avg_wait_h']:5.2f}h")


if __name__ == "__main__":
    MU = 1.0  # 评审者每小时能认真评审 1 个中等 PR（示意）
    print(f"单评审者服务率 μ = {MU:.1f} PR/小时；Sprint = {HOURS_PER_SPRINT} 小时（示意数据）\n")
    row("AI 前", 0.4, MU)        # 人工产出慢，评审轻松
    row("AI 后·同评审", 0.9, MU)  # 产出翻倍多，单评审者接近饱和
    row("AI 后·过载", 1.3, MU)    # 产出超过评审能力，系统发散
