/** @odoo-module **/
import { registry } from "@web/core/registry";

function openFront(env) {
    const host = window.location.host || "";
    let url = "/pos_simulator";
    if (host.endsWith("wuchang.life")) {
        url = "https://cafe.wuchang.life/";
    } else if (host.endsWith("wuchang.global")) {
        url = "https://cafe.wuchang.global/";
    }
    window.open(url, "_blank", "noopener,noreferrer");
}

registry.category("user_menuitems").add("wuchang_front_link", {
    sequence: 1,
    description: "前台入口",
    callback: openFront,
});
