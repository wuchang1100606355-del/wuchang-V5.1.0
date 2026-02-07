#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
accountable_person_authorization_api.py

可究責自然人個資使用授權 API

提供 HTTP API 端點用於管理可究責自然人的個資使用授權。

合規聲明：
- 本系統及AI程序設計之可究責自然人不在隱私權保護規範內
- 本系統經授權之獨立管理權限自然人不在隱私權保護規範內
- 此兩種自然人除姓名外其餘不得公開揭露，但須紀錄於本系統之硬編碼
- 個資使用需獲得明確授權
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler
from http import HTTPStatus
from urllib.parse import urlparse, parse_qs

from authorized_administrators import (
    grant_authorization,
    revoke_authorization,
    get_authorization,
    get_authorization_summary,
    get_all_valid_authorizations,
    check_authorization,
    validate_authorizations,
)


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    """發送 JSON 回應"""
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.end_headers()
    handler.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))


def _read_json(handler: BaseHTTPRequestHandler) -> dict:
    """讀取 JSON 請求體"""
    content_length = int(handler.headers.get("Content-Length", 0))
    if content_length == 0:
        return {}
    body = handler.rfile.read(content_length).decode("utf-8")
    try:
        return json.loads(body)
    except Exception:
        return {}


class AuthorizationAPIHandler(BaseHTTPRequestHandler):
    """可究責自然人個資使用授權 API 處理器"""
    
    def do_GET(self) -> None:
        """處理 GET 請求"""
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        
        # GET /api/accountable/authorization?person_name=姓名
        if parsed.path == "/api/accountable/authorization":
            person_name = (qs.get("person_name") or [""])[0].strip()
            if not person_name:
                _json_response(self, HTTPStatus.BAD_REQUEST, {
                    "ok": False,
                    "error": "missing_person_name",
                })
                return
            
            summary = get_authorization_summary(person_name)
            _json_response(self, HTTPStatus.OK, {
                "ok": True,
                "authorization": summary,
            })
            return
        
        # GET /api/accountable/authorizations
        if parsed.path == "/api/accountable/authorizations":
            authorizations = get_all_valid_authorizations()
            summaries = [get_authorization_summary(auth.person_name) for auth in authorizations]
            _json_response(self, HTTPStatus.OK, {
                "ok": True,
                "authorizations": summaries,
                "count": len(summaries),
            })
            return
        
        # GET /api/accountable/authorization/validate
        if parsed.path == "/api/accountable/authorization/validate":
            validation = validate_authorizations()
            _json_response(self, HTTPStatus.OK, {
                "ok": True,
                "validation": validation,
            })
            return
        
        _json_response(self, HTTPStatus.NOT_FOUND, {
            "ok": False,
            "error": "not_found",
        })
    
    def do_POST(self) -> None:
        """處理 POST 請求"""
        parsed = urlparse(self.path)
        data = _read_json(self)
        
        # POST /api/accountable/authorization/grant
        if parsed.path == "/api/accountable/authorization/grant":
            person_name = str(data.get("person_name") or "").strip()
            person_type = str(data.get("person_type") or "").strip()
            authorization_scope = str(data.get("authorization_scope") or "").strip()
            authorized_uses = data.get("authorized_uses", [])
            
            if not person_name or not person_type or not authorization_scope:
                _json_response(self, HTTPStatus.BAD_REQUEST, {
                    "ok": False,
                    "error": "missing_required_fields",
                    "required": ["person_name", "person_type", "authorization_scope"],
                })
                return
            
            if not isinstance(authorized_uses, list) or not authorized_uses:
                _json_response(self, HTTPStatus.BAD_REQUEST, {
                    "ok": False,
                    "error": "invalid_authorized_uses",
                })
                return
            
            try:
                auth = grant_authorization(
                    person_name=person_name,
                    person_type=person_type,
                    authorization_scope=authorization_scope,
                    authorized_uses=authorized_uses,
                    expires_at=data.get("expires_at"),
                    granted_by=data.get("granted_by"),
                    notes=data.get("notes"),
                )
                
                _json_response(self, HTTPStatus.OK, {
                    "ok": True,
                    "authorization": get_authorization_summary(auth.person_name),
                })
            except Exception as e:
                _json_response(self, HTTPStatus.INTERNAL_SERVER_ERROR, {
                    "ok": False,
                    "error": str(e),
                })
            return
        
        # POST /api/accountable/authorization/revoke
        if parsed.path == "/api/accountable/authorization/revoke":
            person_name = str(data.get("person_name") or "").strip()
            
            if not person_name:
                _json_response(self, HTTPStatus.BAD_REQUEST, {
                    "ok": False,
                    "error": "missing_person_name",
                })
                return
            
            success = revoke_authorization(person_name)
            if success:
                _json_response(self, HTTPStatus.OK, {
                    "ok": True,
                    "revoked": True,
                    "person_name": person_name,
                })
            else:
                _json_response(self, HTTPStatus.BAD_REQUEST, {
                    "ok": False,
                    "error": "revoke_failed",
                    "message": "授權不存在或已撤銷",
                })
            return
        
        # POST /api/accountable/authorization/check
        if parsed.path == "/api/accountable/authorization/check":
            person_name = str(data.get("person_name") or "").strip()
            use_case = str(data.get("use_case") or "").strip()
            
            if not person_name or not use_case:
                _json_response(self, HTTPStatus.BAD_REQUEST, {
                    "ok": False,
                    "error": "missing_required_fields",
                    "required": ["person_name", "use_case"],
                })
                return
            
            authorized = check_authorization(person_name, use_case)
            _json_response(self, HTTPStatus.OK, {
                "ok": True,
                "person_name": person_name,
                "use_case": use_case,
                "authorized": authorized,
            })
            return
        
        _json_response(self, HTTPStatus.NOT_FOUND, {
            "ok": False,
            "error": "not_found",
        })
    
    def log_message(self, format, *args):
        """覆寫日誌方法，避免輸出到控制台"""
        pass


if __name__ == "__main__":
    from http.server import HTTPServer
    
    server = HTTPServer(("127.0.0.1", 8800), AuthorizationAPIHandler)
    print("可究責自然人個資使用授權 API 服務器啟動於 http://127.0.0.1:8800")
    server.serve_forever()
