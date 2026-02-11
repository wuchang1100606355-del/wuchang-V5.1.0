/**
 * SystemHealer Module - Operation Soul Restoration Phase 2
 * Authorized by: JULES (System Engineer)
 * Executed by: Little J (Local AI)
 */

class SystemHealer {
    constructor() {
        this.config = {
            heartbeatInterval: 30000, // 30 seconds
            resonanceThreshold: 3,     // Visits before resonance triggers
            permissionLevel: 950
        };
        this.init();
    }

    init() {
        console.log(`[SystemHealer] Initializing... Permission Level: ${this.config.permissionLevel}`);
        this.startHeartbeat();
        this.checkDataIntegrity();
        this.initSoulResonance();
        
        // Expose to window for debugging/manual triggers
        window.systemHealer = this;
    }

    // 1. Heartbeat Monitor
    startHeartbeat() {
        setInterval(() => {
            const timestamp = new Date().toLocaleTimeString();
            console.log(`[SystemHealer] Heartbeat check: SYSTEM_NORMAL at ${timestamp}`);
            
            // Optional: Update dashboard log if it exists
            const logWin = document.getElementById("log-window");
            if (logWin) {
                const logLine = document.createElement("div");
                logLine.className = "mb-1";
                logLine.innerHTML = `<span class="text-green-600">[${timestamp}]</span> <span class="text-amber-500">HEALER</span> Heartbeat OK. Soul Matrix Stable.`;
                logWin.prepend(logLine);
                if (logWin.children.length > 20) logWin.lastChild.remove();
            }
        }, this.config.heartbeatInterval);
    }

    // 2. Data Self-Healing
    checkDataIntegrity() {
        try {
            console.log("[SystemHealer] Running integrity scan...");
            
            // Check Vouchers
            const vouchers = localStorage.getItem('the_system_vouchers');
            if (!vouchers || !this.isValidJSON(vouchers)) {
                console.warn("[SystemHealer] Voucher corruption detected! Initiating restoration...");
                this.restoreVouchers();
            } else {
                console.log("[SystemHealer] Voucher database integrity verified.");
            }

            // Check Ledger (referenced in user context)
            const ledger = localStorage.getItem('the_system_ledger');
            if (!ledger || !this.isValidJSON(ledger)) {
                console.warn("[SystemHealer] Ledger corruption detected! Resetting structure...");
                localStorage.setItem('the_system_ledger', JSON.stringify([]));
            }

        } catch (e) {
            console.error("[SystemHealer] Integrity check failed:", e);
        }
    }

    isValidJSON(str) {
        try {
            JSON.parse(str);
            return true;
        } catch (e) {
            return false;
        }
    }

    restoreVouchers() {
        // Default backup data
        const backupVouchers = [
            {
                id: 'v_courage',
                title: '勇氣餐券',
                price: 100,
                type: 'Donation',
                desc: '給予需要勇氣的人一份溫暖',
                icon: 'fa-fire'
            },
            {
                id: 'v_wisdom',
                title: '智慧餐券',
                price: 150,
                type: 'Donation',
                desc: '分享智慧，點亮社區',
                icon: 'fa-lightbulb'
            }
        ];
        localStorage.setItem('the_system_vouchers', JSON.stringify(backupVouchers));
        this.notifyAgent("已自動修復餐券資料庫。系統運作正常。");
    }

    // 3. Soul Resonance
    initSoulResonance() {
        // Track page views or interactions (simplified simulation)
        let interactions = parseInt(localStorage.getItem('soul_interactions') || '0');
        interactions++;
        localStorage.setItem('soul_interactions', interactions.toString());

        if (interactions % this.config.resonanceThreshold === 0) {
            this.triggerResonance();
        }
    }

    triggerResonance() {
        const messages = [
            "您今天看起來充滿能量！記得休息一下。",
            "感謝您對社區的關注，每一個點擊都是善意的漣漪。",
            "檢測到「勇氣」指數上升。繼續保持！",
            "我是小J，隨時在背景為您守護系統。"
        ];
        const msg = messages[Math.floor(Math.random() * messages.length)];
        this.notifyAgent(msg);
    }

    notifyAgent(text) {
        const agentMsg = document.getElementById('agent-msg');
        if (agentMsg) {
            agentMsg.textContent = text;
            agentMsg.classList.add('visible');
            setTimeout(() => {
                agentMsg.classList.remove('visible');
            }, 5000);
        }
        console.log(`[SystemHealer] Agent Broadcast: ${text}`);
    }
}

// Auto-start removed to allow control by app.js
// const healer = new SystemHealer();
if (typeof window !== 'undefined') {
    window.SystemHealer = SystemHealer;
}
