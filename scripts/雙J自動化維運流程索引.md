# 雙J自動化維運流程索引

本文件記錄雙J（本地/雲端小j）自動化日常維運流程，並提供快速索引，方便日後查閱與擴充。

---

## 1. 核心自動化腳本

- `scripts/comprehensive_hourly_check.py`  
  每小時自動檢查：
  - 外網可見性（Public IP/Port）
  - DNS/SSL 憑證有效性
  - Google 非營利組織首頁合規
  - 自動產生報告與異常提示

- `scripts/double_j_maintenance_workflow.py`  
  雙J維運工作流：
  - 系統健康度檢查（容器、資源、服務）
  - 每小時自動維運（容器健康、資源清理、服務可用性、外網端口驗證）
  - 日誌記錄與自動化執行

---

## 2. 日常維運自動化步驟

1. **外網可見性檢查**：
   - 透過 `comprehensive_hourly_check.py` 自動檢查所有服務是否可從外網存取。
2. **DNS/SSL 憑證驗證**：
   - 自動比對 DNS 記錄與 SSL 憑證有效期，異常自動提示。
3. **Google合規首頁檢查**：
   - 定期檢查首頁內容是否符合法規要求。
4. **雙J維運工作流**：
   - 由 `double_j_maintenance_workflow.py` 定時執行，確保系統健康與資源最佳化。
5. **自動修復與日誌**：
   - 發現異常自動修復，並將維運結果記錄於 `reports/HOURLY_MAINTENANCE_LOGS.md`。

---

## 3. 快速索引

- [comprehensive_hourly_check.py](scripts/comprehensive_hourly_check.py)
- [double_j_maintenance_workflow.py](scripts/double_j_maintenance_workflow.py)
- [HOURLY_MAINTENANCE_LOGS.md](reports/HOURLY_MAINTENANCE_LOGS.md)

---

## 4. 日常維運建議

- 建議定期檢查維運日誌，並根據異常自動修復建議優化系統。
- 可依需求擴充自動化腳本，加入更多健康檢查與自動修復邏輯。

---

> 本索引由小j自動生成，歡迎家族成員隨時查閱與擴充！
