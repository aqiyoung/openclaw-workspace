#!/bin/bash
# 用法: ./switch-model.sh [provider/model]
# 不带参数: 显示当前状态
# 带参数: 切换主模型
set -e

CONFIG="/home/liyang/.openclaw/openclaw.json"

if [ -z "$1" ]; then
  echo "=== 当前主模型 ==="
  python3 -c "
import json
c = json.load(open('$CONFIG'))
m = c['agents']['defaults']['model']
print(f'primary: {m[\"primary\"]}')
print(f'fallback ({len(m[\"fallbacks\"])}):')
for f in m['fallbacks']:
    print(f'  - {f}')"
  exit 0
fi

NEW_MODEL="$1"
echo "切换到: $NEW_MODEL"

# 验证 model 存在
python3 << PYEOF
import json, sys
new = "$NEW_MODEL"
c = json.load(open("$CONFIG"))
prov, mid = new.split('/', 1)
if prov not in c['models']['providers']:
    print(f"❌ provider {prov} 不存在")
    print(f"   可用: {list(c['models']['providers'].keys())}")
    sys.exit(1)
provider = c['models']['providers'][prov]
if not any(m.get('id') == mid for m in provider.get('models', [])):
    print(f"❌ model {mid} 不在 {prov}")
    print(f"   可用: {[m.get('id') for m in provider.get('models', [])]}")
    sys.exit(1)
old = c['agents']['defaults']['model']['primary']
c['agents']['defaults']['model']['primary'] = new
with open("$CONFIG", 'w') as f:
    json.dump(c, f, indent=2, ensure_ascii=False)
print(f"✅ 切换: {old} → {new}")
PYEOF
