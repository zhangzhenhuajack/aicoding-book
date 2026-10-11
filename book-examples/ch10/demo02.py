#!/usr/bin/env python3
"""同一段客户端代码，只改 base_url 就切换不同"模型提供方"。
这里用标准库 urllib 手写请求，等价于 openai SDK 的
client.chat.completions.create()，但不依赖第三方包，便于原样跑通。
"""
import json, os, urllib.request

def chat(base_url: str, api_key: str, model: str, prompt: str) -> str:
    """与任意 OpenAI 兼容端点对话——函数体不关心对面是谁。"""
    req = urllib.request.Request(
        f"{base_url}/v1/chat/completions",
        data=json.dumps({
            "model": model,
            "messages": [
                {"role": "system", "content": "你是一个有用的助手。"},
                {"role": "user", "content": prompt},
            ],
        }).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"},
        method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        resp = json.load(r)
    return resp["choices"][0]["message"]["content"]

if __name__ == "__main__":
    # 两套"提供方"配置——真实场景里这就是 OpenAI / DeepSeek / 本地 vLLM 的区别。
    providers = [
        {"name": "供应商 A", "base_url": os.environ.get("A_URL", "http://127.0.0.1:8101"),
         "api_key": "sk-fake-A", "model": "model-a"},
        {"name": "供应商 B", "base_url": os.environ.get("B_URL", "http://127.0.0.1:8102"),
         "api_key": "sk-fake-B", "model": "model-b"},
    ]
    prompt = "用一句话解释什么是 OpenAI 兼容接口"
    for p in providers:
        out = chat(p["base_url"], p["api_key"], p["model"], prompt)
        print(f"{p['name']} -> {out}")
