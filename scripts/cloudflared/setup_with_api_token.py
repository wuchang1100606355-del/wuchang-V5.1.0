"""
使用 Cloudflare API 令牌設定 Tunnel
不需要瀏覽器登入，完全自動化
"""

import requests
import json
import os
import sys
from pathlib import Path

# 設定 UTF-8 編碼
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Cloudflare API 設定
CLOUDFLARE_API_TOKEN = "PIh5SgixgtgTVSfTQ335fRADEj6XBcoB86e1geUs"
CLOUDFLARE_API_BASE = "https://api.cloudflare.com/client/v4"
ACCOUNT_ID = None  # 會自動取得

def get_account_id():
    """取得 Cloudflare Account ID"""
    global ACCOUNT_ID
    if ACCOUNT_ID:
        return ACCOUNT_ID
    
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{CLOUDFLARE_API_BASE}/accounts", headers=headers)
    if response.status_code == 200:
        accounts = response.json()
        if accounts.get("result") and len(accounts["result"]) > 0:
            ACCOUNT_ID = accounts["result"][0]["id"]
            print(f"✅ 取得 Account ID: {ACCOUNT_ID}")
            return ACCOUNT_ID
    else:
        print(f"❌ 無法取得 Account ID: {response.status_code}")
        print(f"   回應: {response.text}")
    return None

def list_tunnels():
    """列出所有 Tunnel"""
    account_id = get_account_id()
    if not account_id:
        return []
    
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{CLOUDFLARE_API_BASE}/accounts/{account_id}/cfd_tunnel",
        headers=headers
    )
    
    if response.status_code == 200:
        tunnels = response.json()
        return tunnels.get("result", [])
    else:
        print(f"❌ 無法列出 Tunnel: {response.status_code}")
        print(f"   回應: {response.text}")
        return []

def create_tunnel(name="wuchang-life"):
    """建立新的 Tunnel"""
    account_id = get_account_id()
    if not account_id:
        return None
    
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "name": name,
        "config_src": "local"
    }
    
    response = requests.post(
        f"{CLOUDFLARE_API_BASE}/accounts/{account_id}/cfd_tunnel",
        headers=headers,
        json=data
    )
    
    print(f"   狀態碼: {response.status_code}")
    print(f"   回應: {response.text[:500]}")
    
    if response.status_code == 200:
        tunnel = response.json()
        tunnel_id = tunnel.get("result", {}).get("id")
        tunnel_secret = tunnel.get("result", {}).get("tunnel_secret")
        print(f"✅ 建立 Tunnel 成功: {name}")
        print(f"   Tunnel ID: {tunnel_id}")
        return {
            "id": tunnel_id,
            "name": name,
            "secret": tunnel_secret
        }
    else:
        print(f"❌ 無法建立 Tunnel: {response.status_code}")
        print(f"   回應: {response.text}")
        return None

def get_tunnel_token(tunnel_id):
    """取得 Tunnel Token（用於 credentials.json）"""
    account_id = get_account_id()
    if not account_id:
        return None
    
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{CLOUDFLARE_API_BASE}/accounts/{account_id}/cfd_tunnel/{tunnel_id}/token",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        token = result.get("result", {}).get("token")
        return token
    else:
        print(f"❌ 無法取得 Tunnel Token: {response.status_code}")
        print(f"   回應: {response.text}")
        return None

def create_credentials_file(tunnel_id, account_id, token):
    """建立 credentials.json 檔案"""
    credentials = {
        "AccountTag": account_id,
        "TunnelSecret": token,
        "TunnelID": tunnel_id,
        "TunnelName": "wuchang-life"
    }
    
    # 建立 credentials.json
    creds_path = Path("cloudflared/credentials.json")
    creds_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(creds_path, "w", encoding="utf-8") as f:
        json.dump(credentials, f, indent=2)
    
    print(f"✅ 已建立 credentials.json: {creds_path}")
    return creds_path

