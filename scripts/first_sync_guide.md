# 首次同步指南

**執行時間**: 2026-01-12  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)

---

## 📋 首次同步準備

### 偵測到的UI筆電設備

1. **LUNGsMSI.wuchang.life (192.168.50.84)**
   - 開放端口: SSH(22), HTTP(80), HTTPS(443), Odoo(8069)
   - 狀態: ✅ 在線

2. **POS-PC.wuchang.life (192.168.50.88)**
   - 狀態: ✅ 在線

---

## 🔧 同步方式選擇

### 方式1: 網絡共享（推薦）

**要求**:
- UI筆電需要設定網絡共享資料夾
- 需要網絡共享權限

**步驟**:
1. 在UI筆電上設定共享資料夾（例如: `C:\wuchang` → 共享為 `wuchang`）
2. 在本地系統上映射網絡驅動器或使用UNC路徑
3. 執行同步命令

**命令**:
```powershell
python scripts/sync_with_ui_laptop.py --remote-path "\\192.168.50.84\wuchang" --dry-run
```

### 方式2: SSH同步

**要求**:
- UI筆電需要啟用SSH服務
- 需要SSH認證資訊

**步驟**:
1. 確認SSH服務運行（LUNGsMSI已開放SSH端口）
2. 使用SSH客戶端連接
3. 使用SCP或rsync同步檔案

**命令範例**:
```powershell
# 使用SCP同步
scp -r "C:\wuchang V5.1.0\*" user@192.168.50.84:/path/to/wuchang/
```

### 方式3: 本地路徑（如果已映射）

**要求**:
- 已將網絡共享映射為本地驅動器

**步驟**:
1. 映射網絡驅動器（例如: `Z:\` → `\\192.168.50.84\wuchang`）
2. 使用本地路徑執行同步

**命令**:
```powershell
python scripts/compare_and_sync_bases.py `
  --base1 "C:\wuchang V5.1.0" `
  --base2 "Z:\wuchang" `
  --base1-name "本地基地端" `
  --base2-name "UI筆電基地端" `
  --sync-to base1 `
  --strategy newer `
  --dry-run
```

---

## 🚀 首次同步步驟

### 步驟1: 預覽同步計劃

```powershell
# 預覽模式（推薦先執行）
python scripts/sync_with_ui_laptop.py --remote-path "\\192.168.50.84\wuchang" --dry-run
```

**輸出**:
- 將顯示要同步的檔案列表
- 將顯示要更新的檔案列表
- 將顯示要複製的檔案列表

### 步驟2: 確認同步計劃

檢查預覽輸出：
- ✅ 確認要同步的檔案正確
- ✅ 確認同步方向正確（base1 = 本地）
- ✅ 確認同步策略正確（newer = 較新）

### 步驟3: 執行實際同步

```powershell
# 實際執行同步
python scripts/sync_with_ui_laptop.py --remote-path "\\192.168.50.84\wuchang"
```

**輸出**:
- 將顯示同步進度
- 將顯示同步結果
- 將生成同步報告

### 步驟4: 驗證同步結果

```powershell
# 查看同步報告
Get-Content logs\base_comparison_*.json | ConvertFrom-Json | Format-List

# 或查看最新的同步報告
Get-ChildItem logs\base_comparison_*.json | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content | ConvertFrom-Json | Format-List
```

---

## ⚠️ 注意事項

1. **網絡共享認證**: 
   - 如果網絡共享需要認證，需要先輸入用戶名和密碼
   - 可以使用 `net use` 命令建立持久連接

2. **權限確認**:
   - 確保對兩個基地端都有讀寫權限
   - 本地需要有寫入權限

3. **備份建議**:
   - 同步前建議手動備份重要檔案
   - 工具會自動備份更新的檔案（.backup副檔名）

4. **大檔案同步**:
   - 大檔案同步可能需要較長時間
   - 確保網絡連接穩定

5. **首次同步**:
   - 首次同步可能需要較長時間（需要掃描所有檔案）
   - 建議在網絡穩定的環境下執行

---

## 💡 故障排除

### 問題1: 無法訪問網絡共享

**解決方法**:
1. 檢查網絡連接
2. 檢查防火牆設置
3. 確認網絡共享已正確設定
4. 使用 `net use` 命令測試連接

### 問題2: 權限不足

**解決方法**:
1. 確認用戶有讀寫權限
2. 以管理員身份執行
3. 檢查資料夾權限設置

### 問題3: 同步失敗

**解決方法**:
1. 檢查錯誤訊息
2. 確認檔案未被鎖定
3. 確認磁碟空間充足
4. 檢查網路連接穩定性

---

## 📄 相關檔案

- `scripts/compare_and_sync_bases.py` - 檔案比較與同步工具
- `scripts/sync_with_ui_laptop.py` - UI筆電同步工具
- `config/sync_config.json` - 同步配置檔案
- `logs/base_comparison_*.json` - 同步結果報告

---

**報告生成時間**: 2026-01-12  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)

---

*「首次同步已準備就緒，請根據您的網絡環境選擇合適的同步方式！」* ✨
