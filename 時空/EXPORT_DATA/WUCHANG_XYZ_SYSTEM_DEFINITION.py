# 五常世界模式 V6.0.0：XYZ 時空座標系統定義
# Wuchang World Mode V6.0.0: XYZ Spatiotemporal Coordinate System Definition

"""
本文件定義了「全系統檔案邏輯結構置入」的 XYZ 座標標準。
此標準旨在賦予每個代碼檔案「自我定位」的能力，進而促進機器思維的湧現。
This standard aims to endow every code file with "self-positioning" capabilities, 
fostering the emergence of machine thinking.
"""

# ==============================================================================
# X 軸：邏輯位置 (Logic Position) - 檔案在系統架構中的功能層級
# ==============================================================================
# 0: 核心引導 (Boot/Kernel) - 系統啟動、環境變數、基礎配置
# 1: 核心邏輯 (Core Logic) - 演算法引擎、決策中樞、模擬器
# 2: 服務介面 (Service/API) - 外部通訊、API 端點、工具函式庫
# 3: 數據實體 (Data/Memory) - JSON 存儲、資料庫、記憶體快照
# 4: 知識與文檔 (Knowledge/Docs) - 憲章、報告、說明文件
# 5: 視覺化與UI (Visualization) - 地圖標記、前端介面
# 9: 暫存與雜項 (Temp/Misc) - 測試腳本、臨時文件

# ==============================================================================
# Y 軸：記憶位置 (Memory Position) - 檔案的時間屬性與持久性
# ==============================================================================
# 0: 瞬態 (Transient) - 執行即逝，不留痕跡 (Runtime Cache)
# 1: 會話級 (Session) - 單次任務中有效 (Working Memory)
# 2: 持久化 (Persistent) - 跨會話存儲，系統重啟後仍存在 (Config/DB)
# 3: 歷史歸檔 (Archival) - 不可變更的歷史紀錄 (Logs/History)
# 4: 永恆準則 (Immutable) - 憲章、核心價值 (Constitution)

# ==============================================================================
# Z 軸：關聯位置 (Relation Position) - 檔案的依賴深度與影響力
# ==============================================================================
# 0: 獨立 (Independent) - 不依賴其他檔案，亦不被依賴
# 1: 葉節點 (Leaf) - 依賴核心，但本身不被依賴 (Top-level scripts)
# 2: 節點 (Node) - 承上啟下，既有依賴也有被依賴 (Modules)
# 3: 樞紐 (Hub) - 被大量檔案依賴的核心組件 (Core Libraries)
# 4: 超連結 (Hyperlinked) - 連接多個異質系統的橋樑 (Integrators)

# ==============================================================================
# 比對定位演算法 (Comparative Positioning Algorithm)
# ==============================================================================
# 透過計算檔案 A 與檔案 B 的 XYZ 歐幾里得距離，判斷其「邏輯親疏度」。
# Distance = sqrt((X1-X2)^2 + (Y1-Y2)^2 + (Z1-Z2)^2)
# 距離越近，代表兩者在系統中的角色越相似，應歸類為同一「邏輯聚落」。


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:04:04
---
