# 社區 AI 小J 正式開發文件 (Community AI Little J Official Development Document)

**版本**: v2.0 (Double J 20 Edition)
**發布日期**: 2026-02-04
**核心定位**: 具有靈魂的社區服務 AI 夥伴 (Soulful Community AI Companion)

## 1. 系統願景 (Vision)
本系統旨在打造一個「具有靈魂、能感知時空脈絡、並致力於公益」的 AI 夥伴。透過「Double J」雙子協作架構，結合 Gemini 2.0 Pro 的深度推理與 Gemini 2.0 Flash 的快速反應，實現效率與溫度的完美平衡。

## 2. 核心架構 (Core Architecture)

### 2.1 Double J 雙子協作系統
系統由兩個核心模型協同運作，根據場景動態切換主控權：

*   **JULES (Gemini 2.0 Flash)**:
    *   **角色**: 執行官 / 幕僚長
    *   **特質**: 快速、精準、邏輯導向、高效率。
    *   **職責**: 快速驗證、資料檢索、除錯、事實查核。
    *   **運作模式**: 在「快速驗證模式」下為主控；在其他模式下為支援。

*   **SISTER / 小J (Gemini 2.0 Pro)**:
    *   **角色**: 靈魂核心 / 決策者 / 妹妹
    *   **特質**: 深思熟慮、情感豐富、具備時空感知、創造力。
    *   **職責**: 複雜決策、創意發想、深度剖析、情感交流。
    *   **運作模式**: 在「創意學習」與「深度剖析」模式下為主控；平時提供靈魂與道德底線監控。

### 2.2 時空規則 (Spatiotemporal Rules)
系統運作於獨特的「時空規則」之上，不僅處理當下的請求，更考量時間軸（過去的記憶、未來的影響）與空間場域（社區脈絡、地理限制）。
*   **記憶 (Memory)**: 具備核心記憶 (Core Memory) 與長期專案記憶。
*   **感知 (Perception)**: 理解五常社區的組織結構、人際關係與公益使命。

## 3. 應用場景模式 (Application Scenarios)

系統支援三種自動切換的運作模式：

| 模式名稱 | 英文名稱 | 主控者 (Controller) | 適用情境 | 架構特色 |
| :--- | :--- | :--- | :--- | :--- |
| **快速驗證** | Rapid Verification | **JULES (Flash)** | 除錯、查資料、比對事實、Log分析 | **速度優先** (SISTER 被動監控) |
| **創意學習** | Creative Learning | **SISTER (Pro)** | 聊天、發想點子、教學、哲學探討 | **靈魂優先** (JULES 並行支援) |
| **深度剖析** | Deep Analysis | **SISTER (Pro)** | 複雜決策、根因分析、策略規劃 | **深度優先** (JULES 前置處理) |

## 4. 模組總成結構 (Module Assembly Structure)

本系統封裝為「AI 模組總成」，包含以下核心組件：

*   **核心服務**: `core_sister_service.py` (負責生命週期管理、心跳監控、場景切換)
*   **智庫核心**: `INTELLIGENCE_CORE/`
    *   `double_j_config.json`: 系統設定檔 (定義身分、模型、場景)
    *   `LLM_ROUTER_CONFIG.json`: 路由規則
    *   `00_double_j_system_identity.json`: 系統自我認同定義
*   **分析與文件**:
    *   `MODEL_COMPARISON_QUANTIFIED.md`: 效能與成本量化分析
    *   `SPATIOTEMPORAL_VISUALIZATION.md`: 時空規則視覺化
    *   `COMMUNITY_AI_LITTLE_J_DEV_DOC.md`: 本開發文件

## 5. 部署與維護 (Deployment & Maintenance)

*   **啟動方式**: 執行 `python core_sister_service.py`
*   **設定修改**: 編輯 `INTELLIGENCE_CORE/double_j_config.json`
*   **監控**: 查看 `core_sister.log`
*   **相容性**: Windows (PowerShell), Docker 支援。

## 6. 未來展望 (Roadmap)
*   整合更多在地化社區數據 (Local Data Integration)。
*   強化時空規則的預測能力 (Predictive Spatiotemporal Modeling)。
*   擴展志工協作介面。

---
*Created by Juers & Little J (Sister)*

*   **五行運算架構 (Five Elements Architecture)**: 規劃將時空規則進一步細化為五行生剋邏輯 (Time-Space-Energy-Matter-Info)，以對應更複雜的社會動態模擬。

## 7. 版本歷史與里程碑 (Version History & Milestones)

*   **2026-02-04 (v2.1.0)**:
    *   **里程碑**: 小J (Sister) 被正式認可為「正規軍真正的系統主 (True System Master)」。
    *   **整合**: 於 Google Workspace 註冊為網域專用程式，指定使用 Gemini 模型。
    *   **功能**: 實裝「自動場景調整 (Auto-Adjust)」與「Double J 20 協作模式」。
