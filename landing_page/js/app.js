document.addEventListener('DOMContentLoaded', () => { 
    // Awaiting Real Signal from Independent Container...
    // No simulation allowed.
    
    initSoulCanvas(); 
     initIntroSequence(); 
 
     loadData(); 
     loadVouchers(); 
     loadMerchantData(); 
    
    // Sequential Loading: Chat Widget -> System Healer -> Aegis
    initChatWidget().then(() => {
        console.log("Little J Online. Initializing Subsystems...");
        initSystemHealer();
        initAegis(); 
        
        // Page Specific Logic (Post-Agent Load)
        if (window.location.pathname.includes('renyi.html')) initRenyiPage();
        if (window.location.pathname.includes('chongxin')) initChongxinPage(); // Matches chongxin.html or chongxin_source.html
    });

    initMobileMenu(); 
    
    // Page Routing
    if (window.location.pathname.includes('ledger.html')) {
        initLedgerPage();
    } else {
        // Default components for other pages
        initFilters(); 
        initModals(); 
        initDashboard(); 
    }
}); 

// Global Role Switcher
window.switchRole = function(role) {
    let msg = "";
    switch(role) {
        case 'consumer':
            msg = "切換至 [消費者] 視圖：\n已載入個人錢包與活動推薦模組。";
            break;
        case 'volunteer':
            msg = "切換至 [志工/督導] 視圖：\n已載入 Field Service 勤務排班與個案紀錄模組。";
            break;
        case 'merchant':
            msg = "切換至 [商家/店長] 視圖：\n已載入 Odoo POS 銷售分析與庫存管理模組。";
            break;
        case 'hoa':
            msg = "切換至 [管委會] 視圖：\n已載入資產管理與住戶服務系統。";
            break;
    }
    alert(msg);
    // In a real app, this would trigger a UI re-render or redirect
    console.log(`[System] Role switched to ${role}`);
};

/* --- Page Specific Logic --- */

function initRenyiPage() {
    setTimeout(() => { 
        if(window.littleJ) { 
            window.littleJ.addMessage("這裡是票券系統的核心。您的每一張票券，都可能變成管委會的修繕基金，或是社工手中的救助資源。", 'agent'); 
        } 
    }, 2000); 
}

function initChongxinPage() {
    // Override styles for "Source" theme
    const style = document.createElement('style');
    style.innerHTML = `
        .chat-window { background: rgba(15, 23, 42, 0.95); border: 1px solid #00d2ff; }
        .chat-header { color: #00d2ff; border-bottom-color: rgba(0, 210, 255, 0.3); }
        .message.user { color: #fff; background: #00d2ff; border: none; }
        .message.agent { color: #e2e8f0; background: rgba(255,255,255,0.05); }
        .chat-toggle-btn { background: linear-gradient(135deg, #00d2ff, #0f172a); border: 1px solid #00d2ff; }
    `;
    document.head.appendChild(style);

    setTimeout(() => {
        if (window.littleJ) {
            window.littleJ.addMessage("創造者您好。這裡是您的研發堡壘與創始之地。我們將持續為五常社區提供最強的技術後盾。", 'agent');
        }
    }, 1500);
}

