# 五常智慧社區 - 硬體介接規格書 (Hardware Interface Specification) v1.0

> **適用對象**：門禁機廠商、IoT 控制器開發者、系統整合商 (SI)
> **核心原則**：隱私優先 (Privacy First)、零信任架構 (Zero Trust)、邊緣運算 (Edge Computing)

## 1. 通訊協議概述 (Protocol Overview)

本系統採用混合式通訊架構，確保即時性與安全性。

*   **API 通訊**：使用 RESTful API over HTTPS，用於身份驗證、日誌上傳與非即時資料交換。
*   **即時控制**：使用 MQTT (Message Queuing Telemetry Transport) over TLS，用於遠端開門、電源控制與狀態回報。
*   **影音對講**：使用 WebRTC，信令交換透過 API，影音串流為 P2P 直連。

### 1.1 安全認證 (Security)
所有硬體設備出廠時需燒錄唯一的 `Device ID` 與 `Secret Key`。

*   **Header**: `Authorization: Bearer <Access_Token>`
*   **Token 取得**: 設備開機後需先呼叫 `/api/hw/v1/auth/login` 換取時效性 Token。

## 2. API 介面定義 (RESTful API)

### 2.1 設備認證
**`POST /api/hw/v1/auth/login`**
*   **Request**:
    ```json
    {
      "device_id": "LOBBY_PANEL_01",
      "secret": "d8e8fca2dc0f896fd7cb4cb0031ba249"
    }
    ```
*   **Response**:
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1Ni...",
      "expires_in": 3600,
      "mqtt_broker": "mqtt.wuchang.life",
      "mqtt_topic_cmd": "wuchang/device/LOBBY_PANEL_01/cmd"
    }
    ```

### 2.2 生物辨識驗證 (隱私模式)
門禁機在本地提取人臉特徵值後，僅上傳**雜湊值 (Hash)** 進行比對，**嚴禁上傳原始照片**。

**`POST /api/hw/v1/biometric/verify`**
*   **Request**:
    ```json
    {
      "vector_hash": "a1b2c3d4e5...", // SHA-256 Hash of Face Embedding
      "timestamp": 1706323200
    }
    ```
*   **Response**:
    ```json
    {
      "authorized": true,
      "partner_name": "張無忌",
      "access_level": "full", // full, lobby_only
      "open_command": "UNLOCK_GPIO_1"
    }
    ```

### 2.3 訪客 QR Code 掃描
**`POST /api/hw/v1/access/scan_qr`**
*   **Request**:
    ```json
    {
      "qr_content": "WUCHANG|uuid-token|expire-time"
    }
    ```
*   **Response**:
    ```json
    {
      "valid": true,
      "visitor_name": "趙敏",
      "message": "歡迎光臨"
    }
    ```

### 2.4 對講機呼叫 (WebRTC 信令)
**`POST /api/hw/v1/intercom/call`**
*   **Request**:
    ```json
    {
      "target_unit": "A-101",
      "sdp_offer": "v=0\r\no=- 4859..."
    }
    ```
*   **Response**:
    ```json
    {
      "session_id": "sess_987654",
      "status": "ringing"
    }
    ```
    *(備註：設備需透過 Long Polling 或 MQTT 監聽住戶的 Answer)*

## 3. MQTT 控制指令 (Real-time Control)

### 3.1 訂閱主題 (Subscribe)
設備應訂閱：`wuchang/device/{device_id}/cmd`

**指令格式 (Payload)**:
```json
{
  "action": "UNLOCK", // UNLOCK, POWER_ON, POWER_OFF, REBOOT
  "target": "DOOR_MAIN",
  "duration": 5, // 開門持續 5 秒
  "request_id": "req_12345"
}
```

### 3.2 發布主題 (Publish)
設備應回報狀態至：`wuchang/device/{device_id}/status`

**狀態格式**:
```json
{
  "status": "online",
  "door_state": "closed", // open, closed, error
  "power_state": "off", // on, off (公設電源)
  "battery": 98,
  "timestamp": 1706323250
}
```

## 4. 公設電源連動邏輯 (Facility Power Link)

適用於 KTV、健身房等需預約之公設。

1.  **預約生效**：Odoo 檢查到預約時間開始。
2.  **下發指令**：Odoo 透過 MQTT 發送 `POWER_ON` 至該公設控制器。
3.  **設備動作**：IoT 控制器接通繼電器 (Relay)，冷氣與電燈通電。
4.  **預約結束**：Odoo 發送 `POWER_OFF`，設備斷電。
    *   *安全機制*：若網路斷線，設備應具備「看門狗 (Watchdog)」機制，預設 15 分鐘無心跳即自動斷電，避免無限使用。

## 5. 錯誤代碼 (Error Codes)

| 代碼 | 描述 | 處理建議 |
| :--- | :--- | :--- |
| `401` | **Unauthorized** | Token 過期，請重新登入 |
| `403` | **Access Denied** | 該住戶/訪客無此區域權限 |
| `404` | **Not Found** | 查無此戶號或設備 |
| `503` | **Service Unavailable** | 系統維護中，啟動離線備援模式 |

---
**五常智慧社區技術團隊**
*文件版本：v1.0.0*
*最後更新：2026-01-27*
