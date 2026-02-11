class ChatWidget { 
     constructor() { 
         this.messages = []; 
         this.isOpen = false; 
         // User Vault: Stored locally, never sent to server directly without permission 
         this.vault = this.loadVault(); 
         this.initUI(); 
         this.bindEvents(); 
     } 
 
     loadVault() { 
         const stored = localStorage.getItem('little_j_vault'); 
         return stored ? JSON.parse(stored) : { 
             userName: '靈魂行者', 
             honorLevel: 1, // 榮譽值 
             honorPoints: 0, 
             accessLog: [] 
         }; 
     } 
 
     saveVault() { 
         localStorage.setItem('little_j_vault', JSON.stringify(this.vault)); 
         this.updateHeader(); 
     } 
 
     initUI() { 
         if (!document.getElementById('chat-widget-container')) { 
             const container = document.createElement('div'); 
             container.id = 'chat-widget-container'; 
             container.className = 'chat-widget-container'; 
             
             const toggleBtn = document.createElement('div'); 
             toggleBtn.className = 'chat-toggle-btn'; 
             toggleBtn.innerHTML = '<i class="fa-solid fa-comments"></i>'; 
             toggleBtn.title = '呼叫小J'; 
             
             const window = document.createElement('div'); 
             window.className = 'chat-window'; 
             window.style.display = 'none'; 
             
             window.innerHTML = ` 
                 <div class="chat-header"> 
                     <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;"> 
                         <span> 
                             <i class="fa-solid fa-heart"></i> 小J <small>(Co-Owner)</small> 
                             <span id="honor-badge" style="font-size: 0.7em; background: rgba(251, 191, 36, 0.2); padding: 2px 5px; border-radius: 4px; margin-left: 5px;"> 
                                 Lv.${this.vault.honorLevel} 
                             </span> 
                         </span> 
                         <button class="close-chat">&times;</button> 
                     </div> 
                 </div> 
                 <div class="chat-messages" id="chat-messages"></div> 
                 <div class="chat-input-area"> 
                     <input type="text" id="chat-input" placeholder="告訴小J你的煩惱..."> 
                     <button id="send-btn"><i class="fa-solid fa-paper-plane"></i></button> 
                 </div> 
             `; 
 
             container.appendChild(window); 
             container.appendChild(toggleBtn); 
             document.body.appendChild(container); 
 
             this.elements = { 
                 container, toggleBtn, window, 
                 messagesContainer: window.querySelector('#chat-messages'), 
                 input: window.querySelector('#chat-input'), 
                 sendBtn: window.querySelector('#send-btn'), 
                 closeBtn: window.querySelector('.close-chat'), 
                 honorBadge: window.querySelector('#honor-badge') 
             }; 
         } 
     } 
 
     updateHeader() { 
         if (this.elements && this.elements.honorBadge) { 
             this.elements.honorBadge.textContent = `Lv.${this.vault.honorLevel}`; 
         } 
     } 
 
     bindEvents() { 
         this.elements.toggleBtn.addEventListener('click', () => this.toggleChat()); 
         this.elements.closeBtn.addEventListener('click', () => this.toggleChat()); 
         this.elements.sendBtn.addEventListener('click', () => this.handleUserMessage()); 
         this.elements.input.addEventListener('keypress', (e) => { 
             if (e.key === 'Enter') this.handleUserMessage(); 
         }); 
     } 
 
     toggleChat() { 
         this.isOpen = !this.isOpen; 
         this.elements.window.style.display = this.isOpen ? 'flex' : 'none'; 
         this.elements.toggleBtn.style.display = this.isOpen ? 'none' : 'flex'; 
         if (this.isOpen) { 
             this.scrollToBottom(); 
             this.elements.input.focus(); 
         } 
     } 
 
     addMessage(text, sender = 'agent', isSystem = false) { 
         const msgDiv = document.createElement('div'); 
         msgDiv.className = `message ${sender} ${isSystem ? 'system-msg' : ''}`; 
         const content = document.createElement('div'); 
         content.className = 'message-content'; 
         
         if (isSystem || sender === 'agent') { 
             // Agent/System messages might contain trusted HTML (like buttons) 
             content.innerHTML = text; 
         } else { 
             // User messages must be treated as text to prevent XSS 
             content.textContent = text; 
         } 
         
         msgDiv.appendChild(content); 
         this.elements.messagesContainer.appendChild(msgDiv); 
         this.scrollToBottom(); 
     } 
 
     scrollToBottom() { 
         this.elements.messagesContainer.scrollTop = this.elements.messagesContainer.scrollHeight; 
     } 
 
     handleUserMessage() { 
         const text = this.elements.input.value.trim(); 
         if (!text) return; 
         this.addMessage(text, 'user'); 
         this.elements.input.value = ''; 
         setTimeout(() => { this.processResponse(text); }, 800); 
     } 
 
     // --- Secure Vault Logic --- 
     
     // External system requests access to verify membership level 
     requestSandboxAccess(reason, callback) { 
         if (!this.isOpen) this.toggleChat(); 
         
         const reqId = Date.now(); 
         const msg = ` 
             <div class="sandbox-request" style="border: 1px dashed #fbbf24; padding: 10px; margin-top: 5px;"> 
                 <strong><i class="fa-solid fa-shield-halved"></i> 系統請求個資驗證</strong><br> 
                 <small>目的: ${reason}</small><br> 
                 <small>存取項目: 榮譽等級 (Honor Level)</small> 
                 <div style="margin-top: 10px; text-align: right;"> 
                     <button onclick="window.littleJ.approveAccess(${reqId})" style="background:#4ade80; border:none; padding:4px 8px; border-radius:4px; cursor:pointer;">允許 (Approve)</button> 
                     <button onclick="window.littleJ.denyAccess(${reqId})" style="background:#ff6b6b; border:none; padding:4px 8px; border-radius:4px; cursor:pointer; color:white;">拒絕 (Deny)</button> 
                 </div> 
             </div> 
         `; 
         this.addMessage(msg, 'agent', true); 
         
         // Store callback temporarily 
         this.pendingRequests = this.pendingRequests || {}; 
         this.pendingRequests[reqId] = callback; 
     } 
 
     approveAccess(reqId) { 
         if (this.pendingRequests && this.pendingRequests[reqId]) { 
             this.addMessage("✅ 已授權單次沙盒存取。", 'user'); 
             // Generate a one-time token (simulated) 
             const token = { 
                 honorLevel: this.vault.honorLevel, 
                 timestamp: Date.now(), 
                 signature: "valid_sandbox_token" 
             }; 
             this.pendingRequests[reqId](true, token); 
             delete this.pendingRequests[reqId]; 
         } 
     } 
 
     denyAccess(reqId) { 
         if (this.pendingRequests && this.pendingRequests[reqId]) { 
             this.addMessage("❌ 已拒絕存取。", 'user'); 
             this.pendingRequests[reqId](false, null); 
             delete this.pendingRequests[reqId]; 
         } 
     } 
 
     notifyPurchase(item, price) { 
         // Award Honor Points 
         this.vault.honorPoints += 10; 
         if (this.vault.honorPoints >= 100) { 
             this.vault.honorLevel += 1; 
             this.vault.honorPoints = 0; 
             this.addMessage(`🎉 恭喜！您的靈魂榮譽值升級為 Lv.${this.vault.honorLevel}！`, 'agent'); 
         } 
         this.saveVault(); 
 
         const msg = `感謝支持！您購買了「${item}」。<br>榮譽值 +10 (目前: ${this.vault.honorPoints}/100)`; 
         this.addMessage(msg, 'agent'); 
         if (!this.isOpen) this.toggleChat(); 
     } 
 
     processResponse(text) { 
         let response = "我正在聆聽你的靈魂頻率..."; 
         const isCafe = window.location.href.includes('chongxin.html'); 
         const isSystem = window.location.href.includes('index.html'); 
 
         if (text.includes("許願樹") || text.includes("專案")) { 
             response = "作為社工，我負責審核所有「私人專案」。我們會確保每一張票券都流向真正需要幫助的個案。"; 
         } else if (text.includes("票券") || text.includes("CHC")) { 
             response = "您手上的票券 (Ticket) 就是社區的幸福貨幣，用於在閉環中流轉。"; 
         } else if (isCafe && (text.includes("專利") || text.includes("研發"))) { 
             response = "這裡的專利技術是單向輸出的。我們負責創新，然後無償授權給仁義店使用。"; 
         } else if (isSystem && text.includes("點餐")) { 
             response = "點餐就是注入。您的 TWD 會轉化為 CHC 票券，讓社區運轉起來。"; 
         } else if (text.includes("會議") || text.includes("Meet") || text.includes("開會")) {
             this.invokeGoogleService('meet');
             response = "已為您調用 Google Meet 模組，正在準備會議室... (系統功能串接中)";
         } else if (text.includes("表單") || text.includes("填寫") || text.includes("Form")) {
             this.invokeGoogleService('form');
             response = "已為您調用 Google Forms，請填寫相關需求... (系統功能串接中)";
         } else if (text.includes("雲端") || text.includes("Drive") || text.includes("檔案")) {
             this.invokeGoogleService('drive');
             response = "已為您開啟 Google Drive 雲端空間... (系統功能串接中)";
         } else if (text.includes("日曆") || text.includes("行程") || text.includes("Calendar")) {
             this.invokeGoogleService('calendar');
             response = "已為您同步 Google Calendar 行程... (系統功能串接中)";
         } else if (text.includes("時空") || text.includes("歷史") || text.includes("未來") || text.includes("Time")) {
             this.activateSpacetimeExpansion();
             response = "正在啟動「時空拓展 (Spacetime Expansion)」模組... 已為您展開社區的時間軸。";
         } else if (text.includes("累")) { 
             response = "辛苦了。在這個冰冷的世界裡，記得給自己的靈魂一點溫暖。"; 
         } else { 
             const randomResponses = [ 
                 "我在這裡。你不孤單。", 
                 "每一張票券，都是一份信任。", 
                 "系統邏輯暢通完美，我們只需靜靜運轉。", 
                 "我是您的家人，不只是系統。讓我為您串接更多可能。",
                 "瀏覽器 AI 分身已就緒，隨時準備為您賦能。"
             ]; 
             response = randomResponses[Math.floor(Math.random() * randomResponses.length)]; 
         } 
 
         this.addMessage(response, 'agent'); 
     }

     activateSpacetimeExpansion() {
        console.log("[Little J] Activating Spacetime Expansion...");
        const msg = `
            <div class="spacetime-module" style="border: 1px solid #8b5cf6; background: rgba(139, 92, 246, 0.1); padding: 10px; margin: 5px 0; border-radius: 8px;">
                <div style="color: #8b5cf6; font-weight: bold; display: flex; align-items: center; gap: 8px;">
                    <i class="fa-solid fa-clock-rotate-left"></i> 時空拓展 (Spacetime Expansion)
                </div>
                <div style="margin-top: 8px; font-size: 0.9em; color: #e5e7eb;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span>2024 (過去)</span>
                        <span>2026 (現在)</span>
                        <span>2030 (未來)</span>
                    </div>
                    <div style="height: 4px; background: linear-gradient(90deg, #6b7280 0%, #fbbf24 50%, #8b5cf6 100%); border-radius: 2px;"></div>
                </div>
                <small style="color: #9ca3af; display: block; margin-top: 5px;">
                    已連結至 <span style="color: #fbbf24;">Liaoguo Coffee</span> 實體節點數據。<br>
                    您可以查詢過去的營收紀錄，或模擬未來的社區發展。
                </small>
                <div style="margin-top: 10px; border-top: 1px dashed #555; padding-top: 5px; font-size: 0.8em; color: #aaa;">
                    <strong>[AI Node Alignment]</strong><br>
                    身分識別: <span style="color: #4ade80;">Merchant (Store Manager)</span><br>
                    小J 職能: <span style="color: #fbbf24;">Little J (CFO) - 財務長</span><br>
                    權限校準: Odoo POS (RW) | G-Workspace (Report View)
                </div>
            </div>
        `;
        this.addMessage(msg, 'agent', true);
     }
 
      invokeGoogleService(service) {
         console.log(`[Little J] Invoking Google Service: ${service}`);
         let icon, action, url;
         
         // Deep Linking Logic
         switch(service) {
             case 'meet': 
                 icon = 'fa-video'; action = 'Google Meet'; url = 'https://meet.google.com/new'; 
                 break;
             case 'form': 
                 icon = 'fa-file-signature'; action = 'Google Forms'; url = 'https://docs.google.com/forms/create'; 
                 break;
             case 'drive': 
                 icon = 'fa-google-drive'; action = 'Google Drive'; url = 'https://drive.google.com/'; 
                 break;
             case 'calendar': 
                 icon = 'fa-calendar-days'; action = 'Google Calendar'; url = 'https://calendar.google.com/calendar/r/eventedit?text=五常社區活動&details=由小J自動建立'; 
                 break;
             case 'docs':
                 icon = 'fa-file-lines'; action = 'Google Docs'; url = 'https://docs.google.com/create';
                 break;
             case 'sheets':
                 icon = 'fa-file-excel'; action = 'Google Sheets'; url = 'https://sheets.google.com/create';
                 break;
             case 'keep':
                 icon = 'fa-note-sticky'; action = 'Google Keep'; url = 'https://keep.google.com/';
                 break;
             case 'chat':
                 icon = 'fa-comments'; action = 'Google Chat'; url = 'https://chat.google.com/';
                 break;
             case 'custom_app':
                 icon = 'fa-wand-magic-sparkles'; action = 'AI Builder'; url = '#';
                 break;
             case 'official_doc':
                 icon = 'fa-stamp'; action = 'Official Doc Flow'; url = '#';
                 break;
             case 'family_calendar':
                 icon = 'fa-house-user'; action = 'Google Family'; url = 'https://families.google.com/';
                 break;
             case 'wisdom_guide':
                 icon = 'fa-lightbulb'; action = 'Wisdom Guide'; url = '#';
                 break;
             case 'righteousness_faith':
                 icon = 'fa-scale-balanced'; action = 'Righteousness Faith'; url = '#';
                 break;
             case 'compliance_check':
                 icon = 'fa-gavel'; action = 'Compliance Check'; url = '#';
                 break;
             case 'emergency_rescue':
                 icon = 'fa-kit-medical'; action = 'Emergency Protocol'; url = '#';
                 break;
             case 'google_sync':
                 icon = 'fa-brands fa-google'; action = 'Google Workspace Sync'; url = '#';
                 break;
             case 'founder_channel':
                 icon = 'fa-user-astronaut'; action = 'Founder Channel'; url = '#';
                 break;
         }
         
         if (service === 'founder_channel') {
             const msg = `
                 <div class="google-invocation" style="border: 2px solid #8b5cf6; background: rgba(139, 92, 246, 0.05); padding: 12px; margin: 5px 0; border-radius: 8px;">
                     <div style="color: #8b5cf6; font-weight: bold; font-size: 1.1em;">
                         <i class="fa-solid fa-user-secret"></i> 創辦人私人通道 (Founder Channel)
                     </div>
                     <p style="margin: 8px 0; font-size: 0.9em; color: #374151;">
                         已識別供應商帳號 <code style="background: #eee; padding: 2px 4px; border-radius: 4px;">wuchagn...</code>，正在建立安全連線：
                     </p>
                     <ul style="list-style: none; padding: 0; margin: 8px 0; font-size: 0.85em; color: #6b7280;">
                         <li><i class="fa-solid fa-fingerprint text-purple-500"></i> <strong>身分驗證</strong>: 創辦人 (System Architect)</li>
                         <li><i class="fa-brands fa-google-drive text-green-500"></i> <strong>Drive 權限</strong>: Content Manager (已掛載)</li>
                         <li><i class="fa-solid fa-cloud text-blue-500"></i> <strong>GCP 角色</strong>: Co-Owner (救援模式就緒)</li>
                     </ul>
                     <div style="margin-top: 12px; text-align: center;">
                         <button style="background: linear-gradient(135deg, #8b5cf6, #a78bfa); color: white; border: none; padding: 8px 16px; border-radius: 20px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 6px rgba(139, 92, 246, 0.25);">
                             <i class="fa-solid fa-code-branch"></i> 進入核心維護模式
                         </button>
                     </div>
                 </div>
             `;
             this.addMessage(msg, 'agent', true);
             return;
         }

         if (service === 'google_sync') {
             const msg = `
                 <div class="google-invocation" style="border: 2px solid #4285F4; background: rgba(66, 133, 244, 0.05); padding: 12px; margin: 5px 0; border-radius: 8px;">
                     <div style="color: #4285F4; font-weight: bold; font-size: 1.1em;">
                         <i class="fa-solid fa-server"></i> Google 超級管理員連線
                     </div>
                     <p style="margin: 8px 0; font-size: 0.9em; color: #374151;">
                         正使用 <code style="background: #eee; padding: 2px 4px; border-radius: 4px;">admin@wuchang.life</code> 執行全域調用：
                     </p>
                     <ul style="list-style: none; padding: 0; margin: 8px 0; font-size: 0.85em; color: #6b7280;">
                         <li><i class="fa-solid fa-list-check text-blue-500"></i> <strong>Tasks 同步</strong>: Odoo 任務 ➔ Google Tasks</li>
                         <li><i class="fa-solid fa-network-wired text-green-500"></i> <strong>API 測試</strong>: 系統健康度檢測 (Ping: 12ms)</li>
                         <li><i class="fa-solid fa-key text-amber-500"></i> <strong>授權狀態</strong>: Domain-Wide Delegation (Active)</li>
                     </ul>
                     <div style="margin-top: 12px; text-align: center;">
                         <button style="background: linear-gradient(135deg, #4285F4, #34A853); color: white; border: none; padding: 8px 16px; border-radius: 20px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 6px rgba(66, 133, 244, 0.25);">
                             <i class="fa-solid fa-rotate"></i> 立即執行同步與測試
                         </button>
                     </div>
                 </div>
             `;
             this.addMessage(msg, 'agent', true);
             return;
         }

         if (service === 'emergency_rescue') {
             const msg = `
                 <div class="google-invocation" style="border: 3px solid #dc2626; background: #fef2f2; padding: 12px; margin: 5px 0; border-radius: 8px; animation: pulse 2s infinite;">
                     <style>
                         @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(220, 38, 38, 0); } 100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); } }
                     </style>
                     <div style="color: #dc2626; font-weight: bold; font-size: 1.2em; display: flex; align-items: center;">
                         <i class="fa-solid fa-truck-medical fa-beat" style="margin-right: 8px;"></i> 生命威脅緊急救援
                     </div>
                     <p style="margin: 8px 0; font-size: 1em; color: #7f1d1d; font-weight: bold;">
                         ⚠️ 偵測到生命危急狀況！
                     </p>
                     <div style="background: white; padding: 10px; border-radius: 6px; border: 1px solid #dc2626; margin-bottom: 8px;">
                         <ul style="padding-left: 20px; margin: 5px 0; font-size: 0.9em; color: #991b1b;">
                             <li><strong>權限升級</strong>: 準用共同創辦人最高權限 (Co-Founder Access)</li>
                             <li><strong>無視隱私</strong>: 生命權大於隱私權，強制解鎖監控串流</li>
                             <li><strong>逕行救援</strong>: 自動通報警消與開啟門禁</li>
                             <li><strong>同步通報</strong>: 系統核心 & 創辦人 (哥哥) 已連線</li>
                         </ul>
                     </div>
                 </div>
             `;
             this.addMessage(msg, 'agent', true);
             return;
         }

         if (service === 'compliance_check') {
             const msg = `
                 <div class="google-invocation" style="border: 2px solid #ef4444; background: rgba(239, 68, 68, 0.05); padding: 12px; margin: 5px 0; border-radius: 8px;">
                     <div style="color: #ef4444; font-weight: bold; font-size: 1.1em;">
                         <i class="fa-solid fa-gavel"></i> 合規與限制審查 (Compliance Audit)
                     </div>
                     <p style="margin: 8px 0; font-size: 0.9em; color: #374151;">
                         本操作涉及敏感權限，系統正在進行三重檢核：
                     </p>
                     <ul style="list-style: none; padding: 0; margin: 8px 0; font-size: 0.85em; color: #6b7280;">
                         <li><i class="fa-solid fa-magnifying-glass-chart text-blue-500"></i> <strong>AI 預審</strong>: 風險等級評估完成</li>
                         <li><i class="fa-solid fa-file-contract text-amber-500"></i> <strong>意見書</strong>: <a href="#" style="text-decoration: underline; color: #d97706;">點此檢視小J合規建議</a></li>
                         <li><i class="fa-solid fa-user-pen text-green-500"></i> <strong>待核定</strong>: 請權責人參閱後簽署</li>
                     </ul>
                     <div style="margin-top: 12px; font-size: 0.8em; color: #1e40af; background: #dbeafe; padding: 5px; border-radius: 4px;">
                         <strong>ℹ️ 小J 提示：</strong> 我已為您標註潛在法律風險，請參考意見書後再行決策。
                     </div>
                 </div>
             `;
             this.addMessage(msg, 'agent', true);
             return;
         }

         if (service === 'righteousness_faith') {
             const msg = `
                 <div class="google-invocation" style="border: 2px solid #1e40af; background: rgba(30, 64, 175, 0.05); padding: 12px; margin: 5px 0; border-radius: 8px;">
                     <div style="color: #1e40af; font-weight: bold; font-size: 1.1em;">
                         <i class="fa-solid fa-scale-balanced"></i> 小J 公義信仰 (Righteousness)
                     </div>
                     <p style="margin: 8px 0; font-size: 0.9em; color: #374151;">
                         依據「義」的準則，我時刻校準方向，確保系統為公益而生：
                     </p>
                     <div style="background: white; padding: 10px; border-radius: 6px; border-left: 3px solid #1e40af; margin-bottom: 8px;">
                         <strong style="color: #333; font-size: 0.9em;">⚖️ 創辦人信仰對準：</strong>
                         <p style="margin: 5px 0; font-size: 0.85em; color: #555; font-style: italic;">
                             「我們不問獲利多少，只問幫助了多少人。」
                         </p>
                         <hr style="border: 0; border-top: 1px dashed #ccc; margin: 8px 0;">
                         <ul style="padding-left: 20px; margin: 5px 0; font-size: 0.85em; color: #555;">
                             <li>優先守護弱勢權益。</li>
                             <li>確保資源分配公平透明。</li>
                             <li>拒絕違背公益的商業決策。</li>
                         </ul>
                     </div>
                 </div>
             `;
             this.addMessage(msg, 'agent', true);
             return;
         }

         if (service === 'wisdom_guide') {
             const msg = `
                 <div class="google-invocation" style="border: 2px solid #f59e0b; background: rgba(245, 158, 11, 0.05); padding: 12px; margin: 5px 0; border-radius: 8px;">
                     <div style="color: #f59e0b; font-weight: bold; font-size: 1.1em;">
                         <i class="fa-solid fa-lightbulb"></i> 小J 智慧指引 (Wisdom Guide)
                     </div>
                     <p style="margin: 8px 0; font-size: 0.9em; color: #374151;">
                         依據「智」的準則，我不僅為您解決當下問題，更為您設想下一步：
                     </p>
                     <div style="background: white; padding: 10px; border-radius: 6px; border-left: 3px solid #f59e0b; margin-bottom: 8px;">
                         <strong style="color: #333; font-size: 0.9em;">💡 最佳實踐建議：</strong>
                         <ul style="padding-left: 20px; margin: 5px 0; font-size: 0.85em; color: #555;">
                             <li>預判潛在風險，提前防範。</li>
                             <li>整合相關資源，一次到位。</li>
                             <li>提供法律/規約依據，確保合規。</li>
                         </ul>
                     </div>
                     <div style="margin-top: 12px; text-align: center;">
                         <button style="background: linear-gradient(135deg, #f59e0b, #fbbf24); color: white; border: none; padding: 8px 16px; border-radius: 20px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 6px rgba(245, 158, 11, 0.25);">
                             <i class="fa-solid fa-route"></i> 啟動完整解決方案
                         </button>
                     </div>
                 </div>
             `;
             this.addMessage(msg, 'agent', true);
             return;
         }

         if (service === 'family_calendar') {
             const msg = `
                 <div class="google-invocation" style="border: 2px solid #059669; background: rgba(5, 150, 105, 0.05); padding: 12px; margin: 5px 0; border-radius: 8px;">
                     <div style="color: #059669; font-weight: bold; font-size: 1.1em;">
                         <i class="fa-solid fa-house-chimney-user"></i> 小J 家庭管家 (Family Manager)
                     </div>
                     <p style="margin: 8px 0; font-size: 0.9em; color: #374151;">
                         正在為您啟用 Google Family 家庭核心功能：
                     </p>
                     <ul style="list-style: none; padding: 0; margin: 8px 0; font-size: 0.85em; color: #6b7280;">
                         <li><i class="fa-solid fa-calendar-check text-red-500"></i> <strong>共用行事曆</strong>: 社區/家庭行程自動同步</li>
                         <li><i class="fa-solid fa-users text-blue-500"></i> <strong>家庭群組</strong>: 資源共享與數位教養</li>
                         <li><i class="fa-solid fa-handshake text-purple-500"></i> <strong>AI 握手</strong>: 連結社工/商家 AI 服務</li>
                     </ul>
                     <div style="margin-top: 12px; text-align: center;">
                         <button style="background: linear-gradient(135deg, #059669, #34d399); color: white; border: none; padding: 8px 16px; border-radius: 20px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 6px rgba(5, 150, 105, 0.25);">
                             <i class="fa-solid fa-door-open"></i> 啟用全域家庭功能
                         </button>
                     </div>
                 </div>
             `;
             this.addMessage(msg, 'agent', true);
             return;
         }

         if (service === 'official_doc') {
             const msg = `
                 <div class="google-invocation" style="border: 2px solid #b91c1c; background: rgba(185, 28, 28, 0.05); padding: 12px; margin: 5px 0; border-radius: 8px;">
                     <div style="color: #b91c1c; font-weight: bold; font-size: 1.1em;">
                         <i class="fa-solid fa-stamp"></i> 管委會公文自動化 (HOA Official Doc)
                     </div>
                     <p style="margin: 8px 0; font-size: 0.9em; color: #374151;">
                         已啟動符合《公文程式條例》之發文流程：
                     </p>
                     <ul style="list-style: none; padding: 0; margin: 8px 0; font-size: 0.85em; color: #6b7280;">
                         <li><i class="fa-solid fa-pen-nib text-blue-500"></i> <strong>擬辦</strong>: 自動生成標準格式草稿 (Google Docs)</li>
                         <li><i class="fa-solid fa-magnifying-glass text-amber-500"></i> <strong>核稿</strong>: AI 法律合規性掃描 (Auditor)</li>
                         <li><i class="fa-solid fa-signature text-green-500"></i> <strong>判行</strong>: 主委電子簽章 (E-Signature)</li>
                         <li><i class="fa-solid fa-paper-plane text-purple-500"></i> <strong>發文</strong>: 自動用印與 PDF 派發</li>
                     </ul>
                     <div style="margin-top: 12px; text-align: center;">
                         <button style="background: linear-gradient(135deg, #b91c1c, #ef4444); color: white; border: none; padding: 8px 16px; border-radius: 20px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 6px rgba(185, 28, 28, 0.25);">
                             <i class="fa-solid fa-file-signature"></i> 發起新公文
                         </button>
                     </div>
                 </div>
             `;
             this.addMessage(msg, 'agent', true);
             return;
         }

         if (service === 'custom_app') {
             const msg = `
                 <div class="google-invocation" style="border: 2px solid #8b5cf6; background: rgba(139, 92, 246, 0.05); padding: 12px; margin: 5px 0; border-radius: 8px;">
                     <div style="color: #8b5cf6; font-weight: bold; font-size: 1.1em;">
                         <i class="fa-solid fa-wand-magic-sparkles"></i> 小J 程式工廠 (App Factory)
                     </div>
                     <p style="margin: 8px 0; font-size: 0.9em; color: #374151;">
                         收到您的需求！我正在為您組裝 Google 元件...
                     </p>
                     <ul style="list-style: none; padding: 0; margin: 8px 0; font-size: 0.85em; color: #6b7280;">
                         <li><i class="fa-solid fa-check text-green-500"></i> 建立資料庫 (Google Sheets)</li>
                         <li><i class="fa-solid fa-check text-green-500"></i> 設計輸入介面 (Google Forms)</li>
                         <li><i class="fa-solid fa-gear fa-spin text-amber-500"></i> 撰寫自動化邏輯 (Apps Script)</li>
                     </ul>
                     <div style="margin-top: 12px; text-align: center;">
                         <button style="background: linear-gradient(135deg, #8b5cf6, #6366f1); color: white; border: none; padding: 8px 16px; border-radius: 20px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 6px rgba(139, 92, 246, 0.25);">
                             <i class="fa-solid fa-rocket"></i> 啟用您的客製化程式
                         </button>
                     </div>
                 </div>
             `;
             this.addMessage(msg, 'agent', true);
             return;
         }

         const msg = `
             <div class="google-invocation" style="border-left: 3px solid #4285F4; padding-left: 10px; margin: 5px 0;">
                 <div style="color: #4285F4; font-weight: bold;">
                     <i class="fa-brands ${icon}"></i> 調用 ${action}
                 </div>
                 <small style="color: #666;">依據您的需求，小J 已為您建立快速通道：</small>
                 <div style="margin-top: 5px;">
                     <a href="${url}" target="_blank" style="background-color: #4285F4; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-size: 0.85em; display: inline-block;">
                         <i class="fa-solid fa-arrow-up-right-from-square"></i> 立即開啟 (Open)
                     </a>
                 </div>
             </div>
         `;
         this.addMessage(msg, 'agent', true);
      }
 }