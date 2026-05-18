#!/usr/bin/env python3
"""模型切换面板 - 最小化版本"""
import json, os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler

# 配置
PORT = 18790
PASSWORD = "Younglee1018"

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = open(os.path.join(os.path.dirname(__file__), "model-switch.html")).read()
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""
        
        if self.path == "/api/login":
            try:
                d = json.loads(body)
                pwd = d.get("password", "")
                print(f"LOGIN: received='{pwd}' expected='{PASSWORD}'", file=sys.stderr)
                if pwd == PASSWORD:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(b'{"ok":true,"token":"test123"}')
                else:
                    self.send_response(403)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(b'{"error":"密码错误"}')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f'{"error":"{e}"}'.encode())
        else:
            self.send_response(404)
            self.end_headers()

print(f"启动模型切换面板，端口 {PORT}，密码 {PASSWORD}", file=sys.stderr)
HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
