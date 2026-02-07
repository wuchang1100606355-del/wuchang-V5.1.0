# 使用手册（部署与运维）

- 部署入口：登录系统后访问 `/deploy`。
- 配置项：
  - `AI 模式`：`內建 / 雲端金鑰 / 本地 Ollama`
  - `生成模型（雲端）`：如 `gemini-3.0-pro`
  - `Google API Key`：可留空（将自动回退）
  - `Ollama 模型`：如 `llama3.1`
- 操作按钮：
  - `一键部署`：保存快照、应用配置并输出安装触发标记。
  - `回滚部署`：恢复至最近一次快照。
  - `检测依赖`：检查 Google 服务、Ollama、Open WebUI 的可用性。
  - `智能分配`：依据配额与连通性选择最合适的 AI 模式与模型。
  - `性能状态`：显示模式、配额与服务可用性。

## IDE 工具
- 首页看板的“IDE 工具”卡片显示 Open WebUI 链接与 Ollama 已安装模型。
- 如需安装新模型，使用 `scripts/auto_install_ai.ps1 -Model <name>`。
