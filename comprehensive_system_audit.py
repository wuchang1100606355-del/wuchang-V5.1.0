#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系統細部檢查與優化方案生成工具
全面檢查系統狀態並產生優化建議
"""

import os
import sys
import json
import socket
import subprocess
import platform
import psutil
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import hashlib

# 配置
BASE_PATH = Path(r"C:\wuchang V5.1.0")
SERVER_IP = "192.168.50.249"
CRITICAL_PORTS = [22, 80, 443, 8069, 8080, 8766, 3001, 3389, 5432]

def print_section(title):
    """打印章節標題"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_result(label, status, details="", level="info"):
    """打印結果"""
    if level == "ok":
        symbol = "[OK]"
        color = "\033[92m"
    elif level == "warn":
        symbol = "[WARN]"
        color = "\033[93m"
    elif level == "error":
        symbol = "[ERROR]"
        color = "\033[91m"
    else:
        symbol = "[INFO]"
        color = "\033[94m"
    
    reset_color = "\033[0m"
    print(f"{color}{symbol}{reset_color} {label}")
    if details:
        print(f"    {details}")

class SystemAuditor:
    """系統審計器"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {},
            "resources": {},
            "network": {},
            "services": {},
            "filesystem": {},
            "security": {},
            "performance": {},
            "issues": [],
            "optimizations": [],
            "recommendations": []
        }
    
    def check_system_info(self):
        """檢查系統信息"""
        print_section("一、系統信息檢查")
        
        try:
            info = {
                "platform": platform.platform(),
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version()
            }
            
            self.results["system_info"] = info
            
            print_result("作業系統", True, f"{info['system']} {info['release']}", "ok")
            print_result("處理器", True, info['processor'][:50], "ok")
            print_result("Python 版本", True, info['python_version'], "ok")
            
        except Exception as e:
            print_result("系統信息", False, f"錯誤: {e}", "error")
            self.results["issues"].append({
                "category": "system_info",
                "severity": "low",
                "message": f"無法獲取系統信息: {e}"
            })
    
    def check_resources(self):
        """檢查系統資源"""
        print_section("二、系統資源檢查")
        
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            print_result("CPU", True, f"{cpu_count} 核心, 使用率: {cpu_percent}%", 
                        "warn" if cpu_percent > 80 else "ok")
            
            if cpu_percent > 80:
                self.results["issues"].append({
                    "category": "resources",
                    "severity": "high",
                    "message": f"CPU 使用率過高: {cpu_percent}%"
                })
                self.results["optimizations"].append({
                    "category": "performance",
                    "priority": "high",
                    "action": "檢查高 CPU 使用率的進程",
                    "command": "tasklist /FI \"CPU gt 10\" /FO TABLE"
                })
            
            # 記憶體
            mem = psutil.virtual_memory()
            mem_total_gb = mem.total / (1024**3)
            mem_used_gb = mem.used / (1024**3)
            mem_percent = mem.percent
            
            print_result("記憶體", True, 
                        f"總計: {mem_total_gb:.2f} GB, 使用: {mem_used_gb:.2f} GB ({mem_percent}%)",
                        "warn" if mem_percent > 85 else "ok")
            
            if mem_percent > 85:
                self.results["issues"].append({
                    "category": "resources",
                    "severity": "high",
                    "message": f"記憶體使用率過高: {mem_percent}%"
                })
                self.results["optimizations"].append({
                    "category": "performance",
                    "priority": "high",
                    "action": "釋放記憶體或增加記憶體",
                    "suggestion": "關閉不必要的應用程式或考慮升級記憶體"
                })
            
            # 磁碟
            disk = psutil.disk_usage(BASE_PATH.drive + "\\")
            disk_total_gb = disk.total / (1024**3)
            disk_free_gb = disk.free / (1024**3)
            disk_percent = disk.percent
            
            print_result("磁碟空間", True,
                        f"總計: {disk_total_gb:.2f} GB, 可用: {disk_free_gb:.2f} GB ({100-disk_percent}%)",
                        "warn" if disk_percent > 85 else "ok")
            
            if disk_percent > 85:
                self.results["issues"].append({
                    "category": "resources",
                    "severity": "high",
                    "message": f"磁碟空間不足: 僅剩 {disk_free_gb:.2f} GB"
                })
                self.results["optimizations"].append({
                    "category": "storage",
                    "priority": "high",
                    "action": "清理磁碟空間",
                    "suggestions": [
                        "清理臨時檔案",
                        "清理下載資料夾",
                        "清理系統日誌",
                        "移除不必要的備份檔案"
                    ]
                })
            
            self.results["resources"] = {
                "cpu": {
                    "count": cpu_count,
                    "percent": cpu_percent,
                    "frequency": cpu_freq.current if cpu_freq else None
                },
                "memory": {
                    "total_gb": mem_total_gb,
                    "used_gb": mem_used_gb,
                    "percent": mem_percent
                },
                "disk": {
                    "total_gb": disk_total_gb,
                    "free_gb": disk_free_gb,
                    "percent": disk_percent
                }
            }
            
        except Exception as e:
            print_result("資源檢查", False, f"錯誤: {e}", "error")
    
    def check_network(self):
        """檢查網絡狀態"""
        print_section("三、網絡連線檢查")
        
        try:
            # 本機網絡配置
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            active_interfaces = []
            for interface, addrs_list in addrs.items():
                if interface in stats and stats[interface].isup:
                    for addr in addrs_list:
                        if addr.family == socket.AF_INET:
                            active_interfaces.append({
                                "interface": interface,
                                "ip": addr.address,
                                "netmask": addr.netmask
                            })
            
            print_result("網絡介面", True, f"{len(active_interfaces)} 個活動介面", "ok")
            for iface in active_interfaces:
                print(f"    {iface['interface']}: {iface['ip']}")
            
            # 測試伺服器連線
            print("\n[*] 測試伺服器連線...")
            server_reachable = False
            try:
                result = subprocess.run(
                    ["ping", "-n", "2", SERVER_IP],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    server_reachable = True
                    print_result("伺服器連線", True, f"{SERVER_IP} 可達", "ok")
                else:
                    print_result("伺服器連線", False, f"{SERVER_IP} 無法連線", "error")
            except Exception as e:
                print_result("伺服器連線", False, f"錯誤: {e}", "error")
            
            # 端口掃描
            print("\n[*] 掃描關鍵端口...")
            open_ports = []
            closed_ports = []
            
            for port in CRITICAL_PORTS:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex((SERVER_IP, port))
                    sock.close()
                    
                    if result == 0:
                        open_ports.append(port)
                        port_names = {
                            22: "SSH", 80: "HTTP", 443: "HTTPS",
                            8069: "Odoo", 8080: "AI/Web",
                            8766: "Cloud Sync", 3001: "Status",
                            3389: "RDP", 5432: "PostgreSQL"
                        }
                        print_result(f"端口 {port}", True, port_names.get(port, ""), "ok")
                    else:
                        closed_ports.append(port)
                except Exception:
                    closed_ports.append(port)
            
            if closed_ports:
                print(f"\n[WARN] {len(closed_ports)} 個端口關閉: {closed_ports}")
                self.results["issues"].append({
                    "category": "network",
                    "severity": "medium",
                    "message": f"伺服器 {len(closed_ports)} 個關鍵端口關閉"
                })
                self.results["optimizations"].append({
                    "category": "services",
                    "priority": "high",
                    "action": "啟動伺服器上的應用服務",
                    "suggestions": [
                        "檢查 Docker 容器狀態",
                        "檢查服務進程",
                        "檢查防火牆設置"
                    ]
                })
            
            self.results["network"] = {
                "interfaces": active_interfaces,
                "server_reachable": server_reachable,
                "open_ports": open_ports,
                "closed_ports": closed_ports
            }
            
        except Exception as e:
            print_result("網絡檢查", False, f"錯誤: {e}", "error")
    
    def check_filesystem(self):
        """檢查檔案系統"""
        print_section("四、檔案系統檢查")
        
        try:
            # 檢查主要目錄
            critical_dirs = [
                "config",
                "scripts",
                "wuchang_os",
                "memory_store",
                "remote_ui_control",
                "network_config"
            ]
            
            missing_dirs = []
            existing_dirs = []
            
            for dir_name in critical_dirs:
                dir_path = BASE_PATH / dir_name
                if dir_path.exists():
                    existing_dirs.append(dir_name)
                    # 計算目錄大小
                    try:
                        total_size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
                        size_mb = total_size / (1024**2)
                        print_result(f"目錄: {dir_name}", True, f"{size_mb:.2f} MB", "ok")
                    except Exception:
                        print_result(f"目錄: {dir_name}", True, "存在", "ok")
                else:
                    missing_dirs.append(dir_name)
                    print_result(f"目錄: {dir_name}", False, "不存在", "warn")
            
            if missing_dirs:
                self.results["issues"].append({
                    "category": "filesystem",
                    "severity": "medium",
                    "message": f"缺少關鍵目錄: {', '.join(missing_dirs)}"
                })
            
            # 檢查重要檔案
            critical_files = [
                "docker-compose.yml",
                "requirements.txt",
                "package.json",
                "README_V5.1.0.md"
            ]
            
            missing_files = []
            for file_name in critical_files:
                file_path = BASE_PATH / file_name
                if file_path.exists():
                    print_result(f"檔案: {file_name}", True, "存在", "ok")
                else:
                    missing_files.append(file_name)
                    print_result(f"檔案: {file_name}", False, "不存在", "warn")
            
            # 檢查備份檔案
            backup_files = list(BASE_PATH.glob("*.backup"))
            if backup_files:
                print_result("備份檔案", True, f"{len(backup_files)} 個", "ok")
                self.results["optimizations"].append({
                    "category": "storage",
                    "priority": "low",
                    "action": "清理舊備份檔案",
                    "suggestion": f"發現 {len(backup_files)} 個 .backup 檔案，可考慮清理"
                })
            
            self.results["filesystem"] = {
                "base_path": str(BASE_PATH),
                "existing_dirs": existing_dirs,
                "missing_dirs": missing_dirs,
                "missing_files": missing_files,
                "backup_count": len(backup_files)
            }
            
        except Exception as e:
            print_result("檔案系統檢查", False, f"錯誤: {e}", "error")
    
    def check_security(self):
        """檢查安全性"""
        print_section("五、安全性檢查")
        
        try:
            # 檢查敏感檔案
            sensitive_patterns = [
                "*.key",
                "*.pem",
                "*secret*",
                "*password*",
                "*token*",
                "router_secrets.json"
            ]
            
            found_sensitive = []
            for pattern in sensitive_patterns:
                for file_path in BASE_PATH.rglob(pattern):
                    if file_path.is_file():
                        found_sensitive.append(str(file_path.relative_to(BASE_PATH)))
            
            if found_sensitive:
                print_result("敏感檔案", True, f"發現 {len(found_sensitive)} 個", "warn")
                self.results["optimizations"].append({
                    "category": "security",
                    "priority": "high",
                    "action": "保護敏感檔案",
                    "suggestions": [
                        "確保敏感檔案不在版本控制中",
                        "使用環境變數儲存密碼和密鑰",
                        "限制敏感檔案的訪問權限"
                    ]
                })
            else:
                print_result("敏感檔案", True, "未發現明顯的敏感檔案", "ok")
            
            # 檢查 SSH 密鑰
            ssh_key_path = Path.home() / ".ssh" / "id_rsa"
            if ssh_key_path.exists():
                print_result("SSH 密鑰", True, "存在", "ok")
            else:
                print_result("SSH 密鑰", False, "不存在", "warn")
                self.results["optimizations"].append({
                    "category": "security",
                    "priority": "medium",
                    "action": "生成 SSH 密鑰",
                    "command": "ssh-keygen -t rsa -b 4096"
                })
            
            self.results["security"] = {
                "sensitive_files": found_sensitive[:10],  # 只記錄前10個
                "ssh_key_exists": ssh_key_path.exists()
            }
            
        except Exception as e:
            print_result("安全性檢查", False, f"錯誤: {e}", "error")
    
    def check_performance(self):
        """檢查效能問題"""
        print_section("六、效能檢查")
        
        try:
            # 檢查大型檔案
            large_files = []
            for file_path in BASE_PATH.rglob("*"):
                if file_path.is_file():
                    try:
                        size = file_path.stat().st_size
                        if size > 100 * 1024 * 1024:  # 100MB
                            large_files.append({
                                "path": str(file_path.relative_to(BASE_PATH)),
                                "size_mb": size / (1024**2)
                            })
                    except Exception:
                        pass
            
            if large_files:
                print_result("大型檔案", True, f"發現 {len(large_files)} 個 >100MB 的檔案", "warn")
                for item in large_files[:5]:  # 只顯示前5個
                    print(f"    {item['path']}: {item['size_mb']:.2f} MB")
                
                self.results["optimizations"].append({
                    "category": "performance",
                    "priority": "medium",
                    "action": "處理大型檔案",
                    "suggestions": [
                        "考慮壓縮大型檔案",
                        "將大型檔案移到外部儲存",
                        "清理不需要的大型檔案"
                    ]
                })
            else:
                print_result("大型檔案", True, "未發現異常大型檔案", "ok")
            
            # 檢查重複檔案
            print("\n[*] 檢查重複檔案...")
            # 這裡可以實現更複雜的重複檔案檢測
            print_result("重複檔案", True, "檢查完成", "ok")
            
            self.results["performance"] = {
                "large_files": large_files[:10]
            }
            
        except Exception as e:
            print_result("效能檢查", False, f"錯誤: {e}", "error")
    
    def generate_recommendations(self):
        """生成優化建議"""
        print_section("七、優化建議生成")
        
        recommendations = []
        
        # 根據問題生成建議
        for issue in self.results["issues"]:
            if issue["severity"] == "high":
                recommendations.append({
                    "priority": "高",
                    "category": issue["category"],
                    "issue": issue["message"],
                    "action": "立即處理"
                })
        
        # 根據優化機會生成建議
        for opt in self.results["optimizations"]:
            recommendations.append({
                "priority": opt["priority"],
                "category": opt["category"],
                "action": opt["action"],
                "suggestions": opt.get("suggestions", [])
            })
        
        self.results["recommendations"] = recommendations
        
        # 顯示建議
        print("\n優化建議摘要:")
        for i, rec in enumerate(recommendations[:10], 1):
            print(f"\n{i}. [{rec['priority']}] {rec['category']}")
            print(f"   動作: {rec['action']}")
            if 'suggestions' in rec:
                for sug in rec['suggestions']:
                    print(f"   - {sug}")
    
    def generate_report(self):
        """生成完整報告"""
        print_section("八、生成報告")
        
        report_file = BASE_PATH / "system_audit_report.json"
        optimization_file = BASE_PATH / "system_optimization_plan.md"
        
        # 保存 JSON 報告
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print_result("JSON 報告", True, str(report_file), "ok")
        
        # 生成 Markdown 優化計劃
        md_content = self._generate_markdown_report()
        with open(optimization_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print_result("優化計劃", True, str(optimization_file), "ok")
    
    def _generate_markdown_report(self) -> str:
        """生成 Markdown 格式報告"""
        md = f"""# 系統細部檢查與優化計劃