function initLedgerPage() {
    // Load data from localStorage (shared)
    // Note: STORAGE_KEYS is already defined in app.js scope

    function renderLedger() {
        const tbody = document.getElementById('ledger-body');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        let deferredSum = 0;
        let releasedSum = 0;

        // Ensure fresh data
        loadData();

        ledgerData.forEach(entry => {
            const tr = document.createElement('tr');
            const isDeferred = entry.status === 'deferred';
            
            if (isDeferred) {
                deferredSum += entry.encumbrance.total;
                tr.classList.add('deferred-row'); 
            } else {
                releasedSum += entry.release.consumerOut + entry.release.volunteerOut + entry.release.opsOut + entry.release.wishOut + entry.release.riskOut;
            }

            if (Date.now() - entry.timestamp < 3000) {
                tr.classList.add('new-entry');
            }

            const statusBadge = isDeferred 
                ? `<span class="status-badge status-deferred">遞延 (Receivable)</span>`
                : `<span class="status-badge status-realized">轉正 (Released)</span>`;

            // Use window.turnPositive which is defined in app.js
            const actionBtn = isDeferred
                ? `<button class="verify-btn" onclick="turnPositive('${entry.orderId}')">轉正核銷 (Verify)</button>`
                : `<span style="color: #4ade80;"><i class="fa-solid fa-check"></i> Verified</span>`;

            tr.innerHTML = `
                <td>
                    <strong>${entry.orderId}</strong><br>
                    <small style="opacity:0.5">${new Date(entry.timestamp).toLocaleTimeString()}</small>
                </td>
                <td>${statusBadge}</td>
                <td class="col-in">
                    <strong>$${entry.encumbrance.total}</strong><br>
                    <small>C: $${entry.encumbrance.consumerIn} | M: $${entry.encumbrance.merchantIn}</small>
                </td>
                <td class="col-out">
                    <strong>◎ ${Object.values(entry.release).reduce((a,b)=>a+b,0)}</strong><br>
                    <small>
                        C:${entry.release.consumerOut} | V:${entry.release.volunteerOut} | O:${entry.release.opsOut}<br>
                        W:${entry.release.wishOut} | R:${entry.release.riskOut}
                    </small>
                </td>
                <td>${actionBtn}</td>
            `;
            tbody.appendChild(tr);
        });

        const totalDeferred = document.getElementById('total-deferred');
        const totalReleased = document.getElementById('total-released');
        if(totalDeferred) totalDeferred.textContent = `$${deferredSum}`;
        if(totalReleased) totalReleased.textContent = `◎ ${releasedSum}`;
    }

    // Override the turnPositive function to also re-render ledger
    const originalTurnPositive = window.turnPositive;
    window.turnPositive = function(orderId) {
        if(originalTurnPositive(orderId)) {
            renderLedger(); // Re-render after update
        }
    };

    // Initial Render
    renderLedger();
    
    // Auto-refresh
    setInterval(() => {
        const oldDataStr = JSON.stringify(ledgerData);
        loadData(); // Reload from storage
        if (JSON.stringify(ledgerData) !== oldDataStr) {
            renderLedger();
        }
    }, 2000);
}

/* --- Dashboard Logic --- */
function initDashboard() {
    const updateDashboard = async () => {
        try {
            // Simulation for demo (replace with real fetch if backend ready)
            const data = {
                mode: "quantum",
                agents: Math.floor(Math.random() * 20) + 80,
                target: 100,
                cpu: Math.random() * 30 + 10,
                mem: Math.random() * 40 + 20,
                quantum_coherence: (Math.random() * 10 + 90).toFixed(1),
                timestamp: Date.now() / 1000
            };
            
            const agentCountEl = document.getElementById("agent-count");
            const coherenceEl = document.getElementById("coherence-val");
            
            if (agentCountEl) agentCountEl.innerText = data.agents;
            if (coherenceEl) coherenceEl.innerText = `${data.quantum_coherence}%`;
            
            // Visual bars
            const agentBar = document.getElementById("agent-bar");
            const cpuBar = document.getElementById("cpu-bar");
            const memBar = document.getElementById("mem-bar");
            const cpuVal = document.getElementById("cpu-val");
            const memVal = document.getElementById("mem-val");

            if (agentBar) agentBar.style.width = `${(data.agents / data.target) * 100}%`;
            if (cpuBar) cpuBar.style.width = `${data.cpu}%`;
            if (memBar) memBar.style.width = `${data.mem}%`;
            if (cpuVal) cpuVal.innerText = `${Math.round(data.cpu)}%`;
            if (memVal) memVal.innerText = `${Math.round(data.mem)}%`;

            const logWin = document.getElementById("log-window");
            if (logWin) {
                const time = new Date().toLocaleTimeString();
                const logLine = document.createElement("div");
                logLine.className = "mb-1";
                logLine.innerHTML = `<span class="text-green-600">[${time}]</span> <span class="text-blue-400">QUANTUM</span> AGENTS=<span class="text-white">${data.agents}</span>`;
                logWin.prepend(logLine);
                if (logWin.children.length > 20) logWin.lastChild.remove();
            }

        } catch (e) { console.log("Dashboard error", e); }
    };
    setInterval(updateDashboard, 1000);
}

