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
    dropbox_defaults_path = r"C:\Users\o0930\Dropbox\公司資料室\五常社區服務系統\行政\company_defaults.json"
    defaults = _read_json(dropbox_defaults_path) or _read_json(defaults_path) or {}

    branding = {}
    dropbox_branding_path = r"C:\Users\o0930\Dropbox\公司資料室\五常社區服務系統\行政\branding.json"
    downloads_branding_path = "/opt/wuchang/downloads/branding.json"
    for p in (dropbox_branding_path, downloads_branding_path):
        try:
            if os.path.exists(p):
                b = _read_json(p) or {}
                if b:
                    branding = b
                    break
        except Exception:
            pass

    name = defaults.get("name") or "五常物業規劃顧問股份有限公司"
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

    assoc = env["res.company"].search([("name", "=", "新北市三重區五常社區發展協會")], limit=1)
    if not assoc:
        assoc = env["res.company"].sudo().create({"name": "新北市三重區五常社區發展協會"})
    main_co = env["res.company"].search([("name", "=", "聊國咖啡重新總店")], limit=1)
    if not main_co:
        main_co = env["res.company"].sudo().create({"name": "聊國咖啡重新總店", "parent_id": assoc.id})
    branch_co = env["res.company"].search([("name", "=", "聊國咖啡仁義分店")], limit=1)
    if not branch_co:
        branch_co = env["res.company"].sudo().create({"name": "聊國咖啡仁義分店", "parent_id": assoc.id})

    if "pos.config" in env.registry:
        cfg_main = env["pos.config"].search([("name", "=", "聊國咖啡重新總店")], limit=1)
        if cfg_main:
            cfg_main.sudo().write({"company_id": main_co.id, "receipt_header": main_co.name})
        else:
            env["pos.config"].sudo().create({"name": "聊國咖啡重新總店", "company_id": main_co.id, "iface_print_auto": True, "receipt_header": main_co.name, "receipt_footer": ""})
        cfg_branch = env["pos.config"].search([("name", "=", "聊國咖啡仁義分店")], limit=1)
        if cfg_branch:
            cfg_branch.sudo().write({"company_id": branch_co.id, "receipt_header": branch_co.name})
        else:
            env["pos.config"].sudo().create({"name": "聊國咖啡仁義分店", "company_id": branch_co.id, "iface_print_auto": True, "receipt_header": branch_co.name, "receipt_footer": ""})

    print("done")

    try:
        if branding:
            icp.set_param("branding.producer", branding.get("producer", name))
            icp.set_param("branding.association", branding.get("association", "新北市三重區五常社區發展協會"))
            icp.set_param("branding.system_vendor", branding.get("system_vendor", name))
            icp.set_param("branding.system_owner", branding.get("system_owner", "新北市三重區五常社區發展協會"))
            icp.set_param("branding.coffee_org", branding.get("coffee_org", ""))
            icp.set_param("branding.patent", branding.get("patent", ""))
            icp.set_param("branding.coffee_main_phone", branding.get("coffee_main_phone", ""))
            icp.set_param("branding.coffee_branch_phone", branding.get("coffee_branch_phone", ""))
            icp.set_param("branding.patent_no", branding.get("patent_no", ""))
            icp.set_param("branding.google_form_wish_url", branding.get("google_form_wish_url", ""))
            icp.set_param("branding.google_doc_research_url", branding.get("google_doc_research_url", ""))
            icp.set_param("branding.marquee_text", branding.get("marquee_text", ""))
            badges = branding.get("badges") or []
            try:
                icp.set_param("branding.badges", json.dumps(badges, ensure_ascii=False))
            except Exception:
                pass
            print("branding parameters applied")
        else:
            icp.set_param("branding.producer", name)
            icp.set_param("branding.association", "新北市三重區五常社區發展協會")
            icp.set_param("branding.system_vendor", name)
            icp.set_param("branding.system_owner", "新北市三重區五常社區發展協會")
            try:
                icp.set_param("branding.badges", json.dumps([
                    {"slug": "google_nonprofit", "title": "Google 非營利", "image_url": ""},
                    {"slug": "google_startup", "title": "Google 新創", "image_url": ""},
                    {"slug": "sinyi_community", "title": "社區一家", "image_url": ""}
                ], ensure_ascii=False))
            except Exception:
                pass
            print("branding parameters applied (defaults)")
    except Exception as e:
        print("branding parameters error:", e)


with _managed_env() as _env:
    main(_env)
