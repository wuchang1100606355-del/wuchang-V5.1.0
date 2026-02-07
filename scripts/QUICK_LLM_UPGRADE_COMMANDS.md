# 快速 LLM 升級命令參考

**容器名稱：** 需要確認  
**模型：** qwen2:7b

---

## 🔍 第一步：確認容器名稱

```bash
# 查看所有容器
docker ps -a

# 或查找 ollama 相關容器
docker ps -a | findstr ollama
docker ps -a | grep -i ollama
```

---

## 📥 第二步：下載 qwen2:7b 模型

**替換 `<容器名稱>` 為實際的容器名稱：**

```bash
docker exec <容器名稱> ollama pull qwen2:7b
```

**或使用完整命令（如果容器名是 wuchangv510-ollama-1）：**
```bash
docker exec wuchangv510-ollama-1 ollama pull qwen2:7b
```

---

## 🧪 第三步：測試模型

```bash
docker exec <容器名稱> ollama run qwen2:7b "Hello"
```

**或完整命令：**
```bash
docker exec wuchangv510-ollama-1 ollama run qwen2:7b "Hello"
```

---

## 🔧 第四步：更新配置

```bash
python scripts/update_llm_config_after_upgrade.py
```

**或指定模型名稱：**
```bash
python scripts/update_llm_config_after_upgrade.py --model qwen2:7b
```

---

## 📋 完整執行範例

```bash
# 1. 確認容器
docker ps -a | findstr ollama

# 2. 下載模型（替換 CONTAINER_NAME）
docker exec CONTAINER_NAME ollama pull qwen2:7b

# 3. 測試模型
docker exec CONTAINER_NAME ollama run qwen2:7b "Hello"

# 4. 更新配置
python scripts/update_llm_config_after_upgrade.py
```

---

## ⚠️ 如果容器未運行

**啟動容器：**
```bash
docker start <容器名稱>
```

**或重新建立容器：**
```bash
docker run -d --name ollama -p 11434:11434 ollama/ollama:latest
```

---

## 📝 其他可用的模型選項

```bash
# 輕量級選項
docker exec <容器名稱> ollama pull qwen2:1.5b

# Llama 系列
docker exec <容器名稱> ollama pull llama3.1:8b

# Mistral 系列
docker exec <容器名稱> ollama pull mistral:7b
```

---

**提示：** 如果容器名稱不同，請先執行 `docker ps -a` 確認正確的容器名稱。
