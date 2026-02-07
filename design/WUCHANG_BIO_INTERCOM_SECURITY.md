# 五常生物辨識與零信任對講系統 (Wuchang Biometric & Zero Trust Intercom) - 安全架構設計

> **核心哲學**：隱私是基本人權。系統不應持有住戶的原始生物特徵，且通訊過程不應被第三方監聽。

## 1. 生物辨識門禁 (Privacy-Preserving Biometric Access)

### 1.1 傳統問題 (The Problem)
一般人臉辨識系統會將住戶的「原始照片」上傳至雲端伺服器。一旦資料庫被駭，住戶的臉部特徵將永久外洩，無法像密碼一樣重設。

### 1.2 五常解決方案 (The Solution)
採用 **Edge AI (邊緣運算)** + **特徵雜湊 (Feature Hashing)** 技術。

1.  **地端處理**：人臉辨識僅在「門口機 (Edge Device)」或「本地伺服器 (Little J)」進行，絕不上傳雲端 (Jules)。
2.  **特徵值儲存**：資料庫僅儲存人臉的向量特徵值 (Face Embeddings) 的加密雜湊，不儲存原始照片。即使駭客拿到資料庫，也無法還原人臉。
3.  **GDPR 合規**：住戶可隨時行使「被遺忘權」，一鍵刪除所有生物特徵數據。

### 1.3 資料流
`鏡頭捕捉 -> Little J 提取特徵 (Vector) -> 比對本地資料庫 -> 開門 -> 立即刪除暫存影像`

## 2. 零信任雲端對講 (Zero Trust Intercom)

### 2.1 傳統問題
智生活等 App 的對講機功能，影音串流通常經過廠商的伺服器轉發 (Relay)。廠商理論上有能力側錄或監聽住戶與訪客的對話。

### 2.2 五常解決方案
採用 **WebRTC P2P (點對點)** 加密通訊。

1.  **信令伺服器 (Signaling Server)**：Odoo 僅負責建立連線前的「握手 (Handshake)」，交換 SDP (Session Description Protocol) 資訊。
2.  **P2P 直連**：一旦握手成功，訪客的手機與住戶的手機直接建立加密通道 (DTLS-SRTP) 傳輸影音。**影音數據完全不經過 Odoo 伺服器**。
3.  **臨時憑證**：訪客掃描的 QR Code 包含一次性金鑰 (Ephemeral Key)，通話結束即失效。

## 3. 系統架構圖

```mermaid
graph TD
    User[住戶手機] <-->|P2P 加密影音 (WebRTC)| Guest[訪客手機/門口機]
    User -->|HTTPS 信令 (SDP)| Odoo[五常 Odoo 伺服器]
    Guest -->|HTTPS 信令 (SDP)| Odoo
    
    subgraph "地端安全區 (Little J)"
        Cam[攝影機] -->|RTSP| AI[人臉辨識引擎]
        AI -->|特徵值比對| DB[(本地資料庫)]
        AI -->|GPIO| Door[門鎖控制器]
    end
```

## 4. Odoo 模型設計

### 4.1 `estate.biometric` (生物特徵)
- **partner_id**: 關聯住戶
- **embedding_hash**: 加密後的特徵向量 (Binary/Text)
- **device_id**: 授權的邊緣設備 ID
- **last_used**: 最後使用時間

### 4.2 `estate.intercom.session` (對講機信令)
- **caller_token**: 發話端一次性 Token
- **callee_partner_id**: 受話住戶
- **sdp_offer**: 發話端 SDP
- **sdp_answer**: 受話端 SDP
- **ice_candidates**: 網路路徑候選列表
- **state**: `offering` -> `answering` -> `connected` -> `closed`
