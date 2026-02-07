# Git 推送指南

## 遠程倉庫設定

- **倉庫名稱**: wuchang-os
- **遠程 URL**: https://github.com/wuchang/wuchang-os.git
- **當前分支**: migration/ui-total-ai

## 推送步驟

### 1. 建立 GitHub 倉庫（如果尚未建立）

如果 GitHub 上還沒有 `wuchang-os` 倉庫，請先建立：

1. 前往：https://github.com/new
2. 倉庫名稱：`wuchang-os`
3. 描述：`五常智慧社區雲系統 (Wuchang OS)`
4. 選擇：Private（私有）或 Public（公開）
5. **不要**勾選 "Initialize with README"
6. 點擊 "Create repository"

### 2. 建立 Personal Access Token

1. 前往：https://github.com/settings/tokens
2. 點擊 "Generate new token (classic)"
3. 設定：
   - Note: `Wuchang OS - Local Development`
   - Expiration: 選擇適當的過期時間
   - Scopes: 勾選 `repo`（完整倉庫權限）
4. 點擊 "Generate token"
5. **立即複製 Token**（只會顯示一次）

### 3. 推送代碼

```powershell
# 添加所有變更
git add .

# 提交變更
git commit -m "feat: 整合 Google Workspace 和完整系統設定

- 新增 Google Workspace 整合模組
- 整合 Google Meet、Google 表單、Google Drive
- 新增 AI 公文生成系統
- 新增公文範本系統
- 設定伺服器和超級管理員權限
- 更新架構設計文檔"

# 推送到遠程倉庫
git push -u origin migration/ui-total-ai
```

推送時會提示：
- **Username**: `wuchang`
- **Password**: `<貼上 Personal Access Token>`

Windows 認證管理器會自動儲存認證資訊，之後就不需要再次輸入。

### 4. 驗證推送

```powershell
# 檢查遠程分支
git branch -r

# 查看遠程倉庫狀態
git remote show origin
```

## 故障排除

### 如果推送失敗

1. **檢查連線**
   ```powershell
   git fetch origin
   ```

2. **檢查認證**
   - 確認 Personal Access Token 是否有效
   - 確認 Token 是否有 `repo` 權限

3. **清除認證快取**（如果需要）
   ```powershell
   git credential-manager-core erase
   ```

4. **重新設定遠程倉庫**
   ```powershell
   git remote remove origin
   git remote add origin https://github.com/wuchang/wuchang-os.git
   ```
