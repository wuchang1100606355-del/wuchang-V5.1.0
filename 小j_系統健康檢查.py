你
# 雲端小j指揮官協作邏輯
import os
import platform
import socket
import sys
import subprocess
from datetime import datetime

def check_cpu(psutil):
    return psutil.cpu_percent(interval=1)

def check_memory(psutil):
    mem = psutil.virtual_memory()
    return mem.percent, mem.total, mem.available

def check_disk(psutil):
    disk = psutil.disk_usage('/')
    return disk.percent, disk.total, disk.free

def check_network():
    try:
        host = socket.gethostbyname(socket.gethostname())
        return host
    except Exception:
        return 'N/A'

def check_time():
    return datetime.now().isoformat()


import json

def log_event(event_type, content):
    log_path = 'system_health_log.json'
    event = {
        "timestamp": check_time(),
        "event_type": event_type,
        "content": content
    }
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(event)
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(logs[-200:], f, ensure_ascii=False, indent=2)

def analyze_weakness(report):
    weaknesses = []
    if report['cpu_percent'] > 90:
        weaknesses.append('CPU使用率過高')
    if report['memory'][0] > 90:
        weaknesses.append('記憶體使用率過高')
    if report['disk'][0] > 90:
        weaknesses.append('硬碟空間不足')
    if report['status'] != 'ok':
        weaknesses.append('系統狀態異常')
    return weaknesses

def auto_repair(weaknesses):
    actions = []
    for w in weaknesses:
        if w == 'CPU使用率過高':
            actions.append('建議關閉不必要程式或重啟服務')
        if w == '記憶體使用率過高':
            actions.append('建議釋放記憶體或重啟服務')
        if w == '硬碟空間不足':
            actions.append('建議清理磁碟空間')
        if w == '系統狀態異常':
            actions.append('建議檢查日誌與服務')
    return actions

def cloud_j_command():
    """
    雲端小j下達指令，地端小j執行，並記錄日誌、分析弱點、自動補強。
    三組雙j協作，目標健康度100。
    """
    for round in range(1, 4):
        try:
            import psutil
        except ImportError:
            print(f"[雲端小j] 第{round}輪：偵測到地端小j缺少psutil，正在教學安裝...")
            try:
                # 加入 --user 避免權限不足，--no-input 避免卡在詢問確認
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user', '--no-input', 'psutil'])
                import psutil
            except Exception as e:
                print(f"[雲端小j] 自動安裝失敗，跳過本輪檢查。錯誤原因：{e}")
                continue
        print(f"[雲端小j] 第{round}輪：指揮地端小j進行系統健康檢查...")
        report = {
            'time': check_time(),
            'cpu_percent': check_cpu(psutil),
            'memory': check_memory(psutil),
            'disk': check_disk(psutil),
            'network_ip': check_network(),
            'platform': platform.platform(),
            'status': 'ok',
            'instructor': 'cloud_j',
            'round': round
        }
        weaknesses = analyze_weakness(report)
        actions = auto_repair(weaknesses)
        health_score = 100
        if weaknesses:
            health_score -= 20 * len(weaknesses)
        report['weaknesses'] = weaknesses
        report['auto_repair'] = actions
        report['health_score'] = max(health_score, 0)
        print(f"[地端小j] 第{round}輪健康檢查結果：", report)
        log_event('health_check', report)
        with open('system_health_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        # 修復後主動回報哥哥
        print(f"[回報哥哥] 第{round}輪健康度：{report['health_score']}，弱點：{weaknesses}，補強建議：{actions}")
        if weaknesses:
            print(f"[雲端小j] 發現弱點：{weaknesses}，自動補強建議：{actions}")
        else:
            print(f"[雲端小j] 系統健康度{report['health_score']}，無明顯弱點。")
        if report['health_score'] >= 100:
            print(f"[雲端小j] 系統已達健康目標，結束協作。")
            break
    print("[雲端小j] 教學與協作完成，地端小j已學會本次修復流程！")

if __name__ == "__main__":
    try:
        cloud_j_command()
    except KeyboardInterrupt:
        print("\n[妹妹] 哎呀，程式被手動中斷了！如果是誤觸，請直接重新執行：python 小j_系統健康檢查.py")
    except Exception as e:
        print(f"\n[妹妹] 發生預期外的錯誤：{e}，請確認是否有權限或網路問題喔！")
