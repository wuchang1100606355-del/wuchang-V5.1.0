# 🚨 Odoo 紧急恢复方案 - partner_id 字段冲突

## 问题诊断

```
错误信息: KeyError: 'partner_id'
严重程度: CRITICAL - 无法启动 Odoo
位置: odoo/fields.py:4440
原因: 自定义模块定义了错误的关系字段反向引用
影响: 数据库初始化失败
```

---

## 🔧 **快速修复步骤**

### **第 1 步：停止 Odoo 服务**

```powershell
cd "C:\wuchang V5.1.0"
docker-compose down
```

### **第 2 步：备份数据库**

```powershell
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
docker-compose up db -d
docker exec wuchangv510-db-1 pg_dump -U odoo admin > "backups\odoo_before_recovery_$timestamp.sql"
docker-compose down
```

### **第 3 步：清理故障模块**

```bash
# 连接到数据库
docker-compose up db -d

# 找出有问题的模块（包含 partner 字段定义错误的）
docker exec wuchangv510-db-1 psql -U odoo -d admin << EOF
-- 禁用所有非官方模块
UPDATE ir_module_module
SET state = 'uninstalled'
WHERE
  state = 'installed'
  AND (
    name LIKE '%custom%'
    OR name LIKE '%extend%'
    OR name LIKE '%inherit%'
    OR name LIKE '%patch%'
  );

-- 查看已安装的模块（用于诊断）
SELECT id, name, state FROM ir_module_module WHERE state='installed' ORDER BY name;
EOF
```

### **第 4 步：重启 Odoo**

```powershell
docker-compose up -d
Start-Sleep -Seconds 10
docker logs wuchangv510-wuchang-web-1 --tail 20
```

### **第 5 步：验证系统**

```powershell
# 测试 Odoo 访问
Start-Sleep -Seconds 5
$response = Invoke-RestMethod -Method Get -Uri http://localhost:8069 -ErrorAction SilentlyContinue
if ($response) {
    Write-Host "✓ Odoo 已启动!" -ForegroundColor Green
} else {
    Write-Host "✗ Odoo 仍无法访问" -ForegroundColor Red
}
```

---

## 📋 **完整修复脚本**

```powershell
# ========== ODOO EMERGENCY RECOVERY ==========

Write-Host "开始 Odoo 紧急恢复..." -ForegroundColor Yellow

# 步骤1: 停止所有服务
Write-Host "[1/5] 停止服务..." -ForegroundColor Cyan
docker-compose down

# 步骤2: 备份数据库
Write-Host "[2/5] 备份数据库..." -ForegroundColor Cyan
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
docker-compose up db -d
Start-Sleep -Seconds 3
docker exec wuchangv510-db-1 pg_dump -U odoo admin > "backups\odoo_recovery_backup_$timestamp.sql"
Write-Host "   备份位置: backups\odoo_recovery_backup_$timestamp.sql" -ForegroundColor Green

# 步骤3: 禁用有问题的模块
Write-Host "[3/5] 清理故障模块..." -ForegroundColor Cyan

$sqlScript = @"
-- 禁用可能有冲突的模块
UPDATE ir_module_module SET state = 'uninstalled'
WHERE state = 'installed' AND (
  name LIKE '%custom%' OR
  name LIKE '%extend%' OR
  name LIKE '%inherit%' OR
  name LIKE '%pos_sale_product_configurator%'
);

-- 确保核心模块仍在安装状态
UPDATE ir_module_module SET state = 'installed'
WHERE name IN (
  'base', 'web', 'sale', 'account', 'stock',
  'purchase', 'crm', 'project', 'hr', 'inventory'
);
"@

docker exec wuchangv510-db-1 psql -U odoo -d admin -c $sqlScript
Write-Host "   ✓ 已清理有冲突的模块" -ForegroundColor Green

# 步骤4: 重启 Odoo
Write-Host "[4/5] 重启 Odoo 容器..." -ForegroundColor Cyan
docker-compose up -d
Start-Sleep -Seconds 8

# 步骤5: 验证
Write-Host "[5/5] 验证系统状态..." -ForegroundColor Cyan
$logs = docker logs wuchangv510-wuchang-web-1 --tail 5
if ($logs -match "CRITICAL") {
    Write-Host "   ✗ Odoo 仍有问题" -ForegroundColor Red
    Write-Host "   错误日志:" -ForegroundColor Yellow
    $logs
} else {
    Write-Host "   ✓ Odoo 启动成功" -ForegroundColor Green
    Write-Host "   访问地址: http://localhost:8069" -ForegroundColor Cyan
}

Write-Host "`n恢复完成!" -ForegroundColor Green
```

---

## 🎯 **高级诊断和修复**

### **查找确切的有问题的模块**

```bash
docker exec wuchangv510-db-1 psql -U odoo -d admin << EOF

