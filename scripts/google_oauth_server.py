#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse, json, requests, os, sys

CLIENT_SECRET_FILE = os.path.expanduser("~/.openclaw/workspace/google_client_secret.json")
TOKEN_FILE = os.path.expanduser("~/.openclaw/workspace/google_token.json")
REDIRECT_URI = "https://nas.threel.site/oauth2/callback"

with open(CLIENT_SECRET_FILE) as f:
    creds = json.load(f)
CLIENT_ID = creds["web"]["client_id"]
CLIENT_SECRET = creds["web"]["client_secret"]

class Handler(BaseHTTPRequestHandler):
    def _handle(self, body=""):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        
        # 尝试从 body 读取参数（POST 场景）
        if body:
            body_params = urllib.parse.parse_qs(body)
            for k, v in body_params.items():
                if k not in params:
                    params[k] = v
        
        with open("/tmp/oauth_debug.log", "a") as f:
            f.write(f"\n--- {self.command} {parsed.path} ---\n")
            f.write(f"query: {parsed.query}\n")
            f.write(f"body: {body[:200]}\n")
            f.write(f"params: {json.dumps(params, ensure_ascii=False)}\n")
        
        code = params.get("code", [""])[0]
        error = params.get("error", [""])[0]
        
        if code:
            try:
                resp = requests.post("https://oauth2.googleapis.com/token", data={
                    "code": code, "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "redirect_uri": REDIRECT_URI,
                    "grant_type": "authorization_code"
                }, timeout=10)
                token_data = resp.json()
                
                with open("/tmp/oauth_debug.log", "a") as f:
                    f.write(f"token_resp: {json.dumps(token_data, ensure_ascii=False)[:500]}\n")
                
                if "access_token" in token_data:
                    with open(TOKEN_FILE, "w") as f:
                        json.dump(token_data, f, indent=2)
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write("<h1>✅ 授权成功！可以关闭此页面。</h1>".encode())
                    print("✅ Token saved!", flush=True)
                    sys.exit(0)
                else:
                    self.send_response(400)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(f"<h1>❌ Token 交换失败</h1><pre>{json.dumps(token_data, ensure_ascii=False)}</pre>".encode())
                    print(f"❌ {token_data}", flush=True)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
                print(f"❌ {e}", flush=True)
        elif error:
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"<h1>❌ Google error: {error}</h1>".encode())
            print(f"❌ Google: {error}", flush=True)
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h1>OAuth 回调服务运行中</h1><p>等待授权回调...</p>".encode())
    
    def do_GET(self):
        self._handle()
    
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8", errors="ignore") if length > 0 else ""
        self._handle(body)
    
    def log_message(self, *a): pass

print("🌐 调试模式 v2 启动", flush=True)
server = HTTPServer(("127.0.0.1", 8899), Handler)
server.serve_forever()
