import os
import sys
import time
import xmlrpc.client

URL = os.getenv("ODOO_URL", "http://localhost:8069")
DB = os.getenv("ODOO_DB", "admin")
USER = os.getenv("ODOO_USER", "admin")
PWD = os.getenv("ODOO_PWD", "admin")


def log(msg: str) -> None:
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def main() -> None:
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USER, PWD, {})
        if not uid:
            raise RuntimeError("auth failed")
        log(f"Auth OK, uid={uid}")

        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

        ver = common.version()
        log(f"Odoo version: {ver}")

        partner_id = models.execute_kw(
            DB,
            uid,
            PWD,
            "res.partner",
            "create",
            [
                {
                    "name": "TEST-48H-HIGH-PRIV",
                    "comment": "temp test record",
                }
            ],
        )
        log(f"Create partner id={partner_id}")

        models.execute_kw(
            DB,
            uid,
            PWD,
            "res.partner",
            "write",
            [[partner_id], {"comment": "updated by high-priv test"}],
        )
        log("Update partner comment OK")

        rec = models.execute_kw(
            DB,
            uid,
            PWD,
            "res.partner",
            "read",
            [[partner_id], ["name", "comment"]],
        )[0]
        log(f"Readback: {rec}")

        models.execute_kw(DB, uid, PWD, "res.partner",
                          "unlink", [[partner_id]])
        log("Rollback delete OK")

        log("== DONE: Odoo high-priv read/write/rollback ==")
    except Exception as e:
        log(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
