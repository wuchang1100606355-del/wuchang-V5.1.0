"""
demo_security_ack_server.py

「一鍵止鬧 / 已接手」演示用最小服務（可稽核、不可刪除事件）。

目標：
- 任何告警事件一律先落地保存（append-only 稽核檔）
- 「一鍵處置」只做：止鬧/降噪/標記狀態/必填原因/記錄操作者
- 不提供「刪除/隱匿事件」功能（避免破壞稽核與合規）

啟動：
  python demo_security_ack_server.py --port 8799

測試（PowerShell）：
  Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8799/api/security/events -ContentType application/json -Body ('
    {"source":"zhongxing","site_id":"coffee-shop","zone":"Z01","event_type":"alarm","severity":"high","raw_payload":"ALARM Z01"}
  ')

  Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8799/api/security/events/<EVENT_ID>/action -ContentType application/json -Body ('
    {"action":"ack","actor":"店長","reason":"已到現場確認，暫停推播，持續監看"}
  ')

  Invoke-RestMethod -Uri http://127.0.0.1:8799/api/security/events
"""

from __future__ import annotations

import argparse
import json
import os
import time
import uuid
from dataclasses import dataclass, asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse, parse_qs


def _now_iso() -> str:
    # 秒級即可滿足 demo 與稽核
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


def _read_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    try:
        length = int(handler.headers.get("Content-Length") or "0")
    except Exception:
        length = 0
    body = handler.rfile.read(length) if length > 0 else b""
    if not body:
        return {}
    return json.loads(body.decode("utf-8"))


@dataclass
class SecurityEvent:
    id: str
    created_at: str
    source: str
    site_id: str
    zone: str
    event_type: str
    severity: str
    raw_payload: Any | None
    state: str
    last_action_at: str | None = None
    last_action: str | None = None
    last_actor: str | None = None
    last_reason: str | None = None
    snooze_until: str | None = None


