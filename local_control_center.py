"""
local_control_center.py

本機中控 UI（繁中）：
- 集中顯示「兩機（本機/伺服器）」互動狀態
- 提供一鍵執行：DNS 傳播檢查、推送（rules/kb）、查看稽核紀錄

安全前提：
- 只綁定 127.0.0.1（不對外網開放）
- 高風險動作（推送）會由 safe_sync_push.py 內建「無回應＝禁止」硬閘門擋下

啟動：
  python local_control_center.py --port 8788
  然後開： http://127.0.0.1:8788/
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from risk_gate import check_server_health
from dns_propagation_check import DEFAULT_RESOLVERS, load_expected_from_config, query
from google_workspace_writer import write_workspace_artifact


BASE_DIR = Path(__file__).resolve().parent
UI_HTML = BASE_DIR / "wuchang_control_center.html"
DNS_CONFIG = BASE_DIR / "dns_records.json"
AUDIT_JSONL = BASE_DIR / "risk_action_audit.jsonl"


def _json(handler: BaseHTTPRequestHandler, status: int, payload: Dict[str, Any]) -> None:
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


def _read_json(handler: BaseHTTPRequestHandler) -> Dict[str, Any]:
    try:
        length = int(handler.headers.get("Content-Length") or "0")
    except Exception:
        length = 0
    body = handler.rfile.read(length) if length > 0 else b""
    if not body:
        return {}
    return json.loads(body.decode("utf-8"))


def _serve_file(handler: BaseHTTPRequestHandler, path: Path, content_type: str) -> None:
    if not path.exists():
        handler.send_response(HTTPStatus.NOT_FOUND)
        handler.end_headers()
        return
    raw = path.read_bytes()
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


def _get_expected_acme(domain: str) -> Dict[str, Any]:
    """
    從 dns_records.json 取得 _acme-challenge 相關 TXT 的預期值（若存在）。
    """
    domain = (domain or "").strip().rstrip(".")
    expected: Dict[str, Any] = {"domain": domain, "records": []}
    if not DNS_CONFIG.exists():
        expected["error"] = "dns_records.json_not_found"
        return expected

    exp_map = load_expected_from_config(DNS_CONFIG)
    targets = [
        (f"_acme-challenge.{domain}", "TXT"),
        (f"_acme-challenge.www.{domain}", "TXT"),
    ]
    for qname, qtype in targets:
        vals = exp_map.get((qname, qtype))
        expected["records"].append(
            {
                "qname": qname,
                "qtype": qtype,
                "expected_values": vals or [],
            }
        )
    return expected


def _check_acme_propagation(domain: str, resolvers: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    以多個 resolver 查詢 _acme-challenge TXT，並給出「是否可簽發」判斷。
    """
    domain = (domain or "").strip().rstrip(".")
    resolvers = resolvers or list(DEFAULT_RESOLVERS)

    exp = _get_expected_acme(domain)
    records = exp.get("records") or []
    out: Dict[str, Any] = {"domain": domain, "resolvers": resolvers, "expected": exp, "results": []}

    ready = True
    mismatches: List[str] = []

    for rec in records:
        qname = str(rec.get("qname") or "")
        qtype = str(rec.get("qtype") or "TXT")
        expected_values = list(rec.get("expected_values") or [])
        per: Dict[str, Any] = {"qname": qname, "qtype": qtype, "expected_values": expected_values, "by_resolver": {}}

        # 查詢
        answers_by_resolver: Dict[str, List[str]] = {}
        for r in resolvers:
            res = query(qname=qname, qtype=qtype, resolver=r, timeout_seconds=4)
            answers_by_resolver[r] = res.answers
            per["by_resolver"][r] = {
                "ok": res.ok,
                "answers": res.answers,
                "error": res.error,
            }
            if not res.ok:
                ready = False
                mismatches.append(f"{qtype} {qname}: {r} no_answer")

        # 一致性（所有 resolver 回應相同）
        norm = [tuple(answers_by_resolver[r]) for r in resolvers]
        if norm:
            all_same = all(v == norm[0] for v in norm[1:])
            per["all_resolvers_same"] = all_same
            if not all_same:
                ready = False
                mismatches.append(f"{qtype} {qname}: resolvers_mismatch")
        else:
            per["all_resolvers_same"] = True

        # 需包含 expected token（容許多值，但至少包含）
        if expected_values:
            exp_set = set(expected_values)
            for r in resolvers:
                got = set(answers_by_resolver.get(r) or [])
                missing = sorted(list(exp_set - got))
                if missing:
                    ready = False
                    mismatches.append(f"{qtype} {qname}: {r} missing_expected={missing}")
                    per.setdefault("missing_expected_by_resolver", {})[r] = missing

        out["results"].append(per)

    out["ready_to_issue"] = ready and not exp.get("error")
    out["mismatches"] = mismatches
    out["note"] = (
        "本檢查只負責判斷 DNS-01（_acme-challenge TXT）是否已在多個公用 DNS 上一致可見。"
        "若 ready_to_issue=true，通常即可進行憑證簽發；反之請先完成 DNS 處置並等待 TTL 傳播。"
    )
    return out

