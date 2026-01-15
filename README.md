# 華碩路由器 DDNS 連接工具

這個工具用於連接到華碩路由器的 DDNS 地址 `CoffeeLoge.asuscomm.com` 或直接使用 IP 地址連接。

## 功能

- 測試連接到華碩路由器
- 支持 HTTPS 連接（使用本機已安裝的證書）
- 路由器登錄功能
- 獲取路由器信息

## 安裝

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 基本連接測試

```bash
python router_connection.py
```

### 2. 登錄路由器

**方式一：交互式登錄**
```bash
python login_router.py
```
然後按提示輸入用戶名和密碼。

**方式二：命令行參數**
```bash
python login_router.py <用戶名> <密碼>
```

例如：
```bash
python login_router.py admin mypassword
```

### 3. 在代碼中使用

```python
from router_connection import AsusRouterConnection

# 創建連接對象
router = AsusRouterConnection(
    hostname="220.135.21.74",  # 或使用域名
    port=8443,
    use_https=True
)

# 測試連接
router.test_connection(verify_cert=False)

# 登錄
router.login(username="admin", password="your_password", verify_cert=False)

# 獲取路由器信息
info = router.get_router_info(verify_cert=False)
```

## 連接信息

- **IP 地址**: `220.135.21.74`
- **域名**: `CoffeeLoge.asuscomm.com` (DDNS)
- **端口**: `8443` (HTTPS)
- **協議**: HTTPS

## 注意事項

1. **域名**: 以路由器遠端存取頁面顯示為準（例如 `CoffeeLoge.asuscomm.com`）
2. **證書**: 使用 IP 地址連接時，SSL 證書驗證會失敗（因為證書是為域名簽發的），這是正常現象
3. **端口**: 默認使用 8443（HTTPS），如果路由器使用其他端口，請修改 `port` 參數
4. **防火牆**: 確保防火牆允許連接到路由器端口

## 常見端口

- 8443: HTTPS（推薦，當前使用）
- 8080: HTTP
- 443: 標準 HTTPS
- 80: 標準 HTTP

## 故障排除

如果連接失敗：

1. 檢查路由器是否開啟並連接到網路
2. 確認 DDNS 配置正確（如果使用域名）
3. 檢查防火牆設置
4. 驗證證書是否正確安裝
5. 嘗試不同的端口號
6. 使用 IP 地址直接連接（如果 DDNS 無法解析）

## 登錄問題

如果登錄失敗：

1. 確認用戶名和密碼正確
2. 檢查路由器是否啟用了遠程登錄
3. 某些路由器可能需要額外的認證步驟
4. 嘗試在瀏覽器中手動登錄以確認憑證