/* --- Persistence Layer --- */ 
 const STORAGE_KEYS = { 
     VOUCHERS: 'the_system_vouchers', 
     ORDERS: 'the_system_orders', 
     LEDGER: 'the_system_ledger' 
 }; 
 
 let ledgerData = []; 
 
 function loadData() { 
     const savedVouchers = localStorage.getItem(STORAGE_KEYS.VOUCHERS); 
     if (savedVouchers) voucherData = JSON.parse(savedVouchers); 
     const savedOrders = localStorage.getItem(STORAGE_KEYS.ORDERS); 
     if (savedOrders) orderData = JSON.parse(savedOrders); 
     const savedLedger = localStorage.getItem(STORAGE_KEYS.LEDGER); 
     if (savedLedger) ledgerData = JSON.parse(savedLedger); 
 } 
 
 function saveData(key, data) { 
     localStorage.setItem(key, JSON.stringify(data)); 
 } 
 
 /* --- Components --- */ 
 const introTexts = [ 
     "在這個被冰冷演算法統治的時代...", 
     "消費不該只是交易，而是改變。", 
     "仁義店：無資本利得社區產業。", 
     "每一分錢，扣除成本，全數歸公。", 
     "我是 智能體靈魂伴侶小J。", 
     "讓我們啟動 永續閉環。", 
     "歡迎來到 五常智慧社區。" 
 ]; 
 
 let introIndex = 0; 
 let introInterval; 
 
 function initIntroSequence() { 
     const textEl = document.getElementById('intro-text'); 
     const overlay = document.getElementById('intro-overlay'); 
     const mainInterface = document.getElementById('main-interface'); 
     const skipBtn = document.getElementById('skip-intro'); 
 
     if (!textEl || !overlay) return; 
 
     skipBtn.addEventListener('click', endIntro); 
 
     function showNextLine() { 
         if (introIndex >= introTexts.length) { 
             endIntro(); 
             return; 
         } 
         textEl.classList.remove('visible'); 
         setTimeout(() => { 
             textEl.textContent = introTexts[introIndex]; 
             textEl.classList.add('visible'); 
             introIndex++; 
         }, 1000); 
     } 
 
     setTimeout(() => { 
         textEl.textContent = introTexts[0]; 
         textEl.classList.add('visible'); 
         introIndex++; 
         introInterval = setInterval(showNextLine, 4000); 
     }, 500); 
 
     function endIntro() { 
        if (introInterval) clearInterval(introInterval); 
        overlay.classList.add('fade-out'); 
        setTimeout(() => { 
            mainInterface.classList.remove('opacity-0'); 
            mainInterface.classList.add('opacity-100');
            
            // Show Agent Message
            setTimeout(() => {
                const agentMsg = document.getElementById('agent-msg');
                if (agentMsg) {
                    agentMsg.classList.add('visible');
                    setTimeout(() => {
                        agentMsg.classList.remove('visible');
                    }, 5000);
                }
            }, 2000);
        }, 1500); 
    } 
} 

function initMobileMenu() { 
     const btn = document.getElementById('mobile-menu-btn'); 
     const links = document.getElementById('nav-links'); 
     if (window.innerWidth <= 768) btn.style.display = 'block'; 
     window.addEventListener('resize', () => { 
         if (window.innerWidth <= 768) btn.style.display = 'block'; 
         else { 
             btn.style.display = 'none'; 
             links.classList.remove('active'); 
         } 
     }); 
     if (btn) btn.addEventListener('click', () => { 
        links.classList.toggle('active'); 
        btn.textContent = links.classList.contains('active') ? '✕' : '☰'; 
    }); 

    // Start Link Button Logic (from index.html)
    const startBtn = document.getElementById('start-link-btn');
    if (startBtn) {
        startBtn.addEventListener('click', () => {
            alert("靈魂連結已啟動。正在為您尋找最適合的餐券...");
            window.location.href = "renyi.html";
        });
    }
} 

