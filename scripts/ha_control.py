#!/usr/bin/env python3
"""HA 快速控制 - 自动缓存 token"""
import json, sys, time, os, requests

HA_URL = "http://127.0.0.1:8123"
TOKEN_FILE = os.path.expanduser("~/.openclaw/.ha_token")
USERNAME = "threely"
PASSWORD = "younglee1018"

def get_token():
    """获取或刷新 token"""
    # 先检查缓存
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE) as f:
                data = json.load(f)
            if time.time() < data.get("expires_at", 0):
                return data["token"]
        except Exception:
            pass
    
    # 重新登录
    r = requests.post(f"{HA_URL}/auth/login_flow", json={
        "client_id": f"{HA_URL}/",
        "handler": ["homeassistant", None],
        "redirect_uri": f"{HA_URL}/"
    })
    flow_id = r.json()["flow_id"]
    
    r = requests.post(f"{HA_URL}/auth/login_flow/{flow_id}", json={
        "username": USERNAME, "password": PASSWORD,
        "client_id": f"{HA_URL}/"
    })
    code = r.json()["result"]
    
    r = requests.post(f"{HA_URL}/auth/token", data={
        "grant_type": "authorization_code",
        "code": code,
        "client_id": f"{HA_URL}/"
    })
    token_data = r.json()
    token = token_data["access_token"]
    expires_in = token_data.get("expires_in", 1800)
    
    # 缓存（提前5分钟刷新）
    with open(TOKEN_FILE, "w") as f:
        json.dump({"token": token, "expires_at": time.time() + expires_in - 300}, f)
    
    return token

def call_api(method, path, data=None):
    """调用 HA API"""
    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    if method == "GET":
        r = requests.get(f"{HA_URL}{path}", headers=headers)
    else:
        r = requests.post(f"{HA_URL}{path}", headers=headers, json=data)
    return r.json()

def main():
    if len(sys.argv) < 2:
        print("用法: ha_control.py <action> [entity_id] [data]")
        print("  list [filter]     - 列出设备")
        print("  on <entity_id>    - 打开设备")
        print("  off <entity_id>   - 关闭设备")
        print("  toggle <entity_id>- 切换")
        print("  state <entity_id> - 查看状态")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "list":
        filter_kw = sys.argv[2] if len(sys.argv) > 2 else ""
        states = call_api("GET", "/api/states")
        for s in states:
            eid = s["entity_id"]
            name = s.get("attributes", {}).get("friendly_name", "")
            state = s["state"]
            if filter_kw and filter_kw.lower() not in eid.lower() and filter_kw.lower() not in name.lower():
                continue
            print(f"{state:>12}  {name:30s}  {eid}")
    
    elif action == "on":
        eid = sys.argv[2]
        domain = eid.split(".")[0]
        result = call_api("POST", f"/api/services/{domain}/turn_on", {"entity_id": eid})
        print(f"✅ 已打开 {eid}")
    
    elif action == "off":
        eid = sys.argv[2]
        domain = eid.split(".")[0]
        result = call_api("POST", f"/api/services/{domain}/turn_off", {"entity_id": eid})
        print(f"✅ 已关闭 {eid}")
    
    elif action == "toggle":
        eid = sys.argv[2]
        domain = eid.split(".")[0]
        result = call_api("POST", f"/api/services/{domain}/toggle", {"entity_id": eid})
        print(f"✅ 已切换 {eid}")
    
    elif action == "state":
        eid = sys.argv[2]
        result = call_api("GET", f"/api/states/{eid}")
        print(f"状态: {result['state']}")
        print(f"属性: {json.dumps(result.get('attributes', {}), ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    main()
