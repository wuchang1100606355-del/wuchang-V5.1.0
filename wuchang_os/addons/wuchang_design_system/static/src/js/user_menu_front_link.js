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

function frontItem(env) {
    return {
        type: "item",
        id: "wuchang_front_link",
        description: "前台入口",
        callback: () => openFront(env),
        sequence: 1,
    };
}

registry.category("user_menuitems").add("wuchang_front_link", frontItem);
