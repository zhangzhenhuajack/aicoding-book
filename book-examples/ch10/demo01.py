#!/usr/bin/env python3
"""最小假服务器：模拟 OpenAI 兼容的 /v1/chat/completions 端点。
仅用于演示——不调用任何真实模型，只把收到的最后一条用户消息回声，
并加上本服务器自报的 provider 名，证明"换的只是地址，不是代码"。
运行：python3 fake_openai_server.py <port> <provider_name>
"""
import json, sys, time
from http.server import BaseHTTPRequestHandler, HTTPServer

PROVIDER = sys.argv[2] if len(sys.argv) > 2 else "fake-A"

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # 静音默认访问日志

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self.send_error(404, "no such endpoint"); return
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        model = body.get("model", "unknown")
        msgs = body.get("messages", [])
        user_text = next((m["content"] for m in reversed(msgs)
                          if m.get("role") == "user"), "")
        reply = f"[{PROVIDER}:{model}] 你说的是：{user_text}"
        resp = {
            "id": f"chatcmpl-{PROVIDER}-{int(time.time())}",
            "object": "chat.completion", "model": model,
            "choices": [{"index": 0,
                "message": {"role": "assistant", "content": reply},
                "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }
        data = json.dumps(resp).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8101
    srv = HTTPServer(("127.0.0.1", port), Handler)
    print(f"fake OpenAI-compatible server [{PROVIDER}] on 127.0.0.1:{port}")
    srv.serve_forever()
