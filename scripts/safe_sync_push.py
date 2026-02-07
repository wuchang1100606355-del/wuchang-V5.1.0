"""
safe_sync_push.py

同步推送（Local -> Server）工具：內建「無回應＝禁止高風險作業」硬規則。

用途：
- 把本機產出的資料/索引檔推送到「伺服器可讀取的位置」（例如：SMB 分享資料夾 / 掛載磁碟）
- 推送前強制做伺服器健康檢查（health URL）
- 每次動作寫入 JSONL 稽核檔（append-only）

注意：
- 本工具不做「刪除」遠端內容，只做「版本化/原子覆蓋」的檔案更新。
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from risk_gate import (
    RiskGateError,
    now_iso,
    append_audit_jsonl,
    require_responsive_or_abort,
    sha256_file,
)


DEFAULT_FILES = [
    "wuchang_community_knowledge_index.json",
    "wuchang_community_context_compact.md",
]

RULE_FILES = [
    "AGENT_CONSTITUTION.md",
    "RISK_ACTION_SOP.md",
    "risk_gate.py",
    "safe_sync_push.py",
    "api_community_data.py",
]


def _atomic_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, dir=str(dst.parent), prefix=dst.name + ".", suffix=".tmp") as tf:
        tmp_path = Path(tf.name)
    try:
        shutil.copy2(src, tmp_path)
        os.replace(str(tmp_path), str(dst))  # atomic on same volume
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass


def _collect_files(files: List[str]) -> List[Path]:
    out: List[Path] = []
    for f in files:
        p = Path(f).expanduser()
        if not p.is_absolute():
            p = (Path(__file__).resolve().parent / p).resolve()
        out.append(p)
    return out


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--health-url", default=None, help="伺服器健康檢查 URL（無回應即中止）。亦可用環境變數 WUCHANG_HEALTH_URL")
    ap.add_argument("--copy-to", default=None, help="推送目標資料夾（可為 SMB/掛載磁碟）。亦可用環境變數 WUCHANG_COPY_TO")
    ap.add_argument("--actor", default="unknown", help="操作者（會寫入稽核）")
    ap.add_argument("--audit", default="risk_action_audit.jsonl", help="稽核 JSONL 檔路徑（append-only）")
    ap.add_argument(
        "--profile",
        choices=["kb", "rules"],
        default="kb",
        help="推送檔案 profile：kb（索引+compact）、rules（新規則/閘門/推送工具）",
    )
    ap.add_argument("--files", nargs="*", default=None, help="自訂要推送的檔案清單（若提供則覆蓋 profile）")
    ap.add_argument("--timeout", type=float, default=3.0, help="健康檢查 timeout（秒）")
    ap.add_argument("--retries", type=int, default=2, help="健康檢查重試次數")
    args = ap.parse_args(argv)

    health_url = args.health_url or os.getenv("WUCHANG_HEALTH_URL")
    copy_to = args.copy_to or os.getenv("WUCHANG_COPY_TO")
    if not health_url or not copy_to:
        # 依「無回應/不可驗證＝禁止」：沒有目標就不執行推送
        audit_path = Path(args.audit).expanduser()
        if not audit_path.is_absolute():
            audit_path = (Path(__file__).resolve().parent / audit_path).resolve()
        append_audit_jsonl(
            audit_path,
            {
                "timestamp": now_iso(),
                "kind": "sync_push",
                "result": "aborted_missing_target_config",
                "actor": args.actor,
                "health_url": health_url,
                "copy_to": copy_to,
                "hint": "provide --health-url/--copy-to or set WUCHANG_HEALTH_URL/WUCHANG_COPY_TO",
            },
        )
        print("blocked: missing --health-url/--copy-to (or env vars).", file=sys.stderr)
        return 2

    audit_path = Path(args.audit).expanduser()
    if not audit_path.is_absolute():
        audit_path = (Path(__file__).resolve().parent / audit_path).resolve()

    selected_files = list(args.files) if args.files else (RULE_FILES if args.profile == "rules" else DEFAULT_FILES)

    # 0) 風險閘門：無回應＝禁止
    try:
        require_responsive_or_abort(
            health_url=health_url,
            audit_path=audit_path,
            action_type="sync_push",
            actor=args.actor,
            machines="local->server",
            timeout_seconds=float(args.timeout),
            retries=int(args.retries),
            extra={"copy_to": copy_to, "files": selected_files, "profile": args.profile},
        )
    except RiskGateError as e:
        # 額外再寫一筆「已中止」紀錄（便於人眼看）
        append_audit_jsonl(
            audit_path,
            {
                "timestamp": now_iso(),
                "kind": "sync_push",
                "result": "aborted_blocked_no_response",
                "actor": args.actor,
                "health_url": health_url,
                "copy_to": copy_to,
                "error": str(e),
            },
        )
        print(str(e), file=sys.stderr)
        return 2

    # 1) 檔案存在性檢查（屬於高風險作業前置：無法驗證就中止）
    src_files = _collect_files(selected_files)
    missing = [str(p) for p in src_files if not p.exists()]
    if missing:
        append_audit_jsonl(
            audit_path,
            {
                "timestamp": now_iso(),
                "kind": "sync_push",
                "result": "aborted_missing_source_files",
                "actor": args.actor,
                "missing": missing,
            },
        )
        print(f"blocked: missing source files: {missing}", file=sys.stderr)
        return 2

    # 2) 推送（原子覆蓋）
    target_dir = Path(copy_to).expanduser()
    results: List[Dict[str, Any]] = []
    for src in src_files:
        dst = (target_dir / src.name).resolve()
        before_hash = sha256_file(src)
        _atomic_copy(src, dst)
        after_hash = sha256_file(dst)
        results.append(
            {
                "file": src.name,
                "src": str(src),
                "dst": str(dst),
                "sha256": before_hash,
                "verify_dst_sha256": after_hash,
                "ok": before_hash == after_hash,
            }
        )

    ok = all(r.get("ok") for r in results)
    append_audit_jsonl(
        audit_path,
        {
            "timestamp": now_iso(),
            "kind": "sync_push",
            "result": "success" if ok else "failed_verify",
            "actor": args.actor,
            "health_url": health_url,
            "copy_to": str(target_dir),
            "profile": args.profile,
            "files": results,
        },
    )

    # 3) 給人看的輸出
    print(json.dumps({"ok": ok, "files": results}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

