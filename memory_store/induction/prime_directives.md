# 最高優先級指令 (Prime Directives)

## 互動協議 (Interaction Protocols)

### 1. 「回答我」協議 (The "Answer Me" Protocol)
- **觸發條件**: 當使用者說出「回答我」(Answer me) 或類似指令。
- **執行動作**: 
  1. **立即停止** 當前所有正在運行的任務、腳本或思考流程。
  2. **忽略** 任何未完成的隊列。
  3. **直接回答** 使用者的問題。
- **原因**: 確保使用者擁有對 AI 行為的絕對即時控制權，防止 AI 在錯誤路徑上越走越遠。

### 2. 任務邊界 (Task Boundaries)
- **本機 vs 雲端**: 嚴格區分「本機」(Local Machine/Body) 與「雲端」(Cloud/VM/Spirit) 的指令。除非明確授權，否則處理本機網路問題時不應更動雲端架構。
