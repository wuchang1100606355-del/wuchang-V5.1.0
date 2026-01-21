# 版本差距檢查指南

## 當前狀況

環境變數 `WUCHANG_COPY_TO` 未設定，無法連接到真實根伺服器進行版本差距檢查。

## 檢查版本差距的方法

### 方法一：使用環境變數（推薦）

1. **先設定環境變數**
   ```powershell
   .\setup_file_sync_env.ps1
   # 或手動設定
   $env:WUCHANG_COPY_TO = "\\SERVER\share\wuchang"
   ```

2. **執行版本差距檢查**
   ```bash
   # KB Profile
   python check_version_diff.py --profile kb
   
   # Rules Profile
   python check_version_diff.py --profile rules
   ```

### 方法二：直接指定伺服器路徑

如果知道伺服器路徑，可以直接指定：

```bash
# KB Profile
python check_version_diff.py --profile kb --server-dir "\\SERVER\share\wuchang"

# Rules Profile
python check_version_diff.py --profile rules --server-dir "\\SERVER\share\wuchang"
```

### 方法三：使用檔案比對工具

```bash
# 比對並顯示差異
python file_compare_sync.py --profile kb --server-dir "\\SERVER\share\wuchang"

# 比對並以 JSON 格式輸出
python file_compare_sync.py --profile kb --server-dir "\\SERVER\share\wuchang" --json
```

## 版本差距報告說明

報告會顯示：

1. **差距摘要**
   - 總檔案數
   - 內容相同/不同的檔案數
   - 本機較新/伺服器較新的檔案數
   - 僅本機/伺服器存在的檔案數

2. **同步狀態**
   - 同步率百分比
   - 差距程度（差距很小/中等/較大/很大）

3. **差異檔案詳情**
   - 每個檔案的差異類型
   - 修改時間差距
   - 檔案大小差距

4. **同步建議**
   - 建議同步到伺服器的檔案
   - 建議從伺服器同步的檔案

## 常見問題

### Q: 如何知道伺服器路徑？
A: 通常是 SMB 網路分享路徑，格式為 `\\伺服器名稱\分享名稱\路徑`

### Q: 檢查時顯示「伺服器目錄不存在」？
A: 請確認：
- 伺服器路徑是否正確
- 是否有網路連接
- 是否有存取權限

### Q: 如何判斷哪個版本較新？
A: 工具會比較修改時間（mtime），較新的版本會被標記

## 下一步

檢查完版本差距後：
1. 執行擇優同步：`python smart_sync.py --profile [kb|rules]`
2. 驗證同步結果：再次執行版本差距檢查
3. 確認所有檔案已同步