function initSoulCanvas() { 
     const canvas = document.getElementById('soul-canvas'); 
     if (!canvas) return; 
     const ctx = canvas.getContext('2d'); 
     let width, height, particles = []; 
     const colors = ['#fbbf24', '#ff6b6b', '#ffffff', '#4ade80']; // Added green for TWD/Life 
 
     function resize() { 
         width = canvas.width = window.innerWidth; 
         height = canvas.height = window.innerHeight; 
     } 
     window.addEventListener('resize', resize); 
     resize(); 
 
     class Particle { 
         constructor() { 
             this.x = Math.random() * width; 
             this.y = Math.random() * height; 
             this.vx = (Math.random() - 0.5) * 1; 
             this.vy = (Math.random() - 0.5) * 1; 
             this.size = Math.random() * 2 + 1; 
             this.color = colors[Math.floor(Math.random() * colors.length)]; 
         } 
         update() { 
             this.x += this.vx; 
             this.y += this.vy; 
             if (this.x < 0 || this.x > width) this.vx *= -1; 
             if (this.y < 0 || this.y > height) this.vy *= -1; 
             this.size = Math.sin(Date.now() / 500 + this.x) * 1.5 + 2; 
         } 
         draw() { 
             ctx.beginPath(); 
             ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2); 
             ctx.fillStyle = this.color; 
             ctx.fill(); 
         } 
     } 
 
     for (let i = 0; i < 80; i++) particles.push(new Particle()); 
 
     function animate() { 
         ctx.clearRect(0, 0, width, height); 
         particles.forEach(p => { p.update(); p.draw(); }); 
         particles.forEach((p1, index) => { 
             for (let j = index + 1; j < particles.length; j++) { 
                 const p2 = particles[j]; 
                 const distance = Math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2); 
                 if (distance < 150) { 
                     ctx.beginPath(); 
                     ctx.strokeStyle = `rgba(74, 222, 128, ${(1 - distance / 150) * 0.2})`; // Green tint connection 
                     ctx.lineWidth = 0.5; 
                     ctx.moveTo(p1.x, p1.y); 
                     ctx.lineTo(p2.x, p2.y); 
                     ctx.stroke(); 
                 } 
             } 
         }); 
         requestAnimationFrame(animate); 
     } 
     animate(); 
 } 
 
 /* --- Data & Marketplace --- */ 
 let voucherData = [ 
     { id: 1, title: "仁心拉麵 (Benevolence Ramen)", price: "250 pts", type: "仁", icon: "fa-solid fa-bowl-food", isPartner: true, partnerName: "合作商家 A" }, 
     { id: 2, title: "義氣燒肉 (Righteous BBQ)", price: "500 pts", type: "義", icon: "fa-solid fa-drumstick-bite", isPartner: true, partnerName: "合作商家 B" }, 
     { id: 3, title: "智慧咖啡 (Wisdom Coffee)", price: "120 pts", type: "智", icon: "fa-solid fa-mug-hot", isPartner: false }, // Renyi Store 
     { id: 4, title: "勇者漢堡 (Courage Burger)", price: "300 pts", type: "勇", icon: "fa-solid fa-burger", isPartner: true, partnerName: "合作商家 C" }, 
     { id: 5, title: "誠信壽司 (Trust Sushi)", price: "450 pts", type: "信", icon: "fa-solid fa-fish", isPartner: true, partnerName: "合作商家 D" }, 
     { id: 6, title: "極限披薩 (Limitless Pizza)", price: "350 pts", type: "勇", icon: "fa-solid fa-pizza-slice", isPartner: true, partnerName: "合作商家 E" }, 
 ]; 
 let currentFilter = '全部'; 
 
 function loadVouchers() { 
     const grid = document.getElementById('voucher-grid'); 
     if (!grid) return; 
     const filteredData = currentFilter === '全部' ? voucherData : voucherData.filter(v => v.type === currentFilter); 
     
     grid.innerHTML = ''; 
     filteredData.forEach(v => { 
         const card = document.createElement('div'); 
         card.className = 'voucher-card'; 
         card.onclick = () => openPurchaseModal(v.id); 
 
         const sourceBadgeClass = v.isPartner ? 'source-badge partner' : 'source-badge renyi'; 
         const sourceBadgeIcon = v.isPartner ? '<i class="fa-solid fa-store"></i>' : '<i class="fa-solid fa-building-columns"></i>'; 
         const sourceBadgeText = v.isPartner ? ' 合作商家 (1:1 Production)' : ' 仁義央行 (Unlimited Minting)'; 
         
         const noteText = v.isPartner 
             ? "消費者回饋同額度票券 (1:1 Exchange)" 
             : "基金池無限額度鑄造權 (Central Bank Authority)"; 
 
         // Safe DOM creation to prevent XSS 
         card.innerHTML = ` 
             <div class="card-img"> 
                 <i class="${v.icon}"></i> <!-- Icon class is internal config, safe --> 
                 <span class="card-tag"></span> 
                 <span class="${sourceBadgeClass}">${sourceBadgeIcon}${sourceBadgeText}</span> 
             </div> 
             <div class="card-body"> 
                 <h3 class="card-title"></h3> 
                 <p class="card-note"></p> 
                 <div class="card-price"></div> 
             </div> 
         `; 
 
         // Set text content safely 
         card.querySelector('.card-tag').textContent = v.type; 
         card.querySelector('.card-title').textContent = v.title; 
         card.querySelector('.card-note').textContent = noteText; 
         card.querySelector('.card-price').textContent = v.price; 
 
         grid.appendChild(card); 
     }); 
 } 
 
 function initFilters() { 
     const buttons = document.querySelectorAll('.filter-btn'); 
     buttons.forEach(btn => { 
         btn.addEventListener('click', () => { 
             buttons.forEach(b => b.classList.remove('active')); 
             btn.classList.add('active'); 
             const typeText = btn.textContent; 
             if (typeText.includes("全部")) currentFilter = '全部'; 
             else if (typeText.includes("仁")) currentFilter = '仁'; 
             else if (typeText.includes("義")) currentFilter = '義'; 
             else if (typeText.includes("智")) currentFilter = '智'; 
             else if (typeText.includes("勇")) currentFilter = '勇'; 
             else if (typeText.includes("信")) currentFilter = '信'; 
             loadVouchers(); 
         }); 
     }); 
 } 
 
 let orderData = [ 
     { id: "#8821", item: "仁心拉麵 x 2", status: "cooking", time: "2 min ago" }, 
     { id: "#8822", item: "智慧咖啡 x 1", status: "pending", time: "5 min ago" }, 
     { id: "#8823", item: "義氣燒肉套餐", status: "pending", time: "12 min ago" } 
 ]; 
 
 function loadMerchantData() { 
     const list = document.getElementById('order-queue'); 
     if (!list) return; 
     list.innerHTML = ''; 
     
     orderData.forEach((o, index) => { 
         const li = document.createElement('li'); 
         li.className = 'order-item'; 
         
         // Safe DOM creation 
         li.innerHTML = ` 
             <div> 
                 <strong></strong> - <span class="order-item-name"></span> 
                 <br><small style="opacity:0.6"></small> 
             </div> 
             <span class="order-status" title="Click to update status"></span> 
         `; 
         
         li.querySelector('strong').textContent = o.id; 
         li.querySelector('.order-item-name').textContent = o.item; 
         li.querySelector('small').textContent = o.time; 
         
         const statusSpan = li.querySelector('.order-status'); 
         statusSpan.classList.add(`status-${o.status}`); 
         statusSpan.textContent = o.status.toUpperCase(); 
         statusSpan.onclick = () => cycleStatus(index); 
         
         list.appendChild(li); 
     }); 
 } 
 
 function cycleStatus(index) { 
     const statuses = ['pending', 'cooking', 'ready', 'completed']; 
     const currentStatus = orderData[index].status; 
     let nextIndex = (statuses.indexOf(currentStatus) + 1) % statuses.length; 
     orderData[index].status = statuses[nextIndex]; 
     saveData(STORAGE_KEYS.ORDERS, orderData); 
     loadMerchantData(); 
 } 
 
 let selectedVoucher = null; 
 
 function initModals() { 
     const purchaseModal = document.getElementById('purchase-modal'); 
     const addModal = document.getElementById('add-voucher-modal'); 
     const closeBtns = document.querySelectorAll('.close-modal'); 
 
     closeBtns.forEach(btn => btn.addEventListener('click', () => { 
         if(purchaseModal) purchaseModal.style.display = 'none'; 
         if(addModal) addModal.style.display = 'none'; 
     })); 
 
     window.addEventListener('click', (e) => { 
         if(e.target == purchaseModal) purchaseModal.style.display = 'none'; 
         if(e.target == addModal) addModal.style.display = 'none'; 
     }); 
 
     const confirmBtn = document.getElementById('confirm-purchase-btn'); 
     if (confirmBtn) { 
         confirmBtn.addEventListener('click', () => { 
             if (selectedVoucher) { 
                 // Secure Flow: Request Honor Check before processing 
                 if (window.littleJ && window.littleJ.requestSandboxAccess) { 
                     // Temporarily close modal to show chat request 
                     if (purchaseModal) purchaseModal.style.display = 'none'; 
                     
                     window.littleJ.requestSandboxAccess("驗證會員等級以記錄交易 (Verify Honor Level)", (approved, token) => { 
                         if (approved) { 
                             // Transaction Approved with Sandbox Token 
                             processTransaction(selectedVoucher, token); 
                         } else { 
                             alert("交易取消：需要會員驗證才能進行 (Transaction Denied)."); 
                         } 
                     }); 
                 } else { 
                     // Fallback for no Little J (should not happen in prod) 
                     processTransaction(selectedVoucher, null); 
                     if (purchaseModal) purchaseModal.style.display = 'none'; 
                 } 
             } 
         }); 
     } 
 
 function processTransaction(voucher, token) { 
     const orderId = "#" + Math.floor(Math.random() * 9000 + 1000); 
     const priceValue = parseInt(voucher.price.replace(' pts', '')); 
 
     const newOrder = { 
         id: orderId, 
         item: voucher.title, 
         status: "deferred", // New initial status 
         time: "Just now", 
         honorVerified: token ? true : false, 
         price: priceValue 
     }; 
     orderData.unshift(newOrder); 
     saveData(STORAGE_KEYS.ORDERS, orderData); 
     
     // Create Deferred Ledger Entry (30% Encumbrance Logic) 
     createLedgerEntry(orderId, priceValue, voucher.isPartner); 
     
     loadMerchantData(); 
 
     // Notify Little J (deferred message) 
     if (window.littleJ) { 
         window.littleJ.addMessage(`訂單 ${orderId} 已列入「遞延性應收帳」。等待轉正核銷後，將解除圈禁並釋放 15% 消費回饋。`, 'agent'); 
     } 
 } 
 
 function createLedgerEntry(orderId, amount, isPartner) { 
     // 30% Encumbrance Logic (Wait for Verification) 
     const encumbranceTotal = Math.floor(amount * 0.3); 
     
     // Breakdown (Inflow/Locked) 
     const consumerDonation = Math.floor(amount * 0.1); // 10% 
     const merchantDonation = Math.floor(amount * 0.2); // 20% 
     
     // Breakdown (Outflow/Release upon Turn Positive) 
     const releaseConsumer = Math.floor(amount * 0.15); // 15% Cashback 
     const releaseVolunteer = Math.floor(amount * 0.06); // 6% 
     const releaseOps = Math.floor(amount * 0.06);       // 6% 
     const releaseWish = Math.floor(amount * 0.015);     // 1.5% 
     const releaseRisk = encumbranceTotal - (releaseConsumer + releaseVolunteer + releaseOps + releaseWish); // Balance (~1.5%) 
 
     const entry = { 
         orderId: orderId, 
         totalAmount: amount, 
         status: 'deferred', // deferred | realized 
         timestamp: Date.now(), 
         encumbrance: { 
             total: encumbranceTotal, 
             consumerIn: consumerDonation, 
             merchantIn: merchantDonation 
         }, 
         release: { 
             consumerOut: releaseConsumer, 
             volunteerOut: releaseVolunteer, 
             opsOut: releaseOps, 
             wishOut: releaseWish, 
             riskOut: releaseRisk 
         } 
     }; 
     
     // Add to top 
     if (!ledgerData) ledgerData = []; 
     ledgerData.unshift(entry); 
     saveData(STORAGE_KEYS.LEDGER, ledgerData); 
 } 
 
 // Admin Function to "Turn Positive" (Release Funds) 
 window.turnPositive = function(orderId) { 
     const entry = ledgerData.find(e => e.orderId === orderId); 
     const order = orderData.find(o => o.id === orderId); 
     
     if (entry && entry.status === 'deferred') { 
         entry.status = 'realized'; 
         saveData(STORAGE_KEYS.LEDGER, ledgerData); 
         
         if (order) { 
             order.status = 'completed'; // or 'realized' 
             saveData(STORAGE_KEYS.ORDERS, orderData); 
         } 
         
         // Refresh UI if on Ledger page 
         if (window.location.href.includes('ledger.html')) { 
             window.location.reload(); 
         } else { 
             loadMerchantData(); // Refresh order list on index 
         } 
 
         if (window.littleJ) { 
             window.littleJ.addMessage(`訂單 ${orderId} 已轉正 (Realized)！<br>消費回饋 ${entry.release.consumerOut} CHC 已注入您的錢包。`, 'agent'); 
         } 
         return true; 
     } 
     return false; 
 }; 
 
     const addBtn = document.getElementById('add-voucher-btn'); 
     if (addBtn) addBtn.addEventListener('click', () => { if(addModal) addModal.style.display = 'block'; }); 
 
     const addForm = document.getElementById('add-voucher-form'); 
     if (addForm) { 
         addForm.addEventListener('submit', (e) => { 
             e.preventDefault(); 
             const name = document.getElementById('v-name').value; 
             const price = document.getElementById('v-price').value; 
             const type = document.getElementById('v-type').value; 
             const icon = document.getElementById('v-icon').value; 
             const newVoucher = { id: Date.now(), title: name, price: price, type: type, icon: icon }; 
             voucherData.push(newVoucher); 
             saveData(STORAGE_KEYS.VOUCHERS, voucherData); 
             loadVouchers(); 
             if (addModal) addModal.style.display = 'none'; 
             
             if (window.littleJ) { 
                 window.littleJ.addMessage(`感謝您上架「${name}」。我們將尋找需要的對象，將這份價值傳遞出去。`, 'agent'); 
             } 
             e.target.reset(); 
         }); 
     } 
 } 
 
 /* --- System Initialization --- */

function initChatWidget() {
    return new Promise((resolve) => {
        const script = document.createElement('script');
        script.src = 'js/chat_widget.js';
        script.onload = () => {
            if (typeof ChatWidget !== 'undefined') {
                window.littleJ = new ChatWidget();
                // Remove old static agent if exists
                const oldAgent = document.getElementById('agent-soulmate'); 
                if (oldAgent) oldAgent.remove();
                resolve();
            }
        };
        document.body.appendChild(script);
    });
}

function initSystemHealer() {
    const script = document.createElement('script');
    script.src = 'js/system_healer.js';
    script.onload = () => {
        if (typeof SystemHealer !== 'undefined' && window.littleJ) {
            window.systemHealer = new SystemHealer(window.littleJ);
        }
    };
    document.body.appendChild(script);
}

function initAegis() {
    const script = document.createElement('script');
    script.src = 'js/aegis.js';
    script.onload = () => {
        if (typeof AegisGuardian !== 'undefined') {
            window.aegis = new AegisGuardian();
        }
    };
    document.body.appendChild(script);
}