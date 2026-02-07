import os
import sys
import subprocess
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
OPEN_BROWSER = os.getenv("DEMO_OPEN_BROWSER", "1") != "0"

SCRIPTS = [
    ("Odoo high-priv CRUD test", BASE_DIR / "test_odoo_high_priv.py"),
    ("Google Drive/Sheets/Gmail test", BASE_DIR / "test_google_services.py"),
]


def run_script(label: str, path: Path) -> int:
    if not path.exists():
        print(f"[SKIP] {label}: missing {path}")
        return 0
    cmd = [sys.executable, str(path)]
    print(f"\n[RUN ] {label}\n       {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print(f"[OK  ] {label}\n")
    else:
        print(f"[FAIL] {label} (exit {result.returncode})\n")
    return result.returncode


def maybe_open_browser() -> None:
    if not OPEN_BROWSER:
        return
    url = f"{ODOO_URL.rstrip('/')}/web"
    try:
        webbrowser.open(url)
        print(f"[INFO] Opened browser to {url}")
    except Exception as exc:  # pragma: no cover
        print(f"[WARN] Could not open browser automatically: {exc}")


def main() -> None:
    print("== Auto demo runner ==")
    print(f"Python: {sys.executable}")
    print(f"Working dir: {BASE_DIR}")

    maybe_open_browser()

    failed = 0
    for label, path in SCRIPTS:
        rc = run_script(label, path)
        if rc != 0:
            failed += 1

    if failed:
        print(f"== Demo finished with {failed} failure(s) ==")
        sys.exit(1)
    print("== Demo finished successfully ==")


if __name__ == "__main__":
    main()
