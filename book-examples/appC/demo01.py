import pathlib, re

# 本书示例：禁止前端直连后端 endpoint 的结构测试
FRONTEND = pathlib.Path("src/frontend")
PATTERN = re.compile(r"\b(fetch|axios)\s*\(")

def test_no_direct_backend_calls():
    offenders = []
    for p in FRONTEND.rglob("*.ts"):
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if PATTERN.search(line) and "api-client" not in str(p):
                offenders.append(f"{p}:{i}: {line.strip()}")
    assert not offenders, (
        "前端不得直连后端 endpoint，必须经由统一 client 层：\n"
        + "\n".join(offenders)
    )
