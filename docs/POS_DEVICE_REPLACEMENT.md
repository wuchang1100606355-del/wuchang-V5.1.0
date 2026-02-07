# POS 設備汰換說明

**文件日期**: 2025-01-07  
**系統版本**: Wuchang OS V5.1.0

---

## 🎯 設備角色更正

### 主要 POS 設備
- **設備名稱**: v3_mix_edla_gl
- **IP 地址**: 192.168.50.86
- **Android 版本**: 13
- **狀態**: 主要 POS 設備（is_primary = true）

### 原 POS 設備
- **狀態**: 即將汰換 (Deprecated)
- **說明**: 將被 v3_mix_edla_gl 取代

---

## 📋 設備狀態說明

### 設備狀態選項
- `online`: 在線（正常運作）
- `offline`: 離線
- `unknown`: 未知
- `deprecated`: 即將汰換（原 POS 設備）
- `replaced`: 已汰換

### 主要設備標記
- `is_primary`: 標記為主要/活躍設備
- v3_mix_edla_gl 應設為 `is_primary = true`
- 原 POS 設備應設為 `is_primary = false`

---

## 🔄 設備汰換流程

### Step 1: 納管 v3_mix_edla_gl（主要 POS）

```powershell
python scripts\enroll_android_pos.py `
    --device-name "v3_mix_edla_gl" `
    --ip "192.168.50.86" `
    --port 41895 `
    --android-version "13" `
    --developer-mode `
    --debug-usb --debug-gpu --debug-wifi
```

或使用專用腳本：
```powershell
.\scripts\enroll_v3_mix_edla_gl.ps1
```

### Step 2: 標記原 POS 設備為即將汰換

#### 方式 1: 透過 Odoo UI

1. 訪問: http://192.168.50.249:8069/web/login
2. 進入「基礎設施」→「設備」
3. 找到原 POS 設備
4. 編輯設備：
   - 狀態: 改為「即將汰換 (Deprecated)」
   - 主要設備: 取消勾選
   - 備註: 添加「已被 v3_mix_edla_gl 取代，即將汰換」

#### 方式 2: 使用 SQL

```sql
UPDATE wuchang_infrastructure_device
SET 
    status = 'deprecated',
    is_primary = false,
    note = note || '，已被 v3_mix_edla_gl 取代，即將汰換'
WHERE device_type = 'pos' 
  AND name != 'v3_mix_edla_gl'
  AND is_primary = true;
```

#### 方式 3: 使用 PowerShell 腳本

```powershell
.\scripts\mark_old_pos_deprecated.ps1 -OldPOSIP "192.168.50.XXX"
```

---

## ✅ 確認清單

### v3_mix_edla_gl（主要 POS）
- [ ] 設備已納管
- [ ] 狀態為 `online`
- [ ] `is_primary = true`
- [ ] 設備名稱: v3_mix_edla_gl
- [ ] IP: 192.168.50.86

### 原 POS 設備
- [ ] 狀態已改為 `deprecated`
- [ ] `is_primary = false`
- [ ] 備註中說明已被取代

---

## 📊 設備狀態對照

| 設備 | IP | 狀態 | 主要設備 | 說明 |
|------|-----|------|---------|------|
| v3_mix_edla_gl | 192.168.50.86 | online | ✅ 是 | 主要 POS 設備 |
| 原 POS 設備 | 192.168.50.XXX | deprecated | ❌ 否 | 即將汰換 |

---

## 💡 注意事項

1. **v3_mix_edla_gl 是主要 POS 設備**
   - 所有 POS 操作應使用此設備
   - 此設備應設為 `is_primary = true`

2. **原 POS 設備即將汰換**
   - 應標記為 `deprecated` 狀態
   - 不應再作為主要 POS 使用

3. **設備汰換後**
   - 原 POS 設備可標記為 `replaced` 狀態
   - 記錄汰換時間和原因

---

**文件版本**: 1.0  
**最後更新**: 2025-01-07  
**維護者**: 小J (Little J)
