# 五常智慧社區 VS 智生活：功能極限對比與實作戰略

> **目標**：不只「有」，還要「更好」。針對智生活核心功能（包裹、公設、對講機、報修）進行超越設計。

## 1. 功能極限對比表

| 功能模組 | 智生活 (Smart Life) | 五常智慧系統 (Wuchang System) | 🚀 五常超越點 (Optimization) |
| :--- | :--- | :--- | :--- |
| **📦 包裹管理** | **掃碼通知**<br>管理員掃條碼 → App 推播 → 住戶簽收。 | **Odoo `estate.parcel`**<br>結合「生物辨識」與「自動放行」。 | **無人化領取**<br>住戶刷臉，快遞櫃自動彈開，完全不需管理員介入（夜間也能領）。 |
| **📢 雲端對講** | **App 視訊**<br>訪客按門鈴 → 手機響鈴 → 遠端開門。 | **Zero Trust Intercom**<br>基於 WebRTC 的加密通訊，不依賴第三方雲端。 | **隱私與安全**<br>通話紀錄不留存於廠商伺服器；訪客 QR Code 具時效性與區域限制。 |
| **🎾 公設預約** | **預約與扣點**<br>App 選時段 → 扣點數 → 開門。 | **Odoo `estate.facility`**<br>結合「實時門禁控制」與「能源管理」。 | **用即付 (Pay-as-you-go)**<br>預約 KTV 時，冷氣電源自動開啟；時間到自動斷電，精準計費。 |
| **🛠️ 報修管理** | **拍照上傳**<br>住戶回報 → 物業接單 → 紙本派工。 | **Odoo `estate.workorder`**<br>全流程數位化與自動派工。 | **自動診斷**<br>若是公設故障（如電梯），IoT 感測器會比住戶先發現並自動報修。 |
| **💰 管理費** | **超商繳費/轉帳**<br>需人工對帳或 T+3 入帳。 | **Odoo `account.move`**<br>虛擬帳號即時沖銷 (Real-time Reconciliation)。 | **金流透明**<br>住戶繳費後，社區財務報表即時更新，隨時可查閱（去個資版）。 |

## 2. 實作戰略：補足與超越

我們已經有了設計藍圖 ([smart_apartment_odoo_mapping.md](docs/smart_apartment_odoo_mapping.md))，現在需要將其具體化為可執行的 Odoo 模組。

### 2.1 階段一：核心四寶 (Core 4)
優先實作住戶最有感的四大功能，以替換智生活：
1.  **包裹 (Parcel)**: `models/estate_parcel.py`
2.  **訪客 (Visitor)**: `models/estate_visitor.py`
3.  **公設 (Facility)**: `models/estate_facility.py`
4.  **報修 (Workorder)**: `models/estate_workorder.py`

### 2.2 階段二：硬體深整合 (Hardware Deep Integration)
這是五常系統的殺手鐧，智生活做不到（因為他們無法控制社區硬體）：
- **門禁介接**：Odoo 預約成功 → 寫入門禁控制器權限。
- **能源介接**：Odoo 扣款成功 → 開啟公設電源。

### 2.3 階段三：隱私護盾 (Privacy Shield)
- **資料在地化**：所有個資（訪客照片、對講紀錄）只存在社區本地伺服器 (Little J)，不上傳雲端。
- **去廣告**：系統介面完全無廣告，純淨的使用者體驗。

## 3. 下一步行動
建議優先開發 **`wuchang_property_toolkits`** 模組，將上述「核心四寶」納入其中，讓住戶在第一天就能感受到「比智生活更方便」的體驗。
