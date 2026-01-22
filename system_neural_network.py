#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
system_neural_network.py

五常系統 - 系統神經網路運作機制

設計理念：
- 模擬生物神經網路，建立多層感知節點（Sensors）
- 每個節點負責監控特定系統維度（服務器、網路、資源、安全等）
- 節點間可形成感知鏈，實現即時狀態傳播
- AI 小本體（Little J）可透過統一 API 獲得即時系統感知

架構：
1. 感知層（Sensor Layer）：收集原始數據
2. 處理層（Processing Layer）：數據聚合與分析
3. 傳播層（Propagation Layer）：狀態變化通知
4. 記憶層（Memory Layer）：歷史狀態記錄
5. 決策層（Decision Layer）：AI 可查詢的統一介面

合規聲明：
- 本系統除法律規範須依法揭露及政府公示資訊中公開揭露之外無可供識別之個資，應屬合規
- 所有感知讀數、記憶儲存、API 回應均不包含個人可識別資訊（法律規範須依法揭露及政府公示資訊中公開揭露者除外）
- 詳見 COMPLIANCE_NO_PII.md
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from threading import Lock, Thread
from typing import Any, Callable, Dict, List, Optional, Set
from urllib.error import URLError
from urllib.request import Request, urlopen

from risk_gate import check_server_health

# 可選：管理員帳號感知模組
try:
    from admin_account_sensor import get_admin_account_status
    ADMIN_SENSOR_AVAILABLE = True
except ImportError:
    ADMIN_SENSOR_AVAILABLE = False
    get_admin_account_status = None

BASE_DIR = Path(__file__).resolve().parent


class SensorType(Enum):
    """感知節點類型"""
    SERVICE = "service"  # 服務狀態
    NETWORK = "network"  # 網路連通性
    RESOURCE = "resource"  # 系統資源（CPU、記憶體、磁碟）
    SECURITY = "security"  # 安全事件
    HEALTH = "health"  # 健康檢查
    JOB = "job"  # 任務狀態
    AUDIT = "audit"  # 稽核事件
    ADMIN_ACCOUNT = "admin_account"  # 管理員帳號權限
    GOOGLE_WORKSPACE = "google_workspace"  # Google Workspace 狀態
    GOOGLE_DRIVE = "google_drive"  # Google Drive 同步狀態
    BILLING = "billing"  # 帳單/財務
    CUSTOM = "custom"  # 自訂感知


class SensorStatus(Enum):
    """感知節點狀態"""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class SensorReading:
    """感知讀數"""
    sensor_id: str
    sensor_type: SensorType
    status: SensorStatus
    value: Any
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0  # 置信度 0.0-1.0