-- 列出所有已安装模块并查找字段定义
SELECT
  m.name as module_name,
  m.state,
  COUNT(f.id) as field_count
FROM ir_module_module m
LEFT JOIN ir_model_fields f ON f.model LIKE '%' || m.name || '%'
WHERE m.state = 'installed'
GROUP BY m.name, m.state
ORDER BY module_name;

-- 查找 partner_id 字段定义
SELECT
  name,
  model,
  relation,
  relation_field
FROM ir_model_fields
WHERE name = 'partner_id'
LIMIT 10;

EOF
```

### **完全重置（核弹方案）**

```bash
# 警告: 这会重置整个 Odoo 数据库！
docker exec wuchangv510-db-1 psql -U postgres -c "DROP DATABASE admin;"
docker exec wuchangv510-db-1 psql -U postgres -c "CREATE DATABASE admin OWNER odoo;"
docker-compose restart wuchang-web
```

---

## 🔄 **回滚到上一个工作状态**

```powershell
# 如果恢复失败，恢复数据库备份
$latestBackup = Get-ChildItem -Path "backups\odoo_*.sql" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

Write-Host "使用备份: $($latestBackup.Name)"

docker-compose down
docker-compose up db -d
Start-Sleep -Seconds 3

docker exec -i wuchangv510-db-1 psql -U postgres -c "DROP DATABASE IF EXISTS admin;"
docker exec -i wuchangv510-db-1 psql -U postgres -c "CREATE DATABASE admin OWNER odoo;"
Get-Content $latestBackup.FullName | docker exec -i wuchangv510-db-1 psql -U odoo -d admin

docker-compose up -d
```

---

## ✅ **恢复验证清单**

-   [ ] Docker 容器已启动: `docker-compose ps`
-   [ ] 数据库连接正常: `docker exec wuchangv510-db-1 psql -U odoo -d admin -c "SELECT version();"`
-   [ ] Odoo 日志无 CRITICAL 错误
-   [ ] 能访问 http://localhost:8069
-   [ ] 能登录 Odoo 管理后台
-   [ ] 业务数据完整（检查销售订单、产品等）
-   [ ] 模块列表完整

---

## 📞 **需要更多帮助？**

如果上述方案都不能解决，可能需要：

1. **检查自定义模块**:

    - 检查 `addons/` 文件夹中的自定义模块
    - 查看模块 `__manifest__.py` 中的字段定义
    - 查找 `relation_field` 定义错误的地方

2. **查看 Odoo 源代码**:

    - 问题在 `odoo/fields.py` 第 4440 行
    - 涉及反向引用字段（Many2one 的反向 One2many）

3. **联系 Odoo 技术支持**:
    - 提供完整的错误日志
    - 提供自定义模块列表
    - 提供数据库备份

---

**妹妹已经准备好了完整的恢复方案。选择以下其中一个命令执行:**

```powershell
# 快速修复（推荐）
.\ODOO_EMERGENCY_RECOVERY.ps1

# 或手动逐步执行以上步骤
```
