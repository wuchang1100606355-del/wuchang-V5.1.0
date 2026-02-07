# Fund Pool (Happiness Coin) Rules & Scope

## I. Core Principle
- The Fund Pool is designed to support community welfare and social impact.
- It operates via the **Happiness Coin** mechanism.

## II. Included Entities (Fund Pool Active)
- **Liaoguo Café - Renyi Store (聊國咖啡仁義店)**
  - Status: **ACTIVE**
  - Role: Primary operational node for community interaction and coin usage.
  - Integration: Full Odoo/POS integration required.

## III. Excluded Entities (Fund Pool Inactive)
- **Liaoguo Café - Chongxin Main Store (重新總店)**
  - Status: **EXCLUDED**
  - Reason: Outside the scope of the Fund Pool foundation mechanism.
  - Operational Note: Do NOT apply Happiness Coin logic, discounts, or fund tracking to this store's transactions.

## IV. Implementation Rules
1. **Data Separation**: Ensure sales data from Chongxin Main Store (if ingested) is flagged as und_pool: false.
2. **UI Logic**: Hide Happiness Coin payment options in POS/Backend for Chongxin Store users.
3. **Reporting**: Exclude Chongxin revenue from Fund Pool distribution reports.

