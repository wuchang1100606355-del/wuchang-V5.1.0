import base64
import json
import os
import sys
from contextlib import contextmanager
try:
    from odoo import api, SUPERUSER_ID
    import odoo
except Exception:
    odoo = None
    api = None
    SUPERUSER_ID = 1

# This script is intended to be executed inside "odoo shell"
# Example: odoo shell < /opt/wuchang/scripts/odoo_company_setup.py
#
# It updates company defaults (name/logo/contact info), website branding,
# and clears preset placeholders in a safe, idempotent way.

def _read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _read_logo_b64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read())
    except Exception:
        return None


def _country_id_from_code(env, code):
    if not code:
        return False
    country = env["res.country"].search([("code", "=", code)], limit=1)
    return country.id or False


@contextmanager
def _managed_env():
    # Use existing 'env' if provided by odoo shell; otherwise construct one
    if "env" in globals() and globals()["env"]:
        yield globals()["env"]
        return
    if not odoo or not api:
        raise RuntimeError("Odoo environment modules not available")
    db_name = None
    # Prefer config db_name, then environment variables
    try:
        db_name = odoo.tools.config.get("db_name")
    except Exception:
        db_name = None
    if not db_name:
        db_name = os.environ.get("POSTGRES_DB") or os.environ.get("DB_NAME") or "odoo"
    registry = odoo.registry(db_name)
    with registry.cursor() as cr:
        yield api.Environment(cr, SUPERUSER_ID, {})


def main(env):
    defaults_path = "/opt/wuchang/downloads/company_defaults.json"
    defaults = _read_json(defaults_path) or {}

    name = defaults.get("name") or "AI廟"
    email = defaults.get("email") or "admin@wuchang.life"
    phone = defaults.get("phone") or ""
    website_url = defaults.get("website") or ""
    street = defaults.get("street") or ""
    city = defaults.get("city") or ""
    zip_code = defaults.get("zip") or ""
    country_code = defaults.get("country_code") or ""
    vat = defaults.get("vat") or ""
    registry = defaults.get("company_registry") or ""
    logo_path = defaults.get("logo_path") or "/opt/wuchang/downloads/logo.png"
    store_names = defaults.get("stores") or ["仁義店", "重新店"]

    company = env.company or env["res.company"].search([], limit=1)

    vals = {
        "name": name,
        "email": email,
        "phone": phone,
        "website": website_url,
        "street": street,
        "city": city,
        "zip": zip_code,
        "vat": vat,
        "company_registry": registry,
    }
    country_id = _country_id_from_code(env, country_code)
    if country_id:
        vals["country_id"] = country_id

    logo_b64 = _read_logo_b64(logo_path)
    if logo_b64:
        vals["logo"] = logo_b64

    company.sudo().write(vals)
    print("company updated:", company.id, company.name)

    # Align base parameters
    icp = env["ir.config_parameter"].sudo()
    icp.set_param("web.company_name", name)
    lock = ((icp.get_param("wuchang.domain.lock") or "").strip().lower() in ("1","true","yes"))
    if website_url and (not lock):
        icp.set_param("web.base.url", website_url)

    # Update website branding if module installed
    if "website" in env.registry:
        website = env["website"].search([], limit=1)
        if website:
            website.sudo().write({"name": name})
            print("website updated:", website.id, website.name)

    # Clear default placeholders (YourCompany)
    partners = env["res.partner"].search([("name", "=", "YourCompany")])
    if partners:
        partners.sudo().write({"name": name})
        print("renamed YourCompany partners ->", name)

    # Optional: ensure POS stores names exist or updated
    if "pos.config" in env.registry:
        for idx, sname in enumerate(store_names):
            cfg = env["pos.config"].search([("name", "=", sname)], limit=1)
            if cfg:
                cfg.sudo().write({"name": sname})
                print("pos.config exists:", sname)
            else:
                # create minimal POS config attached to current company
                env["pos.config"].sudo().create(
                    {
                        "name": sname,
                        "company_id": company.id,
                        "iface_print_auto": True,
                        "receipt_header": name,
                        "receipt_footer": "",
                    }
                )
                print("pos.config created:", sname)

    print("done")


with _managed_env() as _env:
    main(_env)