def _tail_jsonl(path: Path, limit: int = 50, max_bytes: int = 128_000) -> List[Dict[str, Any]]:
    """
    讀取 JSONL 尾端 N 筆（避免整檔讀入）。
    若某行不是 JSON，就以 {"raw": "..."} 形式回傳。
    """
    if not path.exists():
        return []
    size = path.stat().st_size
    start = max(0, size - max_bytes)
    with path.open("rb") as f:
        f.seek(start)
        chunk = f.read()
    lines = chunk.splitlines()
    # 若不是從 0 開始，第一行可能被截斷，丟掉
    if start > 0 and lines:
        lines = lines[1:]
    out: List[Dict[str, Any]] = []
    for b in lines[-limit:]:
        try:
            s = b.decode("utf-8", errors="replace").strip()
        except Exception:
            s = repr(b)
        if not s:
            continue
        try:
            out.append(json.loads(s))
        except Exception:
            out.append({"raw": s})
    return out


def _run_script(args: List[str], timeout_seconds: int = 60) -> Dict[str, Any]:
    """
    用當前 Python 執行 repo 內腳本，回傳 stdout/stderr/exit_code。
    """
    try:
        cp = subprocess.run(
            [sys.executable, *args],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        return {"exit_code": cp.returncode, "stdout": cp.stdout or "", "stderr": cp.stderr or ""}
    except Exception as e:
        return {"exit_code": 3, "stdout": "", "stderr": f"exception: {e}"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            _serve_file(self, UI_HTML, "text/html; charset=utf-8")
            return

        if parsed.path == "/api/local/health":
            _json(self, HTTPStatus.OK, {"ok": True})
            return

        if parsed.path == "/api/net/snapshot":
            qs = parse_qs(parsed.query)
            # 允許沿用 UI 內填寫的 healthUrl；若未提供就只做本機網路/DNS/閘道探測
            health_url = (qs.get("health_url") or [""])[0].strip()
            domains = qs.get("domain") or []
            args = ["network_snapshot.py"]
            if health_url:
                args += ["--health-url", health_url]
            if domains:
                args += ["--domains", *[d.strip() for d in domains if d.strip()]]
            res = _run_script(args, timeout_seconds=60)
            _json(self, HTTPStatus.OK, {"ok": True, "run": res})
            return

        if parsed.path == "/api/server/health":
            qs = parse_qs(parsed.query)
            url = (qs.get("url") or [""])[0].strip()
            if not url:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "missing_url"})
                return
            hc = check_server_health(url, timeout_seconds=3.0, retries=2)
            _json(self, HTTPStatus.OK, {"ok": True, "health": asdict(hc)})
            return

        if parsed.path == "/api/dns/expected":
            qs = parse_qs(parsed.query)
            domain = (qs.get("domain") or ["wuchang.life"])[0].strip()
            _json(self, HTTPStatus.OK, {"ok": True, "expected": _get_expected_acme(domain)})
            return

        if parsed.path == "/api/dns/acme_status":
            qs = parse_qs(parsed.query)
            domain = (qs.get("domain") or ["wuchang.life"])[0].strip()
            _json(self, HTTPStatus.OK, {"ok": True, "status": _check_acme_propagation(domain)})
            return

        if parsed.path == "/api/audit/tail":
            qs = parse_qs(parsed.query)
            name = (qs.get("file") or ["risk_action_audit.jsonl"])[0].strip()
            limit = int((qs.get("limit") or ["50"])[0])
            # 僅允許讀取 repo 內檔案（避免任意路徑）
            p = (BASE_DIR / name).resolve()
            if BASE_DIR not in p.parents and p != BASE_DIR:
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_path"})
                return
            items = _tail_jsonl(p, limit=max(1, min(limit, 200)))
            _json(self, HTTPStatus.OK, {"ok": True, "file": str(p), "items": items})
            return

        if parsed.path == "/api/docs":
            qs = parse_qs(parsed.query)
            which = (qs.get("name") or ["RISK_ACTION_SOP.md"])[0].strip()
            p = (BASE_DIR / which).resolve()
            if not p.exists() or (BASE_DIR not in p.parents and p != BASE_DIR):
                _json(self, HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
                return
            text = p.read_text(encoding="utf-8", errors="replace")
            _json(self, HTTPStatus.OK, {"ok": True, "name": which, "text": text})
            return

        self.send_response(HTTPStatus.NOT_FOUND)
        self.end_headers()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/run/dns_check":
            data = _read_json(self)
            domain = str(data.get("domain") or "wuchang.life").strip()
            only_acme = bool(data.get("check_acme", True))
            args = ["dns_propagation_check.py", "--domain", domain, "--config", "dns_records.json"]
            if only_acme:
                args.append("--check-acme")
            res = _run_script(args, timeout_seconds=60)
            _json(self, HTTPStatus.OK, {"ok": True, "run": res})
            return

        if parsed.path == "/api/run/sync_push":
            data = _read_json(self)
            profile = str(data.get("profile") or "rules").strip()
            if profile not in ("rules", "kb"):
                _json(self, HTTPStatus.BAD_REQUEST, {"ok": False, "error": "invalid_profile"})
                return
            health_url = str(data.get("health_url") or os.getenv("WUCHANG_HEALTH_URL") or "").strip()
            copy_to = str(data.get("copy_to") or os.getenv("WUCHANG_COPY_TO") or "").strip()
            actor = str(data.get("actor") or "ops").strip()

            # 允許不填：工具本身會依「無回應＝禁止」中止並留下稽核
            args = ["safe_sync_push.py", "--profile", profile, "--actor", actor]
            if health_url:
                args += ["--health-url", health_url]
            if copy_to:
                args += ["--copy-to", copy_to]

            res = _run_script(args, timeout_seconds=180)
            _json(self, HTTPStatus.OK, {"ok": True, "run": res})
            return

        if parsed.path == "/api/workspace/write":
            data = _read_json(self)
            kind = str(data.get("kind") or "little_j").strip()
            title = str(data.get("title") or "control_center").strip()
            content = str(data.get("content") or "").strip()
            meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}

            outdir = os.getenv("WUCHANG_WORKSPACE_OUTDIR") or ""
            webhook = os.getenv("WUCHANG_WORKSPACE_WEBHOOK_URL") or ""

            if not outdir and not webhook:
                # 沒有設定就不寫入（避免寫到未知位置）
                _json(
                    self,
                    HTTPStatus.BAD_REQUEST,
                    {
                        "ok": False,
                        "error": "missing_workspace_config",
                        "hint": "set WUCHANG_WORKSPACE_OUTDIR to a Google Drive synced folder (recommended), or set WUCHANG_WORKSPACE_WEBHOOK_URL",
                    },
                )
                return

            res = write_workspace_artifact(
                kind=kind,
                title=title,
                content=content,
                meta=meta,
                outdir=outdir or None,
                webhook_url=webhook or None,
            )
            _json(self, HTTPStatus.OK, {"ok": True, "result": res.__dict__})
            return

        self.send_response(HTTPStatus.NOT_FOUND)
        self.end_headers()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8788)
    args = ap.parse_args()

    if not UI_HTML.exists():
        raise SystemExit(f"missing UI file: {UI_HTML}")

    httpd = ThreadingHTTPServer(("127.0.0.1", int(args.port)), Handler)
    print(f"[ok] local control center: http://127.0.0.1:{args.port}/")
    httpd.serve_forever()


if __name__ == "__main__":
    main()

