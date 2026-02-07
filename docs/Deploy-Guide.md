# 部署指南（轻量一体化 AI 效能方案）

- 前置条件：安装 Docker + Docker Compose，设置环境变量 `AI_MEMORY_PATH` 与 `AI_COMMON_PATH` 指向本机磁盘。
- 启动系统：`docker compose --profile system up -d`
- 启动 AI 组件：执行脚本 `scripts/auto_install_ai.ps1`（默认拉取 `llama3.1`），或手动 `docker compose --profile ui up -d`。
- 配置页面：登录后台访问 `/deploy`，设置 `AI 模式 / 生成模型 / Google API Key / Ollama 模型`，点击“一键部署”。
- 诊断与监控：在 `/deploy` 页面使用“检测依赖 / 智能分配 / 性能状态”。
- 回滚部署：点击“回滚部署”复原到最近一次部署前的配置快照。

## 路径与挂载
- 记忆仓：`/opt/wuchang/memory_store`（Compose 通过 `AI_MEMORY_PATH` 挂载）
- 共通库：`/opt/wuchang/common_store`（Compose 通过 `AI_COMMON_PATH` 挂载）

## 自动安装脚本
- `scripts/auto_install_ai.ps1`：启动 `ui` profile 并通过 Ollama HTTP API 拉取模型。
- 可选参数：`-ComposeFile`、`-Profile`、`-OllamaHost`、`-Model`

## 常见问题
- 如果 Open WebUI 或 Ollama 未启动，“一键部署”返回 `needs_ui_start=true`，请执行 `scripts/auto_install_ai.ps1`。
- Google API Key 未设定时，系统会自动回退至本地或内建模式。
