user = env["res.users"].search([("login", "=", "admin@wuchang.life")], limit=1)
print("found", user.ids)
if user:
    user.sudo()._set_password("odoo")
    user.sudo().write({"totp_secret": False, "active": True})
    print("done", user.id)
else:
    print("user not found")
