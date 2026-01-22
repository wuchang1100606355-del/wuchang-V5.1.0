"""
使用 Cloudflare API 令牌自動設定 DNS 記錄
完全自動化，不需要手動操作 Squarespace
"""

import requests
import json
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
ZONE_NAME = "wuchang.life"

def get_zone_id():
    """取得 Zone ID"""
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{CLOUDFLARE_API_BASE}/zones",
        headers=headers,
        params={"name": ZONE_NAME}
    )
    
    if response.status_code == 200:
        zones = response.json()
        if zones.get("result") and len(zones["result"]) > 0:
            zone_id = zones["result"][0]["id"]
            print(f"✅ 取得 Zone ID: {zone_id}")
            return zone_id
    else:
        print(f"❌ 無法取得 Zone ID: {response.status_code}")
        print(f"   回應: {response.text}")
    return None

def list_dns_records(zone_id):
    """列出所有 DNS 記錄"""
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{CLOUDFLARE_API_BASE}/zones/{zone_id}/dns_records",
        headers=headers
    )
    
    if response.status_code == 200:
        records = response.json()
        return records.get("result", [])
    else:
        print(f"❌ 無法列出 DNS 記錄: {response.status_code}")
        return []

def create_cname_record(zone_id, name, target):
    """建立 CNAME 記錄"""
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "type": "CNAME",
        "name": name,
        "content": target,
        "ttl": 300
    }
    
    response = requests.post(
        f"{CLOUDFLARE_API_BASE}/zones/{zone_id}/dns_records",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        record = response.json()
        print(f"✅ 建立 CNAME 記錄成功: {name} → {target}")
        return record.get("result")
    else:
        print(f"❌ 無法建立 CNAME 記錄: {response.status_code}")
        print(f"   回應: {response.text}")
        return None

def update_dns_record(zone_id, record_id, name, target):
    """更新 DNS 記錄"""
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "type": "CNAME",
        "name": name,
        "content": target,
        "ttl": 300
    }
    
    response = requests.put(
        f"{CLOUDFLARE_API_BASE}/zones/{zone_id}/dns_records/{record_id}",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        record = response.json()
        print(f"✅ 更新 DNS 記錄成功: {name} → {target}")
        return record.get("result")
    else:
        print(f"❌ 無法更新 DNS 記錄: {response.status_code}")
        print(f"   回應: {response.text}")
        return None

def delete_dns_record(zone_id, record_id, name):
    """刪除 DNS 記錄"""
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.delete(
        f"{CLOUDFLARE_API_BASE}/zones/{zone_id}/dns_records/{record_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✅ 刪除 DNS 記錄成功: {name}")
        return True
    else:
        print(f"❌ 無法刪除 DNS 記錄: {response.status_code}")
        print(f"   回應: {response.text}")
        return False

def main():
    """主函數"""
    print("=" * 60)
    print("使用 Cloudflare API 令牌自動設定 DNS")
    print("=" * 60)
    print()
    
    # 取得 Tunnel ID（需要用戶輸入）
    tunnel_id = input("請輸入 Tunnel ID: ").strip()
    if not tunnel_id:
        print("❌ 必須提供 Tunnel ID")
        print("   取得方式：docker exec -it wuchangv510-cloudflared-1 cloudflared tunnel list")
        return
    
    target = f"{tunnel_id}.cfargotunnel.com"
    print(f"目標: {target}")
    print()
    
    # 取得 Zone ID
    print("[1] 取得 Zone ID...")
    zone_id = get_zone_id()
    if not zone_id:
        print("❌ 無法取得 Zone ID，請確認：")
        print("   1. API 令牌權限是否足夠")
        print("   2. 網域是否已轉移到 Cloudflare（DNS 管理）")
        print()
        print("💡 如果 DNS 仍在 Squarespace 管理，請使用手動設定方法")
        return
    print()
    
    # 列出現有 DNS 記錄
    print("[2] 檢查現有 DNS 記錄...")
    records = list_dns_records(zone_id)
    print(f"   找到 {len(records)} 筆記錄")
    print()
    
    # 設定根域名（@）
    print("[3] 設定根域名（@）...")
    root_records = [r for r in records if r.get("name") == ZONE_NAME or r.get("name") == "@"]
    
    if root_records:
        # 更新第一個記錄
        first_record = root_records[0]
        if first_record.get("type") != "CNAME" or first_record.get("content") != target:
            update_dns_record(zone_id, first_record["id"], ZONE_NAME, target)
        else:
            print(f"   ✅ 根域名已正確設定")
        
        # 刪除其他根域名記錄
        for record in root_records[1:]:
            delete_dns_record(zone_id, record["id"], record.get("name", "@"))
    else:
        # 建立新記錄
        create_cname_record(zone_id, ZONE_NAME, target)
    print()
    
    # 設定 WWW 子域名
    print("[4] 設定 WWW 子域名...")
    www_name = f"www.{ZONE_NAME}"
    www_records = [r for r in records if r.get("name") == www_name]
    
    if www_records:
        www_record = www_records[0]
        if www_record.get("type") != "CNAME" or www_record.get("content") != target:
            update_dns_record(zone_id, www_record["id"], www_name, target)
        else:
            print(f"   ✅ WWW 子域名已正確設定")
    else:
        create_cname_record(zone_id, www_name, target)
    print()
    
    # 總結
    print("=" * 60)
    print("✅ DNS 設定完成！")
    print("=" * 60)
    print()
    print("📋 設定的記錄：")
    print(f"   {ZONE_NAME} → {target}")
    print(f"   www.{ZONE_NAME} → {target}")
    print()
    print("⏱️  DNS 傳播時間：約 5-10 分鐘")
    print("🔒 SSL 證書會自動簽發（約 5-10 分鐘）")

if __name__ == "__main__":
    main()