def main():
    """主函數"""
    print("=" * 60)
    print("使用 Cloudflare API 令牌設定 Tunnel")
    print("=" * 60)
    print()
    
    # 1. 檢查現有 Tunnel
    print("[1] 檢查現有 Tunnel...")
    tunnels = list_tunnels()
    if tunnels:
        print(f"   找到 {len(tunnels)} 個 Tunnel:")
        for tunnel in tunnels:
            print(f"   - {tunnel.get('name')} (ID: {tunnel.get('id')})")
    else:
        print("   沒有找到現有 Tunnel")
    print()
    
    # 2. 建立或使用現有 Tunnel
    print("[2] 建立或使用 Tunnel...")
    tunnel_name = "wuchang-life"
    tunnel_info = None
    
    # 檢查是否已存在
    for tunnel in tunnels:
        if tunnel.get("name") == tunnel_name:
            print(f"   ✅ 使用現有 Tunnel: {tunnel_name}")
            tunnel_info = {
                "id": tunnel.get("id"),
                "name": tunnel.get("name"),
                "secret": None  # 需要另外取得
            }
            break
    
    # 如果不存在，建立新的
    if not tunnel_info:
        print(f"   📝 建立新 Tunnel: {tunnel_name}")
        tunnel_info = create_tunnel(tunnel_name)
        if not tunnel_info:
            print("❌ 無法建立 Tunnel")
            print("   提示：可能需要使用 cloudflared CLI 建立 Tunnel")
            print("   執行：docker exec -it wuchangv510-cloudflared-1 cloudflared tunnel create wuchang-life")
            return
    
    print(f"   Tunnel ID: {tunnel_info['id']}")
    print()
    
    # 3. 取得 Tunnel Token
    print("[3] 取得 Tunnel Token...")
    account_id = get_account_id()
    token = get_tunnel_token(tunnel_info["id"])
    
    if not token:
        print("❌ 無法取得 Tunnel Token")
        return
    
    print("   ✅ 已取得 Token")
    print()
    
    # 4. 建立 credentials.json
    print("[4] 建立 credentials.json...")
    creds_path = create_credentials_file(
        tunnel_info["id"],
        account_id,
        token
    )
    print()
    
    # 5. 更新 config.yml
    print("[5] 更新 config.yml...")
    config_path = Path("cloudflared/config.yml")
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config_content = f.read()
        
        # 更新 Tunnel ID
        if "tunnel: <tunnel-id>" in config_content or "tunnel: PIh5SgixgtgTVSfTQ335fRADEj6XBcoB86e1geUs" in config_content:
            config_content = config_content.replace(
                "tunnel: <tunnel-id>",
                f"tunnel: {tunnel_info['id']}"
            )
            config_content = config_content.replace(
                "tunnel: PIh5SgixgtgTVSfTQ335fRADEj6XBcoB86e1geUs",
                f"tunnel: {tunnel_info['id']}"
            )
            
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(config_content)
            
            print(f"   ✅ 已更新 config.yml")
            print(f"   Tunnel ID: {tunnel_info['id']}")
        else:
            print(f"   ⚠️  config.yml 中已有 Tunnel ID，未更新")
    else:
        print(f"   ⚠️  config.yml 不存在")
    print()
    
    # 6. 總結
    print("=" * 60)
    print("✅ 設定完成！")
    print("=" * 60)
    print()
    print("📋 下一步操作：")
    print("  1. 複製檔案到容器：")
    print(f"     docker cp cloudflared/config.yml wuchangv510-cloudflared-1:/etc/cloudflared/config.yml")
    print(f"     docker cp {creds_path} wuchangv510-cloudflared-1:/etc/cloudflared/credentials.json")
    print("  2. 重啟容器：")
    print("     docker restart wuchangv510-cloudflared-1")
    print("  3. 檢查日誌：")
    print("     docker logs wuchangv510-cloudflared-1")
    print("  4. 在 Squarespace 設定 DNS：")
    print(f"     CNAME @ → {tunnel_info['id']}.cfargotunnel.com")
    print(f"     CNAME www → {tunnel_info['id']}.cfargotunnel.com")
    print()
    print(f"📌 Tunnel ID: {tunnel_info['id']}")

if __name__ == "__main__":
    main()
