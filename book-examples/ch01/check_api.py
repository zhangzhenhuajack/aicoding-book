import inspect
import json

# 这是 AI 生成的、我们怀疑含有幻觉 API 的调用点：(模块名, 属性名)
suspect_calls = [
    ("json", "load_file"),   # 幻觉：json 并没有 load_file
    ("json", "loads"),       # 真实存在
    ("json", "dumps"),       # 真实存在
    ("json", "pretty"),      # 幻觉：没有 pretty
]

modules = {"json": json}

for mod_name, name in suspect_calls:
    mod = modules[mod_name]
    exists = hasattr(mod, name)
    mark = "OK   存在" if exists else "FAIL 幻觉"
    print(f"[{mark}] {mod_name}.{name}")
    if not exists:
        real = [n for n, _ in inspect.getmembers(mod) if not n.startswith("_")]
        near = [n for n in real if name[:4] in n or "load" in n or "dump" in n]
        print(f"        该模块并无此名；相近的真实名有: {sorted(set(near))}")
