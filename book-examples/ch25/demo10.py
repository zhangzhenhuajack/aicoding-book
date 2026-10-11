# bench25.py —— 本书示例
import time, statistics
from fastapi.testclient import TestClient
from app.main import create_app

c = TestClient(create_app())
for _ in range(50):          # 预热
    c.get("/openapi.json")
N, lat = 2000, []
t0 = time.perf_counter()
for _ in range(N):
    s = time.perf_counter()
    r = c.get("/openapi.json")
    lat.append((time.perf_counter() - s) * 1000)
    assert r.status_code == 200
wall = time.perf_counter() - t0
lat.sort()
print(f"N={N} wall={wall:.2f}s throughput={N/wall:.0f} req/s")
print(f"ms: p50={statistics.median(lat):.2f} "
      f"p95={lat[int(N*0.95)]:.2f} p99={lat[int(N*0.99)]:.2f} max={lat[-1]:.2f}")
