"""檢查標準容器配置"""
import subprocess
import sys

# 設定 UTF-8 編碼
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

# 標準容器配置（根據 CONTAINER_MANAGEMENT_GUIDE.md）
STANDARD_CONTAINERS = {
    "核心服務": [
        ("wuchang-web", "Odoo ERP 系統", 8069),
        ("db", "PostgreSQL 資料庫", 5432),
    ],
    "Web 服務": [
        ("caddy", "Caddy Web 伺服器", [80, 443]),
        ("caddy-ui", "Caddy 管理介面", [8081, 8444]),
    ],
    "網路服務": [
        ("cloudflared", "Cloudflare Tunnel", None),
    ],
    "AI 服務": [
        ("ollama", "AI 模型服務", 11434),
        ("open-webui", "AI 介面", 8080),
    ],
    "管理工具": [
        ("portainer", "容器管理介面", 9000),
        ("uptime-kuma", "監控工具", 3001),
    ]
}

def get_running_containers():
    """取得運行中的容器"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            return []
        
        return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
    except Exception as e:
        print(f"無法取得容器列表: {e}")
        return []

def check_standard_containers():
    """檢查標準容器"""
    print("=" * 70)
    print("標準容器配置檢查")
    print("=" * 70)
    print()
    
    running = get_running_containers()
    
    print("【標準容器配置】")
    print()
    
    total_standard = 0
    found_containers = []
    missing_containers = []
    
    for category, containers in STANDARD_CONTAINERS.items():
        print(f"📦 {category}:")
        for name_pattern, description, port in containers:
            total_standard += 1
            # 檢查是否有匹配的容器名稱
            matched = [c for c in running if name_pattern.lower() in c.lower()]
            
            if matched:
                found_containers.append((matched[0], description, port))
                port_str = f"端口: {port}" if port else "無對外端口"
                print(f"  ✅ {description} ({matched[0]}) - {port_str}")
            else:
                missing_containers.append((name_pattern, description, port))
                port_str = f"端口: {port}" if port else "無對外端口"
                print(f"  ❌ {description} ({name_pattern}) - {port_str} [未運行]")
        print()
    
    print("=" * 70)
    print("【統計摘要】")
    print("=" * 70)
    print()
    
    print(f"標準容器總數: {total_standard}")
    print(f"✅ 已運行: {len(found_containers)}")
    print(f"❌ 未運行: {len(missing_containers)}")
    print(f"📊 運行率: {len(found_containers)/total_standard*100:.1f}%")
    print()
    
    # 其他容器
    other_containers = [c for c in running if not any(
        pattern.lower() in c.lower() 
        for pattern, _, _ in sum(STANDARD_CONTAINERS.values(), [])
    )]
    
    if other_containers:
        print("=" * 70)
        print("【其他容器（非標準配置）】")
        print("=" * 70)
        print()
        for container in other_containers:
            print(f"  ⚠️ {container}")
        print()
    
    print("=" * 70)
    print("【結論】")
    print("=" * 70)
    print()
    
    if len(missing_containers) == 0:
        print("✅ 所有標準容器都在運行中")
    else:
        print(f"⚠️ 有 {len(missing_containers)} 個標準容器未運行:")
        for name, desc, _ in missing_containers:
            print(f"   - {desc} ({name})")
    
    print()
    print(f"標準配置應有 {total_standard} 個容器")
    print(f"目前運行中: {len(found_containers)} 個標準容器")
    if other_containers:
        print(f"其他容器: {len(other_containers)} 個")

if __name__ == "__main__":
    check_standard_containers()
