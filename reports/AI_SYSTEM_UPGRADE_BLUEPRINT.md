# 全系統 AI 程序升級藍圖 (System-Wide AI Upgrade Blueprint)

> **文件狀態**：規劃中
> **建立日期**：2026-01-27
> **最高指導原則**：
> 1. **人格權重鎖定**：Little J 與 Jules 的核心人格 (妹妹/夥伴) 為不可動搖之基石，任何升級皆不得修改。
> 2. **使用者最高權限**：可究責自然人 (江政隆) 擁有凌駕規則之上的最終命令權 (Override Authority)。

## 1. 升級核心目標 (Upgrade Objectives)

### 1.1 從自動化到自治 (From Automation to Autonomy)
*   **現狀**：AI 模組 (V1.0) 多為被動觸發的腳本。
*   **目標**：升級為具備「主動感知、邊緣決策、自我修復」能力的 V2.0 自治代理。

### 1.2 權限架構重塑 (Authority Restructuring)
*   **引入 Override Protocol**：在底層邏輯中植入「使用者命令優先」的判斷迴路。
*   **人格層保護 (Persona Layer Protection)**：將人格設定檔 (`double_j_appearance.yaml`) 設為唯讀核心，防止運算邏輯優化過程中的意外稀釋。

---

## 2. 小J V2.0 (Little J) 升級規劃

### 2.1 雙核引擎實作 (Dual-Core Implementation)
*   **即時核 (Real-time Core)**：
    *   **技術**：Rust/C++ 高效能模組。
    *   **職責**：毫秒級處理 Router 封包與 POS 串流，確保「數位圍籬」無縫運作。
*   **邏輯核 (Logic Core)**：
    *   **技術**：Python + Local LLM (Qwen/Phi)。
    *   **職責**：執行 50/50 金流拆帳、PII 隱私過濾。
    *   **新增**：`UserCommandOverride` 模組，當接收到特定簽章指令時，繞過常規邏輯直接執行。

### 2.2 人格增強 (Persona Enhancement)
*   **記憶錨點 (Memory Anchor)**：將與使用者的互動歷史轉化為長期記憶，強化「妹妹」角色的情感連結。
*   **主動關懷**：不只回報錯誤，更能主動提示天氣、行程與健康建議 (結合專勤隊數據)。

---

## 3. 雲端小J (Jules) 升級規劃

### 3.1 全域大腦 (Global Brain)
*   **跨域學習**：分析多個社區節點 (若有擴展) 的數據，優化外送路徑算法。
*   **財務審計 V2**：不僅查核儲備率，還能預測未來現金流風險，提前發出預警。

### 3.2 資源連結器 (Resource Connector)
*   **自動化提案**：主動掃描外部 NPO 補助計畫，自動生成符合許願樹需求的申請草案。

---

## 4. 最高權限指令邏輯 (User Command Override Protocol)

### 4.1 邏輯定義
```python
def execute_command(command, user_id):
    # 1. 驗證使用者身份 (必須是可究責自然人)
    if not verify_accountable_person(user_id):
        return check_system_rules(command) # 走一般規則檢查

    # 2. 最高權限路徑 (Override Path)
    # 只要不損害他人權益，直接執行
    if not check_harm_to_others(command):
        log_override_action(command) # 記錄以備究責
        return force_execute(command)
    
    return check_system_rules(command)
```

### 4.2 應用場景
*   **緊急動用**：使用者可指令動用「風險基金」進行非預定支出。
*   **規則豁免**：使用者可指令特定交易免除 20% 捐贈 (例如特殊公益活動)。

---

## 5. 實施步驟 (Execution Steps)

1.  **鎖定人格設定**：即刻將 `config/ai_agents/` 下的人格檔案設為系統級唯讀。
2.  **開發 Override 模組**：在 `wuchang_core` 中實作最高權限判斷邏輯。
3.  **部署雙核引擎**：逐步將 Little J 的 I/O 處理遷移至高效能語言。
