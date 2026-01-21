# 虛擬硬碟為什麼這麼大？

## 當前虛擬硬碟使用情況

### 總大小：約 115.52 GB

1. **Docker 虛擬硬碟**：83.02 GB
   - 可回收空間：約 34 GB
   - Images: 22.76 GB (42% 可回收)
   - Volumes: 1.927 GB (88% 可回收)
   - Build Cache: 9.765 GB

2. **WSL 虛擬硬碟**：16.44 GB
   - 用於 Windows Subsystem for Linux

3. **BlueStacks 虛擬硬碟**：16.06 GB
   - Android 模擬器

## 為什麼虛擬硬碟這麼大？

### 主要原因：

1. **動態擴展機制**
   - 虛擬硬碟（.vhdx, .vdi）會自動增長以容納資料
   - 但**不會自動縮小**，即使刪除內部檔案

2. **刪除檔案不釋放空間**
   - 在虛擬硬碟內部刪除檔案
   - 虛擬硬碟檔案本身的大小不會立即減少
   - 需要手動壓縮才能回收空間

3. **累積的資料**
   - Docker 映像檔、容器、快取
   - WSL Linux 系統檔案和資料
   - 應用程式日誌和暫存檔

4. **碎片整理**
   - 虛擬硬碟內部可能有碎片
   - 需要壓縮來整理和回收空間

## 解決方案

### 1. 清理 Docker（可回收約 34 GB）

```powershell
# 清理未使用的資源
docker system prune -a --volumes

# 然後壓縮虛擬硬碟
wsl --shutdown
Optimize-VHD -Path "$env:USERPROFILE\AppData\Local\Docker\wsl\disk\docker_data.vhdx" -Mode Full
```

### 2. 壓縮 WSL 虛擬硬碟

```powershell
# 關閉 WSL
wsl --shutdown

# 壓縮
Optimize-VHD -Path "$env:USERPROFILE\AppData\Local\wsl\*\ext4.vhdx" -Mode Full
```

### 3. 如果不再使用 BlueStacks

- 可以卸載 BlueStacks 以釋放 16 GB

## 自動化腳本

使用 `cleanup_and_compress_virtual_disks.ps1` 可以自動：
1. 清理 Docker 未使用的資源
2. 壓縮 Docker 虛擬硬碟
3. 壓縮 WSL 虛擬硬碟

**執行方式**：
```powershell
powershell -ExecutionPolicy Bypass -File "cleanup_and_compress_virtual_disks.ps1"
```

## 預期效果

- **Docker**：從 83 GB 可能減少到 50-60 GB（節省約 20-30 GB）
- **WSL**：從 16 GB 可能減少到 5-10 GB（節省約 6-11 GB）
- **總計可節省**：約 26-41 GB

## 注意事項

1. ⚠️ 壓縮過程需要時間（可能需要 10-30 分鐘）
2. ⚠️ 需要停止相關服務（Docker、WSL）
3. ⚠️ 需要管理員權限
4. ⚠️ 壓縮後可能需要重啟相關服務