class EventStore:
    def __init__(self, audit_path: str) -> None:
        self.audit_path = audit_path
        self.events: dict[str, SecurityEvent] = {}
        self._load_from_audit()

    def _append_audit(self, record: dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(self.audit_path)), exist_ok=True)
        with open(self.audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _load_from_audit(self) -> None:
        if not os.path.exists(self.audit_path):
            return
        try:
            with open(self.audit_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    kind = rec.get("kind")
                    if kind == "event_created":
                        ev = SecurityEvent(**rec["event"])
                        self.events[ev.id] = ev
                    elif kind == "event_action":
                        ev_id = rec.get("event_id")
                        ev = self.events.get(ev_id)
                        if not ev:
                            continue
                        # 重放最後狀態（append-only）
                        ev.state = rec.get("state") or ev.state
                        ev.last_action_at = rec.get("at") or ev.last_action_at
                        ev.last_action = rec.get("action") or ev.last_action
                        ev.last_actor = rec.get("actor") or ev.last_actor
                        ev.last_reason = rec.get("reason") or ev.last_reason
                        ev.snooze_until = rec.get("snooze_until") or ev.snooze_until
        except Exception:
            # demo 工具：不讓壞檔阻斷啟動
            return

    def create_event(self, data: dict[str, Any]) -> SecurityEvent:
        ev = SecurityEvent(
            id=str(uuid.uuid4()),
            created_at=_now_iso(),
            source=str(data.get("source") or "unknown"),
            site_id=str(data.get("site_id") or "unknown"),
            zone=str(data.get("zone") or "unknown"),
            event_type=str(data.get("event_type") or "alarm"),
            severity=str(data.get("severity") or "medium"),
            raw_payload=data.get("raw_payload"),
            state="open",
        )
        self.events[ev.id] = ev
        self._append_audit({"kind": "event_created", "at": ev.created_at, "event": asdict(ev)})
        return ev

    def action_event(self, ev_id: str, action: str, actor: str, reason: str, snooze_seconds: int | None) -> SecurityEvent:
        ev = self.events.get(ev_id)
        if not ev:
            raise KeyError("event_not_found")

        at = _now_iso()
        action = (action or "").strip().lower()
        if action not in {"ack", "snooze", "resolve"}:
            raise ValueError("invalid_action")

        # 狀態機（演示用）
        if action == "ack":
            new_state = "acknowledged"
            snooze_until = None
        elif action == "resolve":
            new_state = "resolved"
            snooze_until = None
        else:
            new_state = "snoozed"
            sec = int(snooze_seconds or 300)
            snooze_until = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(time.time() + sec))

        ev.state = new_state
        ev.last_action_at = at
        ev.last_action = action
        ev.last_actor = actor
        ev.last_reason = reason
        ev.snooze_until = snooze_until

        self._append_audit(
            {
                "kind": "event_action",
                "at": at,
                "event_id": ev.id,
                "action": action,
                "state": new_state,
                "actor": actor,
                "reason": reason,
                "snooze_until": snooze_until,
            }
        )
        return ev

    def list_events(self) -> list[SecurityEvent]:
        # 最新在前（簡單排序）
        return sorted(self.events.values(), key=lambda e: (e.created_at, e.id), reverse=True)


class Handler(BaseHTTPRequestHandler):
    store: EventStore

    def log_message(self, fmt: str, *args: Any) -> None:
        # 安靜一點，避免刷屏
        return

    def _not_found(self) -> None:
        _json_response(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            _json_response(self, HTTPStatus.OK, {"ok": True})
            return
        if parsed.path == "/api/security/events":
            qs = parse_qs(parsed.query)
            public = (qs.get("public") or ["0"])[0] == "1"
            items = []
            for ev in self.store.list_events():
                d = asdict(ev)
                if public:
                    # 公開視圖：隱去 raw_payload（但稽核仍在 audit log）
                    d["raw_payload"] = None
                items.append(d)
            _json_response(self, HTTPStatus.OK, {"ok": True, "events": items})
            return
        self._not_found()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/security/events":
            try:
                data = _read_json(self)
            except Exception:
                _json_response(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_json"})
                return
            ev = self.store.create_event(data)
            _json_response(self, HTTPStatus.CREATED, {"ok": True, "event": asdict(ev)})
            return

        # /api/security/events/<id>/action
        parts = parsed.path.strip("/").split("/")
        if len(parts) == 4 and parts[0] == "api" and parts[1] == "security" and parts[2] == "events" and parts[3]:
            # 這支不是 action endpoint
            self._not_found()
            return
        if len(parts) == 5 and parts[0] == "api" and parts[1] == "security" and parts[2] == "events" and parts[4] == "action":
            ev_id = parts[3]
            try:
                data = _read_json(self)
            except Exception:
                _json_response(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_json"})
                return

            action = str(data.get("action") or "").strip()
            actor = str(data.get("actor") or "").strip()
            reason = str(data.get("reason") or "").strip()
            snooze_seconds = data.get("snooze_seconds")

            if not actor:
                _json_response(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_actor"})
                return
            if not reason:
                _json_response(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_reason"})
                return

            try:
                ev = self.store.action_event(
                    ev_id=ev_id,
                    action=action,
                    actor=actor,
                    reason=reason,
                    snooze_seconds=int(snooze_seconds) if snooze_seconds is not None else None,
                )
            except KeyError:
                _json_response(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "event_not_found"})
                return
            except ValueError as e:
                _json_response(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(e)})
                return

            _json_response(self, HTTPStatus.OK, {"ok": True, "event": asdict(ev)})
            return

        self._not_found()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8799)
    ap.add_argument("--audit", default="security_event_audit.jsonl")
    args = ap.parse_args()

    store = EventStore(audit_path=os.path.abspath(args.audit))

    class _H(Handler):
        store = store

    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), _H)
    print(f"[demo] listening on http://127.0.0.1:{args.port}")
    print(f"[demo] audit log: {os.path.abspath(args.audit)}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

