#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
neural_network_api.py

系統神經網路 API 端點

提供 HTTP API 供 Little J 查詢系統感知狀態
"""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse

from system_neural_network import get_neural_network


def _json(handler: BaseHTTPRequestHandler, status: int, payload: Dict[str, Any]) -> None:
    """發送 JSON 回應"""
    raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


class NeuralNetworkAPIHandler(BaseHTTPRequestHandler):
    """神經網路 API 處理器"""

    def log_message(self, fmt: str, *args: Any) -> None:
        """禁用日誌"""
        return

    def do_GET(self) -> None:
        """處理 GET 請求"""
        parsed = urlparse(self.path)
        path = parsed.path

        nn = get_neural_network()

        # 確保神經網路已啟動
        if not nn.running:
            nn.start()

        if path == "/api/neural/health":
            _json(self, HTTPStatus.OK, {"ok": True, "running": nn.running})

        elif path == "/api/neural/perception":
            # 獲取系統感知摘要（供 AI 小本體使用）
            perception = nn.get_system_perception()
            _json(self, HTTPStatus.OK, {"ok": True, "perception": perception})

        elif path == "/api/neural/status":
            # 獲取所有節點狀態
            status = nn.get_all_status()
            _json(self, HTTPStatus.OK, {"ok": True, "status": status})

        elif path == "/api/neural/node":
            # 獲取特定節點狀態
            qs = parse_qs(parsed.query)
            node_id = (qs.get("id") or [""])[0].strip()
            if not node_id:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_node_id"})
                return

            node_status = nn.get_node_status(node_id)
            if node_status is None:
                _json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "node_not_found"})
                return

            _json(self, HTTPStatus.OK, {"ok": True, "node": node_status})

        elif path == "/api/neural/events":
            # 獲取最近事件
            qs = parse_qs(parsed.query)
            limit = int((qs.get("limit") or ["50"])[0])
            events = nn.get_recent_events(limit=limit)
            _json(self, HTTPStatus.OK, {"ok": True, "events": events, "count": len(events)})

        else:
            _json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:
        """處理 POST 請求（未來擴展用）"""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/neural/start":
            nn = get_neural_network()
            nn.start()
            _json(self, HTTPStatus.OK, {"ok": True, "message": "neural_network_started"})

        elif path == "/api/neural/stop":
            nn = get_neural_network()
            nn.stop()
            _json(self, HTTPStatus.OK, {"ok": True, "message": "neural_network_stopped"})

        else:
            _json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})


def add_neural_network_routes(handler_class: type, base_path: str = "/api/neural") -> None:
    """
    將神經網路 API 路由添加到現有的 HTTP 處理器

    使用方式：
        from neural_network_api import add_neural_network_routes
        
        class MyHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                # 現有路由處理...
                # 然後添加神經網路路由
                add_neural_network_routes(MyHandler)
    """
    # 這個函數可以通過修改 handler 的 do_GET/do_POST 方法來添加路由
    # 或者返回一個路由處理函數供調用
    pass
