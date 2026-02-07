"""
小 J 全局浮動圖示模組
透明圓形圖示，始終顯示在所有系統最上層
"""

# 小 J 浮動圖示 HTML/CSS/JS
LITTLE_J_FLOATING_ICON = """
<!-- 小 J 全局浮動圖示 -->
<div id="littleJIcon" class="little-j-icon">
    <div class="little-j-circle">
        <div class="little-j-content">
            <div class="little-j-avatar" id="littleJAvatar">
                <!-- 白色頭髮頭像 - 如果圖片存在則顯示，否則顯示 emoji -->
                <img src="/static/little_j_white_hair.png" 
                     alt="小 J" 
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='block';"
                     style="display: block; width: 100%; height: 100%; object-fit: cover; border-radius: 50%; border: none; outline: none; padding: 0; margin: 0;">
                <span style="display: none;">🤖</span>
            </div>
            <div class="little-j-status" id="littleJStatus">
                <div class="status-dot"></div>
            </div>
        </div>
    </div>
    <div class="little-j-tooltip" id="littleJTooltip">
        <div class="tooltip-content">
            <div class="tooltip-header">
                <strong>小 J 服務</strong>
                <span class="tooltip-status" id="tooltipStatus">運行中</span>
            </div>
            <div class="tooltip-body">
                <div class="tooltip-item">
                    <span>狀態:</span>
                    <span id="tooltipState">正常</span>
                </div>
                <div class="tooltip-item">
                    <span>執行次數:</span>
                    <span id="tooltipCount">0</span>
                </div>
                <div class="tooltip-item">
                    <span>最後活動:</span>
                    <span id="tooltipLast">剛剛</span>
                </div>
            </div>
            <div class="tooltip-actions">
                <button onclick="openLittleJPanel()">打開面板</button>
                <button onclick="executeLittleJ()">執行任務</button>
            </div>
        </div>
    </div>
</div>

<style>
/* ============================================
   小 J 全局浮動圖示樣式
   ============================================ */

.little-j-icon {
    position: fixed;
    bottom: 30px;
    right: 30px;
    z-index: 999999; /* 最高層級，確保在所有內容之上 */
    cursor: pointer;
    user-select: none;
    transition: all 0.3s ease;
}

/* 圓形圖示 */
.little-j-circle {
    width: 70px;
    height: 70px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3),
                0 0 0 3px rgba(255, 255, 255, 0.1),
                inset 0 1px 1px rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    transition: all 0.3s ease;
    border: 2px solid rgba(255, 255, 255, 0.2);
}

.little-j-circle:hover {
    transform: scale(1.1);
    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.5),
                inset 0 1px 1px rgba(255, 255, 255, 0.3);
}

.little-j-circle:active {
    transform: scale(0.95);
}

/* 內容區域 */
.little-j-content {
    position: relative;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%; /* 確保內容也是圓形 */
    overflow: hidden; /* 隱藏超出部分 */
}

/* 頭像/圖示 */
.little-j-avatar {
    font-size: 2.5em;
    line-height: 1;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
    animation: float 3s ease-in-out infinite;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    border-radius: 50%; /* 圓形 */
    overflow: hidden; /* 隱藏超出部分 */
}

/* 白色頭髮頭像圖片 - 圓形無邊界 */
.little-j-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover; /* 覆蓋整個區域 */
    border-radius: 50%; /* 圓形 */
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
    border: none; /* 無邊界 */
    outline: none; /* 無外框 */
    padding: 0; /* 無內邊距 */
    margin: 0; /* 無外邊距 */
    display: block; /* 塊級元素 */
}

@keyframes float {
    0%, 100% {
        transform: translateY(0px);
    }
    50% {
        transform: translateY(-5px);
    }
}

/* 狀態指示器 */
.little-j-status {
    position: absolute;
    top: 5px;
    right: 5px;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #28a745;
    animation: pulse 2s ease-in-out infinite;
}

.status-dot.warning {
    background: #ffc107;
}

.status-dot.error {
    background: #dc3545;
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
        transform: scale(1);
    }
    50% {
        opacity: 0.7;
        transform: scale(1.1);
    }
}

/* 工具提示 */
.little-j-tooltip {
    position: absolute;
    bottom: 90px;
    right: 0;
    width: 280px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 15px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3),
                0 0 0 1px rgba(255, 255, 255, 0.5);
    padding: 0;
    opacity: 0;
    visibility: hidden;
    transform: translateY(10px) scale(0.95);
    transition: all 0.3s ease;
    pointer-events: none;
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.little-j-icon:hover .little-j-tooltip,
.little-j-icon.active .little-j-tooltip {
    opacity: 1;
    visibility: visible;
    transform: translateY(0) scale(1);
    pointer-events: auto;
}

.tooltip-content {
    padding: 15px;
}

.tooltip-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.tooltip-header strong {
    font-size: 1.1em;
    color: #333;
}

.tooltip-status {
    font-size: 0.85em;
    padding: 4px 10px;
    background: #28a745;
    color: white;
    border-radius: 12px;
}

.tooltip-status.warning {
    background: #ffc107;
    color: #333;
}

.tooltip-status.error {
    background: #dc3545;
}

.tooltip-body {
    margin-bottom: 12px;
}

.tooltip-item {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    font-size: 0.9em;
    color: #666;
}

.tooltip-item span:first-child {
    color: #999;
}

.tooltip-item span:last-child {
    font-weight: 500;
    color: #333;
}

.tooltip-actions {
    display: flex;
    gap: 8px;
    margin-top: 10px;
}

.tooltip-actions button {
    flex: 1;
    padding: 8px 12px;
    border: none;
    border-radius: 8px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-size: 0.85em;
    cursor: pointer;
    transition: all 0.2s ease;
}

.tooltip-actions button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.tooltip-actions button:active {
    transform: translateY(0);
}

/* 響應式設計 */
@media (max-width: 768px) {
    .little-j-icon {
        bottom: 20px;
        right: 20px;
    }
    
    .little-j-circle {
        width: 60px;
        height: 60px;
    }
    
    .little-j-avatar {
        font-size: 2em;
    }
    
    .little-j-tooltip {
        width: 250px;
        bottom: 80px;
    }
}

@media (max-width: 480px) {
    .little-j-icon {
        bottom: 15px;
        right: 15px;
    }
    
    .little-j-circle {
        width: 55px;
        height: 55px;
    }
    
    .little-j-avatar {
        font-size: 1.8em;
    }
    
    .little-j-tooltip {
        width: 220px;
        right: -10px;
    }
}

/* 拖動功能 */
.little-j-icon.dragging {
    cursor: grabbing;
}

.little-j-icon.draggable {
    cursor: grab;
}

/* 動畫效果 */
@keyframes bounce {
    0%, 100% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(-10px);
    }
}

.little-j-icon.notification {
    animation: bounce 0.5s ease;
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
    .little-j-tooltip {
        background: rgba(30, 30, 30, 0.95);
        border-color: rgba(255, 255, 255, 0.1);
    }
    
    .tooltip-header strong {
        color: #fff;
    }
    
    .tooltip-item {
        color: #ccc;
    }
    
    .tooltip-item span:last-child {
        color: #fff;
    }
}
</style>

<script>
// 小 J 浮動圖示 JavaScript
(function() {
    const icon = document.getElementById('littleJIcon');
    const tooltip = document.getElementById('littleJTooltip');
    const statusDot = document.querySelector('.status-dot');
    const tooltipStatus = document.getElementById('tooltipStatus');
    const tooltipState = document.getElementById('tooltipState');
    const tooltipCount = document.getElementById('tooltipCount');
    const tooltipLast = document.getElementById('tooltipLast');
    
    // 初始化
    let isDragging = false;
    let currentX, currentY, initialX, initialY;
    let xOffset = 0, yOffset = 0;
    
    // 從 localStorage 讀取位置
    const savedPosition = localStorage.getItem('littleJPosition');
    if (savedPosition) {
        const pos = JSON.parse(savedPosition);
        icon.style.right = pos.right + 'px';
        icon.style.bottom = pos.bottom + 'px';
        xOffset = pos.xOffset || 0;
        yOffset = pos.yOffset || 0;
    }
    
    // 點擊圖示
    icon.addEventListener('click', function(e) {
        if (!isDragging) {
            icon.classList.toggle('active');
            updateLittleJStatus();
        }
    });
    
    // 拖動功能
    icon.addEventListener('mousedown', dragStart);
    icon.addEventListener('touchstart', dragStart);
    
    document.addEventListener('mousemove', drag);
    document.addEventListener('touchmove', drag);
    
    document.addEventListener('mouseup', dragEnd);
    document.addEventListener('touchend', dragEnd);
    
    function dragStart(e) {
        if (e.type === 'touchstart') {
            initialX = e.touches[0].clientX - xOffset;
            initialY = e.touches[0].clientY - yOffset;
        } else {
            initialX = e.clientX - xOffset;
            initialY = e.clientY - yOffset;
        }
        
        if (e.target === icon || icon.contains(e.target)) {
            isDragging = true;
            icon.classList.add('dragging');
        }
    }
    
    function drag(e) {
        if (isDragging) {
            e.preventDefault();
            
            if (e.type === 'touchmove') {
                currentX = e.touches[0].clientX - initialX;
                currentY = e.touches[0].clientY - initialY;
            } else {
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;
            }
            
            xOffset = currentX;
            yOffset = currentY;
            
            setTranslate(currentX, currentY, icon);
        }
    }
    
    function dragEnd(e) {
        initialX = currentX;
        initialY = currentY;
        isDragging = false;
        icon.classList.remove('dragging');
        
        // 保存位置
        const rect = icon.getBoundingClientRect();
        const right = window.innerWidth - rect.right;
        const bottom = window.innerHeight - rect.bottom;
        localStorage.setItem('littleJPosition', JSON.stringify({
            right: right,
            bottom: bottom,
            xOffset: xOffset,
            yOffset: yOffset
        }));
    }
    
    function setTranslate(xPos, yPos, el) {
        el.style.transform = `translate(${xPos}px, ${yPos}px)`;
    }
    
    // 更新小 J 狀態
    function updateLittleJStatus() {
        fetch('/api/ai/settings')
            .then(response => response.json())
            .then(data => {
                if (data.error) return;
                
                // 更新狀態點
                const status = data.ai_program_status?.running ? 'success' : 
                              data.ai_program_status?.error ? 'error' : 'warning';
                statusDot.className = 'status-dot ' + (status !== 'success' ? status : '');
                
                // 更新工具提示
                tooltipStatus.textContent = status === 'success' ? '運行中' : 
                                          status === 'error' ? '錯誤' : '待機';
                tooltipStatus.className = 'tooltip-status ' + (status !== 'success' ? status : '');
                
                tooltipState.textContent = status === 'success' ? '正常' : 
                                         status === 'error' ? '異常' : '待機';
                tooltipCount.textContent = data.ai_program_status?.execution_count || 0;
                
                // 更新最後活動時間
                if (data.ai_program_status?.last_execution) {
                    const lastTime = new Date(data.ai_program_status.last_execution);
                    const now = new Date();
                    const diff = Math.floor((now - lastTime) / 1000);
                    if (diff < 60) {
                        tooltipLast.textContent = '剛剛';
                    } else if (diff < 3600) {
                        tooltipLast.textContent = Math.floor(diff / 60) + '分鐘前';
                    } else {
                        tooltipLast.textContent = Math.floor(diff / 3600) + '小時前';
                    }
                } else {
                    tooltipLast.textContent = '--';
                }
            })
            .catch(error => {
                console.error('更新小 J 狀態失敗:', error);
            });
    }
    
    // 打開小 J 面板
    window.openLittleJPanel = function() {
        // 可以打開全屏面板或導航到 AI 儀表板
        window.location.href = '#ai-dashboard';
        // 或者觸發自定義事件
        window.dispatchEvent(new CustomEvent('openLittleJPanel'));
    };
    
    // 執行小 J 任務
    window.executeLittleJ = function() {
        fetch('/api/ai/execute', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                program: 'ai_little_j',
                parameters: {}
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 顯示通知動畫
                icon.classList.add('notification');
                setTimeout(() => {
                    icon.classList.remove('notification');
                }, 500);
                
                // 更新狀態
                setTimeout(updateLittleJStatus, 1000);
            }
        })
        .catch(error => {
            console.error('執行小 J 任務失敗:', error);
        });
    };
    
    // 定期更新狀態
    setInterval(updateLittleJStatus, 5000);
    
    // 初始更新
    updateLittleJStatus();
    
    // 監聽全局事件
    window.addEventListener('littleJStatusUpdate', function(e) {
        updateLittleJStatus();
    });
})();
</script>
"""