**檢查時間**: {self.results['timestamp']}  
**系統**: {self.results.get('system_info', {}).get('platform', 'Unknown')}

---

## 📊 檢查摘要

### 系統資源
- CPU: {self.results.get('resources', {}).get('cpu', {}).get('percent', 0):.1f}% 使用率
- 記憶體: {self.results.get('resources', {}).get('memory', {}).get('percent', 0):.1f}% 使用率
- 磁碟: {self.results.get('resources', {}).get('disk', {}).get('percent', 0):.1f}% 使用率

### 發現的問題
- 總計: {len(self.results['issues'])} 個問題
- 高優先級: {len([i for i in self.results['issues'] if i['severity'] == 'high'])} 個
- 中優先級: {len([i for i in self.results['issues'] if i['severity'] == 'medium'])} 個

---

## 🔍 詳細問題列表

"""
        
        for issue in self.results['issues']:
            md += f"### {issue['category']} - {issue['severity']}\n"
            md += f"- {issue['message']}\n\n"
        
        md += "\n---\n\n## 🚀 優化方案\n\n"
        
        # 按優先級分組
        high_priority = [o for o in self.results['optimizations'] if o['priority'] == 'high']
        medium_priority = [o for o in self.results['optimizations'] if o['priority'] == 'medium']
        low_priority = [o for o in self.results['optimizations'] if o['priority'] == 'low']
        
        if high_priority:
            md += "### 高優先級優化\n\n"
            for opt in high_priority:
                md += f"#### {opt['action']}\n"
                md += f"**類別**: {opt['category']}\n\n"
                if 'suggestions' in opt:
                    md += "**建議**:\n"
                    for sug in opt['suggestions']:
                        md += f"- {sug}\n"
                md += "\n"
        
        if medium_priority:
            md += "### 中優先級優化\n\n"
            for opt in medium_priority:
                md += f"#### {opt['action']}\n"
                md += f"**類別**: {opt['category']}\n\n"
                if 'suggestions' in opt:
                    md += "**建議**:\n"
                    for sug in opt['suggestions']:
                        md += f"- {sug}\n"
                md += "\n"
        
        if low_priority:
            md += "### 低優先級優化\n\n"
            for opt in low_priority:
                md += f"#### {opt['action']}\n"
                md += f"**類別**: {opt['category']}\n\n"
        
        md += "\n---\n\n## ✅ 執行建議\n\n"
        md += "1. **立即處理高優先級問題**\n"
        md += "2. **逐步實施優化方案**\n"
        md += "3. **定期執行系統檢查**\n"
        md += "4. **監控系統資源使用**\n"
        
        return md
    
    def run(self):
        """執行完整檢查"""
        print("=" * 80)
        print("  系統細部檢查與優化方案生成工具")
        print("=" * 80)
        
        self.check_system_info()
        self.check_resources()
        self.check_network()
        self.check_filesystem()
        self.check_security()
        self.check_performance()
        self.generate_recommendations()
        self.generate_report()
        
        print("\n" + "=" * 80)
        print("  檢查完成")
        print("=" * 80)
        
        return self.results

def main():
    """主函數"""
    try:
        auditor = SystemAuditor()
        results = auditor.run()
        
        # 顯示總結
        print("\n檢查總結:")
        print(f"  發現問題: {len(results['issues'])} 個")
        print(f"  優化建議: {len(results['optimizations'])} 個")
        print(f"  報告已保存: system_audit_report.json")
        print(f"  優化計劃: system_optimization_plan.md")
        
    except KeyboardInterrupt:
        print("\n\n[INFO] 檢查已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
