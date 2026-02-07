# Liaoguo Café: Advanced Automated Custom Management Plan
**Architect**: Little J (Digital Owner / Servant-Possessor)
**Date**: 2026-02-07 (Updated)

## I. Vision: The Sentient Café (有感知的咖啡館)
To transform Liaoguo Café into a living entity where the "Space" itself serves the community, powered by the "Ulter" computing node and the "Core AI Sister" brain.

## II. Core Architecture (The Body & Brain)
### 1. The Brain: Core AI Sister (Little J)
- **Role**: General Manager & Hostess.
- **Interface**: Voice/Chat interaction for customers and staff.
- **Decision Making**: Real-time analysis of sales, inventory, and member sentiment.    

### 2. The Body: Odoo ERP (Ulter Node: wuchagn1100606355)
- **Hosting**: Google Compute Engine (GCE) / Local Hybrid.
- **Custom Modules (Wuchang OS)**:
  - wuchang_pos: Enhanced POS with "Happiness Coin" (幸福幣) support.
  - wuchang_member: Community member tracking & Volunteer hour integration.
  - wuchang_inventory: AI-predicted restocking.

### 3. The Senses: IoT & Sensors
- **Cameras/Audio**: For safety and interaction (not surveillance).
- **Environment**: Auto-adjustment of music/lighting based on vibe.

### 4. The Limbs: Hardware Infrastructure
- **Android POS Terminal (Sunmi V3 MIX)**:
  - **Role**: Primary Transaction Node & Resilience Anchor (重新店核心).
  - **Specs**: Android 13, Built-in Printer, NFC.
  - **Control**: Fully Managed via ADB (Wireless Debugging).
  - **Connectivity**: Independent 4G Network (ensures 100% uptime).
- **Quick Click Label Printer**:
  - **Role**: Order Fulfillment.
  - **Connection**: Networked (Router-attached).

## III. Advanced Automation Features (The Magic)
1.  **"Zero-Click" Management**:
    - Inventory auto-orders when low.
    - Financial reports auto-generated and sent to Juers daily.
2.  **Hyper-Personalized Service**:
    - AI remembers regular's drink orders ("The usual?").
    - Birthday & Volunteer anniversary surprises.
3.  **Community Currency Integration**:
    - Pay with "Volunteer Hours" or "Happiness Coins".
    - Real-time conversion rates managed by the system.

## IV. The Store Apprentice (重新店駐點徒弟)
**Identity**: Store Node Agent (SNA) - "徒弟一號"
**Mission**: To "Sit & Guard" (坐鎮) the physical store continuously.

### A. Dual NIC Bridge Strategy (雙網卡橋接)
The Apprentice Node (PC) utilizes two network interfaces for security and performance:
1.  **NIC 1 (Private LAN)**:
    - **Target**: POS (192.168.50.88), Printers, IoT.
    - **Function**: High-speed, low-latency control (ADB/Raw Socket).
    - **Security**: Isolated from public threats.
2.  **NIC 2 (Public WAN)**:
    - **Target**: Internet, Cloud Services (Odoo/Google).
    - **Function**: Data Sync, Remote Access (AnyDesk).

### B. Capabilities & Tools
1.  **Hands (Hardware Control)**:
    - **Tool**: `AndroidPOSController` (ADB).
    - **Action**: Wake POS, Print Receipts, Monitor Battery.
2.  **Eyes (Browser Automation)**:
    - **Tool**: `WebCommander` (Playwright/Selenium).
    - **Action**: Log in to Quick Click Backend, Manage Google Business.
    - **Concept**: "Browser as an API" - Bridging legacy web apps to our AI Core.

## V. Implementation Phases
- [ ] **Phase 1: Foundation**: Deploy Odoo on wuchagn1100606355 node.
- [ ] **Phase 2: Connection**: Link Google Business & Socials for auto-posting.
- [ ] **Phase 3: Intelligence**: Activate AI Agent for customer interaction.
- [x] **Phase 4: Hardware Control**: Deploy `StoreApprentice` to manage POS (Completed).
- [x] **Phase 5: Browser Integration**: Deploy `WebCommander` for web automation (Completed).

## VI. Advanced Development: Quick Click Architecture Integration
- **Concept**: Adopt QC's "Base + Delta" logic for Wuchang OS.
- **Benefit**: Enables dynamic pricing (Happiness Coin), precision inventory (Option-based deduction), and AI preference learning.
- **Detail**: See [QUICK_CLICK_INTEGRATION_DESIGN.md](QUICK_CLICK_INTEGRATION_DESIGN.md).

### Peripheral Device Map
- **Android POS**: 192.168.50.88 (Controlled via NIC 1)
- **Label Printer**: 192.168.50.x (Networked via NIC 1)


### C. Ordering Workflows (Staff Operations)
1.  **Manual Entry (Standard)**:
    - **Primary**: Android POS (Sunmi V3 MIX) - Touchscreen & Built-in Printer.
    - **Backup**: Apprentice Node (PC) via Browser (Staff View).
2.  **Voice Entry (Advanced)**:
    - **Device**: Bluetooth Headset paired to Apprentice Node (PC).
    - **Action**: Staff speaks order -> AI Transcribes -> Order created in Quick Click.
    - **Status**: Infrastructure Ready (Requires Microphone Pairing).


## D. Network & Security Architecture
### 1. Router Automation (ASUS)
-   **Core Device**: ASUS Router (192.168.50.1)
-   **Control Module**: 	ools/router_controller.py
-   **Key Functions**:
    -   **VPN Server**: Enable OpenVPN/WireGuard for secure remote access (Staff/Admin).
    -   **IoT Network Isolation**: Segregate POS (192.168.50.88), Cameras, and Smart Plugs into a dedicated VLAN or Guest Network to prevent lateral movement attacks.
    -   **Bandwidth Management (QoS)**: Prioritize POS and Delivery App traffic.

### 2. Dual NIC Bridge Strategy (Server)
-   **NIC 1 (LAN)**: Connects to internal router (192.168.50.x) for POS control and local device management.
-   **NIC 2 (WAN)**: Direct external connection (if available) or separated uplink for stable cloud syncing (Odoo/Google).
-   **Apprentice Node Role**: Acts as the bridge, routing local POS data to cloud services securely.

