"""Anthropic → OpenAI 协议转换 proxy
让 Claude Code（Anthropic 协议）能用 lidlid（OpenAI 协议）。

用法:
  export LIDLID_API_KEY=***
  export LIDLID_MODEL=claude-opus-4-8
  python3 anthropic-to-openai-proxy.py --port 9876
然后 Claude Code:
  ANTHROPIC_BASE_URL=http://127.0.0.1:9876
  ANTHROPIC_API_KEY=dummy
  ANTHROPIC_MODEL=claude-opus-4-8
"""
import json
import os
import time
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import urllib.request
import urllib.error

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# 配置
import os
UPSTREAM_BASE = os.environ.get("LIDLID_BASE_URL", "https://new.lidlid.cc/v1")
UPSTREAM_KEY = os.environ.get("LIDLID_API_KEY", "")
UPSTREAM_MODEL = os.environ.get("LIDLID_MODEL", "claude-opus-4-8")

# 客户端 → 服务端的 headers 转换
def anthropic_to_openai_request(anthropic_body: dict, model: str):
    """Anthropic /v1/messages 格式 → OpenAI /v1/chat/completions 格式"""
    messages = []

    # system 字段 (Anthropic 可以是 string 或 list)
    system = anthropic_body.get("system")
    if system:
        if isinstance(system, str):
            messages.append({"role": "system", "content": system})
        elif isinstance(system, list):
            for block in system:
                if block.get("type") == "text":
                    messages.append({"role": "system", "content": block.get("text", "")})

    # messages
    for msg in anthropic_body.get("messages", []):
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if isinstance(content, list):
            # Anthropic 多模态 content 是 list of blocks
            text_parts = []
            for block in content:
                if block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            content = "\n".join(text_parts)
        messages.append({"role": role, "content": content})

    return {
        "model": model,
        "messages": messages,
        "max_tokens": anthropic_body.get("max_tokens", 4096),
        "temperature": anthropic_body.get("temperature", 1.0),
        "stream": anthropic_body.get("stream", False),
    }


def openai_to_anthropic_response(openai_resp: dict, model: str):
    """OpenAI 响应 → Anthropic 响应"""
    choice = openai_resp.get("choices", [{}])[0]
    message = choice.get("message", {})
    text = message.get("content", "")

    finish_reason = choice.get("finish_reason", "stop")
    stop_reason_map = {
        "stop": "end_turn",
        "length": "max_tokens",
        "tool_calls": "tool_use",
        "content_filter": "refusal",
    }
    stop_reason = stop_reason_map.get(finish_reason, "end_turn")

    return {
        "id": openai_resp.get("id", "msg_" + str(int(time.time()))),
        "type": "message",
        "role": "assistant",
        "model": model,
        "content": [{"type": "text", "text": text}],
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": {
            "input_tokens": openai_resp.get("usage", {}).get("prompt_tokens", 0),
            "output_tokens": openai_resp.get("usage", {}).get("completion_tokens", 0),
        },
    }


class ProxyHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # 简化日志 + 强制 flush
        msg = f"[{time.strftime('%H:%M:%S')}] {format % args}"
        print(msg, flush=True)
        # 写到 log 文件
        with open('/tmp/anthropic-proxy.log', 'a') as f:
            f.write(msg + '\n')

    def do_POST(self):
        msg = f"[POST] {self.path} from {self.client_address}\n"
        with open('/tmp/anthropic-proxy.log', 'a') as f:
            f.write(msg)
        print(msg, flush=True)
        if self.path.startswith("/v1/messages") or self.path == "/v1/messages":
            self.send_error(404, "Not Found")
            return

        # 读 body
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length)
        try:
            body = json.loads(body_bytes)
        except Exception as e:
            self.send_error(400, f"Invalid JSON: {e}")
            return

        # 拿 model
        model = body.get("model", "claude-opus-4.8")
        stream = body.get("stream", False)

        # 转 OpenAI
        openai_req = anthropic_to_openai_request(body, model)

        # 转发到 OpenAI
        try:
            if HAS_REQUESTS:
                resp = requests.post(
                    f"{UPSTREAM_BASE}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {UPSTREAM_KEY}",
                        "Content-Type": "application/json",
                    },
                    json=openai_req,
                    timeout=60,
                )
                openai_resp = resp.json()
            else:
                req = urllib.request.Request(
                    f"{UPSTREAM_BASE}/chat/completions",
                    data=json.dumps(openai_req).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {UPSTREAM_KEY}",
                        "Content-Type": "application/json",
                    },
                )
                with urllib.request.urlopen(req, timeout=60) as r:
                    openai_resp = json.loads(r.read())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(error_body.encode("utf-8"))
            return
        except Exception as e:
            self.send_error(502, f"Upstream error: {e}")
            return

        # 转 Anthropic
        anthropic_resp = openai_to_anthropic_response(openai_resp, model)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(anthropic_resp).encode("utf-8"))

    def do_GET(self):
        msg = f"[GET] {self.path}\n"
        with open('/tmp/anthropic-proxy.log', 'a') as f:
            f.write(msg)
        print(msg, flush=True)
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        elif self.path == "/v1/models":
            # 模拟 OpenAI /v1/models 响应（让 Claude Code init 验证通过）
            model_id = os.environ.get("LIDLID_MODEL", "claude-opus-4-8")
            response = {
                "object": "list",
                "data": [
                    {"id": model_id, "object": "model", "created": int(time.time()), "owned_by": "lidlid"}
                ]
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode("utf-8"))
        else:
            self.send_error(404)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=9876)
    args = ap.parse_args()

    server = ThreadingHTTPServer(("127.0.0.1", args.port), ProxyHandler)
    print(f"✅ Anthropic→OpenAI proxy listening on 127.0.0.1:{args.port}")
    print(f"   Upstream: {UPSTREAM_BASE}")
    print(f"   Claude Code setup:")
    print(f'     ANTHROPIC_BASE_URL=http://127.0.0.1:{args.port}')
    print(f'     ANTHROPIC_API_KEY="<任意字符串>"')
    print(f'     ANTHROPIC_MODEL="claude-opus-4.8"')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
