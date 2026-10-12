"""Demo 34-2：缓存命中模拟（本书示例）
模拟官方回看机制（核验 2026-10-08）：写入只在断点处；读取只找先前写入的条目。
来源：https://docs.claude.com/en/docs/build-with-claude/prompt-caching
"""
import hashlib
from datetime import datetime, timedelta


class CacheSim:
    def __init__(self):
        self.store, self.writes, self.reads = set(), 0, 0

    @staticmethod
    def _hash(blocks):
        h = hashlib.sha256()
        for b in blocks:
            h.update(b.encode("utf-8")); h.update(b"\x00")
        return h.hexdigest()

    def request(self, blocks, breakpoint_index):
        key = self._hash(blocks[: breakpoint_index + 1])
        if key in self.store:
            self.reads += 1; return "HIT"
        self.store.add(key); self.writes += 1  # 真实系统只在断点处写
        return "MISS"


def run(label, make_blocks, breakpoint_index, n=5):
    sim, results = CacheSim(), []
    base = datetime(2026, 10, 8, 9, 0, 0)
    for i in range(n):
        ts = (base + timedelta(seconds=i * 30)).isoformat()
        results.append(sim.request(make_blocks(ts), breakpoint_index))
    print(f"{label}\n  每次结果: {results}")
    print(f"  写入次数={sim.writes}  读取(命中)次数={sim.reads}\n")


def blocks_with_ts(ts):  # block 0-4 稳定；block 5 含时间戳，每次变
    return ["SYSTEM: 你是 TeamPulse 后端开发助手", "RULES: 不得修改 tests/ 断言",
            "DOC: openapi.yaml 契约（稳定）", "DOC: 数据模型（稳定）",
            "DOC: 项目事实卡 30 行（稳定）", f"USER: [{ts}] 请实现邀请接口"]


if __name__ == "__main__":
    run("反模式：断点设在含时间戳的 block 5（index=5）", blocks_with_ts, 5)
    run("正解：断点设在最后一个稳定 block 4（index=4）", blocks_with_ts, 4)
