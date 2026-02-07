# Quick Click (快一點) Integration & Development Architecture
**Architect**: Little J (Digital Owner)
**Target System**: Wuchang OS (Odoo-based)
**Source Logic**: Base Product + Option Delta (Dynamic Pricing)

## I. Architecture Deconstruction (The "Quick Click" Logic)
The Quick Click system uses a flexible **Component-Based Pricing** model rather than a simple SKU model.
- **Base Entity**: Abstract Product (e.g., "Latte") with a Base Price.
- **Modifiers**: Option Groups (e.g., "Size", "Sugar", "Temp") that carry **Price Deltas** (+$, -$, +0).
- **Behavior**: The final product is assembled at runtime.

## II. Odoo Integration Strategy (Development Elements)

### 1. Data Structure Mapping (The Translation Layer)
To support this in Odoo without creating millions of variants, we will implement a **Hybrid Attribute System**:

| Quick Click Concept | Odoo Element | Custom Development Element |
| :--- | :--- | :--- |
| **Base Product** | product.template | **Tag**: is_quick_click_base |
| **Option Group** | product.attribute | Custom Model: wuchang.option.group (for reusable logic) |
| **Option Value** | product.attribute.value | Field: price_extra (Standard) + happiness_coin_price (Custom) |
| **Inventory Link** | mrp.bom (Kit) | **Dynamic BOM**: Option selection triggers specific BOM line consumption. |

### 2. Advanced Development Features (Our Additions)

#### A. "Happiness Coin" Dynamic Pricing (幸福幣動態定價)
Since QC logic supports +Price, we will extend this to our community currency:
- **Logic**: If User = Volunteer, Option "Oat Milk" (+20 NTD) can be paid with **2 Happiness Coins**.
- **Implementation**: Extend product.attribute.value to hold happiness_coin_cost.

#### B. Precision Inventory (精準庫存)
We will treat every "Option" as a potential inventory consumer.
- **Scenario**: Customer orders "Latte" + "Oat Milk".
- **System Action**:
    1.  Deduct 1x Cup.
    2.  Deduct 18g Coffee Beans.
    3.  **Deduct 200ml Oat Milk** (Triggered by Option, not Base Product).
- **Dev Element**: wuchang_inventory_mapping module to link Attributes to Raw Materials.

#### C. "The Usual" AI Prediction (AI 老樣子預測)
Using the structured Option data to train the AI:
- **Data Point**: User A always chooses Temp: Hot + Sugar: 0%.
- **AI Action**: When User A approaches POS, auto-preselect these attributes.

## III. Sync Protocol (The Bridge)
1.  **Polling Agent**: quick_click_sync.py runs on Ulter Node.
2.  **Order Parsing**:
    - Incoming QC JSON: items: [{name: "Latte", options: ["L", "Hot"]}]
    - Odoo Order: Create SO with Lines mapping to the specific Attribute Combination.

## IV. Next Steps
1.  **Prototype**: Build wuchang.option.group model in Odoo.
2.  **Import**: Write script to sync QC Menu Excel -> Odoo.

## V. Store Specifics: Renyi Store (仁義店)
- **Focus**: Optimization of Merchant Backend (商家後台) for Renyi Store.
- **Exclusion**: Chongxin Main Store (重新總店) is NOT included in this integration.
- **Goal**: Automate backend operations (inventory, ordering) specifically for Renyi's workflow.


## VI. Pricing Logic & Strategy
### 1. The Anchor Price Rule (基準價原則)
- **Medium Size (M)** is strictly defined as the **Base Price Anchor** (基準價).
- All Main Item prices listed in the menu correspond to the **Medium Size** variant.

### 2. Variant Pricing Logic
- **Pricing Formula**: Final Price = Base Price (M) + Modifier Delta
- **Delta Examples**:
  - **Medium (M)**: Delta =  (Baseline)
  - **Large (L)**: Delta = + (Upsize Charge)
  - **Small (S)**: Delta = - (Downsize Deduction - **CRITICAL: System must support negative pricing modifiers**)

### 3. Implementation Requirement
- **Odoo**: Use product.template price for Medium. Configure product.attribute.value with price_extra for L (+30) and S (-15).
- **Quick Click API**: Ensure the options payload correctly maps these signed integer values for price adjustments.


### 4. Category-Specific Sizing Pricing (重要規則)
- **Logic**: The price delta for sizes (L/S) is NOT universal. It varies by **Product Category** (飲品類別) or specific item groups.
- **Constraint**: price_extra cannot be a global constant.
- **Implementation**: product.attribute.value must be configured specifically for each product.template or category group to reflect varying costs.
  - Example A (Tea): L = +
  - Example B (Coffee): L = +


## VII. Android POS (4G) Integration Strategy
### 1. Role Definition: The Field Agent
- **Device**: Android POS with independent 4G LTE.
- **Function**:
  - **Resilience Anchor**: Operates even if Store Wi-Fi/Broadband fails.
  - **Data Sync Node**: Pushes transaction data back to Ulter Node (Odoo) via Cloud API.
  - **Developer Mode**: Enabled for custom agent installation (e.g., Sync Service).

### 2. Sync Protocol (The Bridge) - 4G Extension
- **Mode**: Active Push (Android -> Cloud -> Ulter Node).
- **Offline Capability**: Stores transactions locally (SQLite/JSON) when 4G is unstable, auto-pushes when reconnected.
- **Identity**: Tagged with pos_id: android_4g_001 in all JSON payloads for source tracking.
