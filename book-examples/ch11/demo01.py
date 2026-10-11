from dataclasses import dataclass, field

# 五个选型维度（与 11.1 节比较维度一致）
DIMENSIONS = [
    ("failure_cost", "失败代价（越高越需要强安全托底）"),
    ("parallelism", "并行吞吐需求（人少、任务可大量并行）"),
    ("consistency", "一致性/治理需求（人多、要统一标准）"),
    ("self_assembly", "自建意愿（想自己组装、不被平台绑死）"),
    ("maintenance_budget", "可投入的维护预算"),
]

# 四大流派在各维度上的契合基准分（0-5，本书示意值，非厂商数据）
SCHOOLS = {
    "Anthropic（约束+纠正，重安全托底）": {
        "failure_cost": 5, "parallelism": 2, "consistency": 3,
        "self_assembly": 1, "maintenance_budget": 3},
    "OpenAI（验证+告知，重并行掌舵）": {
        "failure_cost": 3, "parallelism": 5, "consistency": 3,
        "self_assembly": 2, "maintenance_budget": 3},
    "Kiro（告知+约束，重规格治理）": {
        "failure_cost": 4, "parallelism": 2, "consistency": 5,
        "self_assembly": 1, "maintenance_budget": 2},
    "开源流派（做底座，自配缰绳）": {
        "failure_cost": 2, "parallelism": 3, "consistency": 2,
        "self_assembly": 5, "maintenance_budget": 1},
}

@dataclass
class Profile:
    weights: dict = field(default_factory=dict)
    def validate(self):
        for key, _ in DIMENSIONS:
            w = self.weights.get(key, 0)
            if not 0 <= w <= 5:
                raise ValueError(f"维度 {key} 的权重必须在 0-5，收到 {w}")

def score(profile):
    profile.validate()
    results = []
    for school, base in SCHOOLS.items():
        total, reasons = 0, []
        for key, label in DIMENSIONS:
            w = profile.weights.get(key, 0)
            contrib = w * base[key]
            total += contrib
            if w >= 3 and base[key] >= 4:
                reasons.append((contrib, f"在「{label}」上契合度高（{base[key]}×权重{w}=+{contrib}）"))
            elif w >= 3 and base[key] <= 2:
                reasons.append((contrib, f"但在「{label}」上是短板（仅 {base[key]}×权重{w}=+{contrib}）"))
        reasons.sort(key=lambda x: -x[0])
        results.append((school, total, [r for _, r in reasons[:3]]))
    results.sort(key=lambda x: -x[1])
    return results

if __name__ == "__main__":
    # 场景：金融核心系统小团队——失败代价极高、人少想并行、
    # 一致性中等、不想自建缰绳、维护预算一般。
    demo = Profile(weights={"failure_cost": 5, "parallelism": 4,
        "consistency": 2, "self_assembly": 1, "maintenance_budget": 2})
    for i, (s, t, rs) in enumerate(score(demo), 1):
        print(f"{i}. {s}  总分 {t}")
        for r in rs:
            print(f"   - {r}")
