"""
dns_propagation_check.py

DNS 傳播現狀檢查（用於判斷是否可簽發憑證，特別是 DNS-01 / _acme-challenge TXT）。

特點：
- 直接呼叫系統 nslookup，向多個指定 resolver 查詢（避免只看本機快取）
- 可用 dns_records.json 作為「預期值」來源，對照是否一致
- 輸出人類可讀摘要，並以 exit code 表示是否通過

Exit codes：
0 = 全部符合（可視為已傳播）
2 = 有不一致/缺漏（不建議進行簽發）
3 = 執行錯誤（工具/環境問題）
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_RESOLVERS = [
    "1.1.1.1",  # Cloudflare
    "8.8.8.8",  # Google
    "9.9.9.9",  # Quad9
    "208.67.222.222",  # OpenDNS
]


@dataclass
class NslookupResult:
    ok: bool
    qname: str
    qtype: str
    resolver: str
    answers: List[str]
    raw: str
    error: str | None = None


def _run_nslookup(qname: str, qtype: str, resolver: str, timeout_seconds: int = 4) -> Tuple[int, str]:
    # Windows: nslookup -type=TXT name resolver
    cmd = ["nslookup", f"-type={qtype}", qname, resolver]
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds, check=False)
        out = (cp.stdout or "") + ("\n" + cp.stderr if cp.stderr else "")
        return cp.returncode, out
    except Exception as e:
        return 999, f"exception: {e}"


def _parse_nslookup_answers(qtype: str, output: str) -> List[str]:
    """
    解析 nslookup 的常見輸出（以 Windows 為主），抽取答案值。
    盡量保守：抓到的答案才算。
    """
    lines = [ln.strip() for ln in (output or "").splitlines() if ln.strip()]
    answers: List[str] = []

    # A/AAAA: "Name: xxx" 下面通常有 "Address: x.x.x.x" 或多個 "Addresses:"
    if qtype.upper() in {"A", "AAAA"}:
        for ln in lines:
            m = re.search(r"\bAddress(?:es)?\s*:\s*(.+)$", ln, flags=re.IGNORECASE)
            if m:
                # 可能同一行多個
                tail = m.group(1).strip()
                # 避免把 "8.8.8.8#53" 之類帶進來
                tail = tail.replace("#53", "")
                for token in re.split(r"[\s,]+", tail):
                    t = token.strip()
                    if t and re.match(r"^[0-9a-fA-F:\.]+$", t):
                        answers.append(t)
        # 有些版本會在下一行顯示 Address:
        for ln in lines:
            m = re.search(r"^\s*Address:\s*([0-9a-fA-F:\.]+)\s*$", ln, flags=re.IGNORECASE)
            if m:
                answers.append(m.group(1))

    # CNAME: "canonical name = target"
    elif qtype.upper() == "CNAME":
        for ln in lines:
            m = re.search(r"\bcanonical name\s*=\s*(\S+)", ln, flags=re.IGNORECASE)
            if m:
                answers.append(m.group(1).rstrip("."))

    # TXT: 常見為 'text = "xxx"' 或 '"xxx"'
    elif qtype.upper() == "TXT":
        # 1) text = "..."
        for ln in lines:
            m = re.search(r"\btext\s*=\s*\"(.*)\"\s*$", ln, flags=re.IGNORECASE)
            if m:
                answers.append(m.group(1))
        # 2) 有些會把 TXT 拆段多行：直接抓引號內容
        if not answers:
            for ln in lines:
                for m in re.finditer(r"\"([^\"]+)\"", ln):
                    answers.append(m.group(1))

    # MX: "mail exchanger = X" + "preference = N"
    elif qtype.upper() == "MX":
        for ln in lines:
            m = re.search(r"\bmail exchanger\s*=\s*(\S+)", ln, flags=re.IGNORECASE)
            if m:
                answers.append(m.group(1).rstrip("."))

    # CAA: nslookup 支援不一，先粗抓引號/; 內容（若 resolver 回應）
    elif qtype.upper() == "CAA":
        # 嘗試抓: 0 issue "letsencrypt.org"
        for ln in lines:
            if "CAA" in ln.upper() or "issue" in ln.lower() or "iodef" in ln.lower():
                for m in re.finditer(r"\"([^\"]+)\"", ln):
                    answers.append(m.group(1))

    # 去重保序
    seen = set()
    out: List[str] = []
    for a in answers:
        a2 = a.strip()
        if not a2:
            continue
        if a2 not in seen:
            seen.add(a2)
            out.append(a2)
    return out


def query(qname: str, qtype: str, resolver: str, timeout_seconds: int = 4) -> NslookupResult:
    code, raw = _run_nslookup(qname=qname, qtype=qtype, resolver=resolver, timeout_seconds=timeout_seconds)
    answers = _parse_nslookup_answers(qtype=qtype, output=raw)
    ok = bool(answers) and code in (0, 1)  # nslookup 有時 1 仍有答案
    err = None
    if not ok:
        err = "no_answers_or_error"
    return NslookupResult(ok=ok, qname=qname, qtype=qtype.upper(), resolver=resolver, answers=answers, raw=raw, error=err)


def load_expected_from_config(config_path: Path) -> Dict[Tuple[str, str], List[str]]:
    """
    將 dns_records.json 轉成 {(fqdn, qtype): [values]} 的預期表。
    """
    data = json.loads(config_path.read_text(encoding="utf-8"))
    domain = str(data.get("domain") or "").strip().rstrip(".")
    expected: Dict[Tuple[str, str], List[str]] = {}

    def fqdn(name: str) -> str:
        name = name.strip()
        if name in ("@", ""):
            return domain
        if name.endswith("." + domain) or name == domain:
            return name.rstrip(".")
        return f"{name}.{domain}"

    for section_key, section in [("records", data.get("records", {})), ("txt_records", data.get("txt_records", {})), ("mx_records", data.get("mx_records", {}))]:
        if not isinstance(section, dict):
            continue
        for name, rec in section.items():
            if not isinstance(rec, dict):
                continue
            rtype = str(rec.get("type") or "").upper().strip()
            vals = rec.get("values") or []
            if not isinstance(vals, list):
                vals = [str(vals)]
            vals2 = [str(v).strip().strip('"').rstrip(".") for v in vals if str(v).strip()]
            if not rtype:
                continue
            expected[(fqdn(str(name)), rtype)] = vals2

    return expected


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", default="wuchang.life", help="主網域（用於推導 _acme-challenge 等）")
    ap.add_argument("--config", default="dns_records.json", help="預期 DNS 設定檔（dns_records.json）")
    ap.add_argument("--resolvers", nargs="*", default=DEFAULT_RESOLVERS, help="要查詢的 DNS resolver 清單（IP）")
    ap.add_argument("--timeout", type=int, default=4, help="nslookup timeout 秒數")
    ap.add_argument("--check-acme", action="store_true", help="只檢查 _acme-challenge TXT（簽發憑證最關鍵）")
    ap.add_argument("--qname", action="append", default=[], help="額外指定要查的 fqdn（可重複）")
    ap.add_argument("--qtype", action="append", default=[], help="額外指定要查的 type（可重複，如 A/TXT/CNAME/MX/CAA）")
    args = ap.parse_args(argv)

    base_dir = Path(__file__).resolve().parent
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = (base_dir / config_path).resolve()

    expected: Dict[Tuple[str, str], List[str]] = {}
    if config_path.exists():
        expected = load_expected_from_config(config_path)
    domain = str(args.domain).strip().rstrip(".")

    # 要檢查的清單
    checks: List[Tuple[str, str]] = []
    if args.check_acme:
        checks = [(f"_acme-challenge.{domain}", "TXT"), (f"_acme-challenge.www.{domain}", "TXT")]
    else:
        # 先用 config 內的預期項目（較完整）
        checks = sorted(list(expected.keys()))
        # 再加上使用者指定
        for qn in args.qname:
            for qt in (args.qtype or ["A", "TXT"]):
                checks.append((qn.strip().rstrip("."), qt.strip().upper()))

    # 去重保序
    seen = set()
    checks2: List[Tuple[str, str]] = []
    for it in checks:
        if it not in seen:
            seen.add(it)
            checks2.append(it)

    # 執行查詢
    any_mismatch = False
    any_error = False
    print(f"[dns] domain={domain} resolvers={args.resolvers}")
    if config_path.exists():
        print(f"[dns] expected_config={config_path}")
    else:
        print(f"[dns] expected_config=missing ({config_path})")

    for (qname, qtype) in checks2:
        exp = expected.get((qname, qtype))
        print("")
        print(f"== {qtype} {qname} ==")
        if exp is not None:
            print(f"expected: {exp}")
        per_resolver: Dict[str, List[str]] = {}
        for r in args.resolvers:
            res = query(qname=qname, qtype=qtype, resolver=r, timeout_seconds=int(args.timeout))
            per_resolver[r] = res.answers
            if not res.ok:
                any_error = True
                print(f"- {r}: [NO ANSWER] ({res.error})")
            else:
                print(f"- {r}: {res.answers}")

        # 判斷一致性（所有 resolver 的答案集合相同）
        norm_sets = [tuple(per_resolver[r]) for r in args.resolvers]
        all_same = all(s == norm_sets[0] for s in norm_sets[1:]) if norm_sets else True
        if not all_same:
            any_mismatch = True
            print("!! mismatch: resolvers returned different answers")

        # 若有 expected，檢查是否包含 expected（容許多值，但至少包含）
        if exp is not None:
            exp_set = set(exp)
            for r in args.resolvers:
                got = set(per_resolver[r] or [])
                if not exp_set.issubset(got):
                    any_mismatch = True
                    print(f"!! mismatch: {r} missing expected values: {sorted(list(exp_set - got))}")

    print("")
    if any_mismatch:
        print("[RESULT] NOT READY: DNS not fully propagated / mismatched. (do not issue certificate yet)")
        return 2
    if any_error:
        print("[RESULT] INCONCLUSIVE: query errors but no mismatches detected. (re-run later)")
        return 2
    print("[RESULT] READY: DNS answers consistent & expected values observed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