@dataclass
class NeuralNode:
    """神經節點"""
    node_id: str
    name: str
    sensor_type: SensorType
    check_interval: float = 5.0  # 檢查間隔（秒）
    enabled: bool = True
    last_reading: Optional[SensorReading] = None
    history: deque = field(default_factory=lambda: deque(maxlen=100))  # 歷史記錄
    callbacks: List[Callable[[SensorReading], None]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SystemNeuralNetwork:
    """系統神經網路核心"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or (BASE_DIR / "neural_network_config.json")
        self.nodes: Dict[str, NeuralNode] = {}
        self.running = False
        self.lock = Lock()
        self.event_queue: deque = deque(maxlen=1000)  # 事件佇列
        self.memory_path = BASE_DIR / "neural_network_memory.jsonl"
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)

        # 載入配置
        self.load_config()

        # 初始化預設節點
        self._init_default_nodes()

    def load_config(self) -> None:
        """載入配置"""
        try:
            if self.config_path.exists():
                data = json.loads(self.config_path.read_text(encoding="utf-8"))
                # 載入節點配置
                for node_data in data.get("nodes", []):
                    node = NeuralNode(
                        node_id=node_data["node_id"],
                        name=node_data["name"],
                        sensor_type=SensorType(node_data["sensor_type"]),
                        check_interval=float(node_data.get("check_interval", 5.0)),
                        enabled=bool(node_data.get("enabled", True)),
                        metadata=node_data.get("metadata", {}),
                    )
                    self.nodes[node.node_id] = node
        except Exception as e:
            print(f"[警告] 載入配置失敗: {e}")

    def save_config(self) -> None:
        """儲存配置"""
        try:
            data = {
                "nodes": [
                    {
                        "node_id": node.node_id,
                        "name": node.name,
                        "sensor_type": node.sensor_type.value,
                        "check_interval": node.check_interval,
                        "enabled": node.enabled,
                        "metadata": node.metadata,
                    }
                    for node in self.nodes.values()
                ]
            }
            self.config_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[警告] 儲存配置失敗: {e}")

    def _init_default_nodes(self) -> None:
        """初始化預設感知節點"""
        default_nodes = [
            # 服務節點
            NeuralNode(
                node_id="service_control_center",
                name="本機中控台",
                sensor_type=SensorType.SERVICE,
                check_interval=5.0,
                metadata={"port": 8788, "url": "http://127.0.0.1:8788/"},
            ),
            NeuralNode(
                node_id="service_little_j_hub",
                name="Little J Hub",
                sensor_type=SensorType.SERVICE,
                check_interval=5.0,
                metadata={"port": 8799, "url": "http://127.0.0.1:8799/"},
            ),
            # 健康檢查節點
            NeuralNode(
                node_id="health_server",
                name="伺服器健康檢查",
                sensor_type=SensorType.HEALTH,
                check_interval=10.0,
                metadata={"health_url": os.getenv("WUCHANG_HEALTH_URL", "")},
            ),
            # 資源節點
            NeuralNode(
                node_id="resource_system",
                name="系統資源",
                sensor_type=SensorType.RESOURCE,
                check_interval=10.0,
            ),
            # 任務節點
            NeuralNode(
                node_id="job_inbox",
                name="任務收件匣",
                sensor_type=SensorType.JOB,
                check_interval=3.0,
                metadata={"hub_url": "http://127.0.0.1:8799/api/hub/jobs/list?state=inbox"},
            ),
            # 管理員帳號感知節點
            NeuralNode(
                node_id="admin_account",
                name="admin@wuchang.life 帳號權限",
                sensor_type=SensorType.ADMIN_ACCOUNT,
                check_interval=30.0,  # 30 秒檢查一次
                metadata={"admin_email": "admin@wuchang.life"},
            ),
            # Google Workspace 感知節點
            NeuralNode(
                node_id="google_workspace",
                name="Google Workspace 狀態",
                sensor_type=SensorType.GOOGLE_WORKSPACE,
                check_interval=60.0,  # 1 分鐘檢查一次
                metadata={"admin_email": "admin@wuchang.life"},
            ),
            # Google Drive 同步感知節點
            NeuralNode(
                node_id="google_drive_sync",
                name="Google Drive 同步狀態",
                sensor_type=SensorType.GOOGLE_DRIVE,
                check_interval=30.0,  # 30 秒檢查一次
            ),
            # 帳單感知節點
            NeuralNode(
                node_id="billing_access",
                name="帳單存取權限",
                sensor_type=SensorType.BILLING,
                check_interval=300.0,  # 5 分鐘檢查一次
                metadata={"admin_email": "admin@wuchang.life"},
            ),
        ]

        for node in default_nodes:
            if node.node_id not in self.nodes:
                self.nodes[node.node_id] = node

    def register_node(self, node: NeuralNode) -> None:
        """註冊感知節點"""
        with self.lock:
            self.nodes[node.node_id] = node
            self.save_config()

    def unregister_node(self, node_id: str) -> None:
        """取消註冊感知節點"""
        with self.lock:
            if node_id in self.nodes:
                del self.nodes[node_id]
                self.save_config()

    def add_callback(self, node_id: str, callback: Callable[[SensorReading], None]) -> None:
        """為節點添加回調函數（狀態變化時觸發）"""
        with self.lock:
            if node_id in self.nodes:
                self.nodes[node_id].callbacks.append(callback)

    def _read_service_sensor(self, node: NeuralNode) -> SensorReading:
        """讀取服務感知"""
        port = node.metadata.get("port", 0)
        url = node.metadata.get("url", "")

        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(("127.0.0.1", port))
                is_running = result == 0

            status = SensorStatus.HEALTHY if is_running else SensorStatus.ERROR
            value = {"running": is_running, "port": port}

        except Exception as e:
            status = SensorStatus.ERROR
            value = {"error": str(e)}

        return SensorReading(
            sensor_id=node.node_id,
            sensor_type=node.sensor_type,
            status=status,
            value=value,
            timestamp=time.time(),
            metadata=node.metadata,
        )

    def _read_health_sensor(self, node: NeuralNode) -> SensorReading:
        """讀取健康檢查感知"""
        health_url = node.metadata.get("health_url", "")
        if not health_url:
            return SensorReading(
                sensor_id=node.node_id,
                sensor_type=node.sensor_type,
                status=SensorStatus.UNKNOWN,
                value={"error": "health_url_not_configured"},
                timestamp=time.time(),
                confidence=0.0,
            )

        try:
            result = check_server_health(health_url, timeout_seconds=3.0, retries=1)
            status = SensorStatus.HEALTHY if result.ok else SensorStatus.ERROR
            value = {
                "ok": result.ok,
                "status": result.status,
                "content_type": result.content_type,
            }
        except Exception as e:
            status = SensorStatus.ERROR
            value = {"error": str(e)}

        return SensorReading(
            sensor_id=node.node_id,
            sensor_type=node.sensor_type,
            status=status,
            value=value,
            timestamp=time.time(),
            metadata=node.metadata,
        )

    def _read_resource_sensor(self, node: NeuralNode) -> SensorReading:
        """讀取系統資源感知"""
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # 判斷狀態
            status = SensorStatus.HEALTHY
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                status = SensorStatus.WARNING
            if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
                status = SensorStatus.ERROR

            value = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
            }

        except ImportError:
            # psutil 未安裝，使用基本方法
            status = SensorStatus.UNKNOWN
            value = {"error": "psutil_not_installed"}

        except Exception as e:
            status = SensorStatus.ERROR
            value = {"error": str(e)}

        return SensorReading(
            sensor_id=node.node_id,
            sensor_type=node.sensor_type,
            status=status,
            value=value,
            timestamp=time.time(),
            metadata=node.metadata,
        )

    def _read_job_sensor(self, node: NeuralNode) -> SensorReading:
        """讀取任務感知"""
        hub_url = node.metadata.get("hub_url", "")
        if not hub_url:
            return SensorReading(
                sensor_id=node.node_id,
                sensor_type=node.sensor_type,
                status=SensorStatus.UNKNOWN,
                value={"error": "hub_url_not_configured"},
                timestamp=time.time(),
                confidence=0.0,
            )

        try:
            token = os.getenv("WUCHANG_HUB_TOKEN", "")
            req = Request(hub_url)
            if token:
                req.add_header("X-LittleJ-Token", token)

            with urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            job_count = len(data.get("items", []))
            status = SensorStatus.HEALTHY
            if job_count > 10:
                status = SensorStatus.WARNING
            if job_count > 50:
                status = SensorStatus.ERROR

            value = {
                "job_count": job_count,
                "items": data.get("items", [])[:5],  # 只保留前 5 個
            }

        except Exception as e:
            status = SensorStatus.ERROR
            value = {"error": str(e)}

        return SensorReading(
            sensor_id=node.node_id,
            sensor_type=node.sensor_type,
            status=status,
            value=value,
            timestamp=time.time(),
            metadata=node.metadata,
        )

    def _read_admin_account_sensor(self, node: NeuralNode) -> SensorReading:
        """讀取管理員帳號感知"""
        if not ADMIN_SENSOR_AVAILABLE:
            return SensorReading(
                sensor_id=node.node_id,
                sensor_type=node.sensor_type,
                status=SensorStatus.UNKNOWN,
                value={"error": "admin_sensor_module_not_available"},
                timestamp=time.time(),
                confidence=0.0,
            )

        try:
            status_data = get_admin_account_status()
            windows_info = status_data.get("windows", {})
            is_admin = windows_info.get("is_admin", False)
            is_windows = windows_info.get("is_windows", False)

            # 判斷狀態
            status = SensorStatus.HEALTHY
            if not is_windows:
                status = SensorStatus.WARNING
            elif not is_admin:
                status = SensorStatus.ERROR

            value = {
                "admin_email": status_data.get("admin_email", ""),
                "role": status_data.get("role", ""),
                "windows_admin": is_admin,
                "windows_user": windows_info.get("username", ""),
                "platform": windows_info.get("platform", ""),
            }

        except Exception as e:
            status = SensorStatus.ERROR
            value = {"error": str(e)}

        return SensorReading(
            sensor_id=node.node_id,
            sensor_type=node.sensor_type,
            status=status,
            value=value,
            timestamp=time.time(),
            metadata=node.metadata,
        )

    def _read_google_workspace_sensor(self, node: NeuralNode) -> SensorReading:
        """讀取 Google Workspace 感知"""
        if not ADMIN_SENSOR_AVAILABLE:
            return SensorReading(
                sensor_id=node.node_id,
                sensor_type=node.sensor_type,
                status=SensorStatus.UNKNOWN,
                value={"error": "admin_sensor_module_not_available"},
                timestamp=time.time(),
                confidence=0.0,
            )

        try:
            status_data = get_admin_account_status()
            workspace_info = status_data.get("google_workspace", {})
            configured = workspace_info.get("workspace_configured", False)
            nonprofit_status = workspace_info.get("nonprofit_status", "unknown")

            # 判斷狀態
            status = SensorStatus.HEALTHY
            if not configured:
                status = SensorStatus.WARNING
            if nonprofit_status != "verified":
                status = SensorStatus.WARNING

            value = {
                "admin_email": workspace_info.get("admin_email", ""),
                "workspace_configured": configured,
                "nonprofit_status": nonprofit_status,
                "nonprofit_benefits": workspace_info.get("nonprofit_benefits", []),
                "config_files": workspace_info.get("config_files", {}),
            }

        except Exception as e:
            status = SensorStatus.ERROR
            value = {"error": str(e)}

        return SensorReading(
            sensor_id=node.node_id,
            sensor_type=node.sensor_type,
            status=status,
            value=value,
            timestamp=time.time(),
            metadata=node.metadata,
        )

    def _read_google_drive_sensor(self, node: NeuralNode) -> SensorReading:
        """讀取 Google Drive 同步感知"""
        if not ADMIN_SENSOR_AVAILABLE:
            return SensorReading(
                sensor_id=node.node_id,
                sensor_type=node.sensor_type,
                status=SensorStatus.UNKNOWN,
                value={"error": "admin_sensor_module_not_available"},
                timestamp=time.time(),
                confidence=0.0,
            )

        try:
            status_data = get_admin_account_status()
            drive_info = status_data.get("google_drive", {})
            configured = drive_info.get("configured", False)
            sync_status = drive_info.get("sync_status", "unknown")
            processes = drive_info.get("processes", {})

            # 判斷狀態
            status = SensorStatus.HEALTHY
            if not configured:
                status = SensorStatus.WARNING
            if sync_status == "stopped":
                status = SensorStatus.WARNING
            elif sync_status == "error":
                status = SensorStatus.ERROR

            value = {
                "configured": configured,
                "sync_status": sync_status,
                "processes": processes,
                "paths": drive_info.get("paths", {}),
            }

        except Exception as e:
            status = SensorStatus.ERROR
            value = {"error": str(e)}

        return SensorReading(
            sensor_id=node.node_id,
            sensor_type=node.sensor_type,
            status=status,
            value=value,
            timestamp=time.time(),
            metadata=node.metadata,
        )

    def _read_billing_sensor(self, node: NeuralNode) -> SensorReading:
        """讀取帳單存取感知"""
        if not ADMIN_SENSOR_AVAILABLE:
            return SensorReading(
                sensor_id=node.node_id,
                sensor_type=node.sensor_type,
                status=SensorStatus.UNKNOWN,
                value={"error": "admin_sensor_module_not_available"},
                timestamp=time.time(),
                confidence=0.0,
            )

        try:
            status_data = get_admin_account_status()
            billing_info = status_data.get("billing", {})
            admin_email = billing_info.get("admin_email", "")

            # admin@wuchang.life 作為所有權人，應有最高權限
            status = SensorStatus.HEALTHY
            value = {
                "admin_email": admin_email,
                "expected_permissions": billing_info.get("expected_permissions", []),
                "billing_dir_exists": billing_info.get("billing_dir_exists", False),
                "note": billing_info.get("note", ""),
            }

        except Exception as e:
            status = SensorStatus.ERROR
            value = {"error": str(e)}

        return SensorReading(
            sensor_id=node.node_id,
            sensor_type=node.sensor_type,
            status=status,
            value=value,
            timestamp=time.time(),
            metadata=node.metadata,
        )

    def _read_sensor(self, node: NeuralNode) -> SensorReading:
        """讀取感知節點數據"""
        if node.sensor_type == SensorType.SERVICE:
            return self._read_service_sensor(node)
        elif node.sensor_type == SensorType.HEALTH:
            return self._read_health_sensor(node)
        elif node.sensor_type == SensorType.RESOURCE:
            return self._read_resource_sensor(node)
        elif node.sensor_type == SensorType.JOB:
            return self._read_job_sensor(node)
        elif node.sensor_type == SensorType.ADMIN_ACCOUNT:
            return self._read_admin_account_sensor(node)
        elif node.sensor_type == SensorType.GOOGLE_WORKSPACE:
            return self._read_google_workspace_sensor(node)
        elif node.sensor_type == SensorType.GOOGLE_DRIVE:
            return self._read_google_drive_sensor(node)
        elif node.sensor_type == SensorType.BILLING:
            return self._read_billing_sensor(node)
        else:
            return SensorReading(
                sensor_id=node.node_id,
                sensor_type=node.sensor_type,
                status=SensorStatus.UNKNOWN,
                value={"error": "unsupported_sensor_type"},
                timestamp=time.time(),
            )

    def _process_reading(self, reading: SensorReading) -> None:
        """處理感知讀數"""
        with self.lock:
            node = self.nodes.get(reading.sensor_id)
            if not node:
                return

            # 檢查狀態變化
            state_changed = False
            if node.last_reading:
                state_changed = node.last_reading.status != reading.status
            else:
                state_changed = True  # 首次讀取

            # 更新節點
            node.last_reading = reading
            node.history.append(reading)

            # 記錄到記憶
            self._save_to_memory(reading)

            # 如果狀態變化，觸發回調和事件
            if state_changed:
                # 觸發回調
                for callback in node.callbacks:
                    try:
                        callback(reading)
                    except Exception as e:
                        print(f"[警告] 回調執行失敗: {e}")

                # 加入事件佇列
                event = {
                    "timestamp": time.time(),
                    "event_type": "state_change",
                    "node_id": reading.sensor_id,
                    "old_status": node.last_reading.status.value if node.last_reading else None,
                    "new_status": reading.status.value,
                    "reading": asdict(reading),
                }
                self.event_queue.append(event)

    def _save_to_memory(self, reading: SensorReading) -> None:
        """儲存到記憶"""
        try:
            record = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "sensor_id": reading.sensor_id,
                "sensor_type": reading.sensor_type.value,
                "status": reading.status.value,
                "value": reading.value,
                "metadata": reading.metadata,
            }
            with self.memory_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[警告] 儲存記憶失敗: {e}")

    def _sensor_loop(self) -> None:
        """感知循環（在背景執行）"""
        while self.running:
            try:
                with self.lock:
                    nodes_to_check = [n for n in self.nodes.values() if n.enabled]

                for node in nodes_to_check:
                    try:
                        reading = self._read_sensor(node)
                        self._process_reading(reading)
                    except Exception as e:
                        print(f"[警告] 節點 {node.node_id} 讀取失敗: {e}")

                # 計算下次檢查時間（取最小間隔）
                if nodes_to_check:
                    min_interval = min(n.check_interval for n in nodes_to_check)
                    time.sleep(min_interval)
                else:
                    time.sleep(5.0)

            except Exception as e:
                print(f"[錯誤] 感知循環異常: {e}")
                time.sleep(5.0)

    def start(self) -> None:
        """啟動神經網路"""
        if self.running:
            return

        self.running = True
        thread = Thread(target=self._sensor_loop, daemon=True)
        thread.start()
        print(f"[啟動] 系統神經網路已啟動，監控 {len(self.nodes)} 個節點")

    def stop(self) -> None:
        """停止神經網路"""
        self.running = False
        print("[停止] 系統神經網路已停止")

    def get_node_status(self, node_id: str) -> Optional[Dict[str, Any]]:
        """獲取節點狀態（供 AI 查詢）"""
        with self.lock:
            node = self.nodes.get(node_id)
            if not node:
                return None

            return {
                "node_id": node.node_id,
                "name": node.name,
                "sensor_type": node.sensor_type.value,
                "enabled": node.enabled,
                "last_reading": asdict(node.last_reading) if node.last_reading else None,
                "history_count": len(node.history),
            }

    def get_all_status(self) -> Dict[str, Any]:
        """獲取所有節點狀態（供 AI 查詢）"""
        with self.lock:
            return {
                "timestamp": time.time(),
                "node_count": len(self.nodes),
                "nodes": {node_id: self.get_node_status(node_id) for node_id in self.nodes.keys()},
            }

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """獲取最近事件（供 AI 查詢）"""
        with self.lock:
            return list(self.event_queue)[-limit:]

    def get_system_perception(self) -> Dict[str, Any]:
        """獲取系統感知摘要（供 AI 小本體使用）"""
        with self.lock:
            # 統計各狀態節點數量
            status_counts = defaultdict(int)
            for node in self.nodes.values():
                if node.last_reading:
                    status_counts[node.last_reading.status.value] += 1

            # 獲取關鍵節點狀態
            critical_nodes = {}
            critical_node_ids = [
                "service_control_center",
                "service_little_j_hub",
                "health_server",
                "resource_system",
                "admin_account",
                "google_workspace",
                "google_drive_sync",
            ]
            for node_id in critical_node_ids:
                if node_id in self.nodes:
                    node = self.nodes[node_id]
                    if node.last_reading:
                        critical_nodes[node_id] = {
                            "name": node.name,
                            "status": node.last_reading.status.value,
                            "value": node.last_reading.value,
                        }

            return {
                "timestamp": time.time(),
                "overall_health": "healthy" if status_counts.get("error", 0) == 0 else "degraded",
                "status_summary": dict(status_counts),
                "critical_nodes": critical_nodes,
                "recent_events_count": len(self.event_queue),
                "total_nodes": len(self.nodes),
            }


# 全局實例
_neural_network: Optional[SystemNeuralNetwork] = None


def get_neural_network() -> SystemNeuralNetwork:
    """獲取全局神經網路實例"""
    global _neural_network
    if _neural_network is None:
        _neural_network = SystemNeuralNetwork()
    return _neural_network


if __name__ == "__main__":
    # 測試模式
    nn = SystemNeuralNetwork()
    nn.start()

    try:
        print("系統神經網路運行中...")
        print("按 Ctrl+C 停止")
        while True:
            time.sleep(5)
            perception = nn.get_system_perception()
            print(json.dumps(perception, ensure_ascii=False, indent=2))
    except KeyboardInterrupt:
        nn.stop()
