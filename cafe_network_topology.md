# Wuchang Cafe Network Topology & Strategy

## 核心策略 (Core Strategy)
1.  **Dual NIC Architecture**:
    -   **Wired LAN (Ethernet)**: 192.168.50.249 (Static). Dedicated for high-speed internal traffic (POS, Odoo, Brain Node).
    -   **Wireless WAN (Wi-Fi)**: Public internet access via Router (192.168.50.1).
    -   **Isolation**: Ensures heavy internal data (Quantum/Brain) doesn't clog the public Wi-Fi.

## 設備清單 (Device List)
-   **Router (Gateway)**:
    -   Model: ASUS RT-BE86U (High Performance)
    -   IP: 192.168.50.1
    -   Services: DHCP, Firewall, Port Forwarding, VPN Server
    -   **Status**: Domain Conflict Resolved (LAN domain adjusted to avoid wuchang.life hijack).
-   **Server (Brain/Quantum Node)**:
    -   IP: 192.168.50.249 (Locked via Router & Static Config)
    -   Hostname: wuchang-brain / wuchang.local
    -   Services: Odoo (8069), Trae AI Agent, Docker Containers
-   **User Device (Admin)**:
    -   IP: 192.168.50.84 (Connected via VPN/Wi-Fi)
    -   Role: System Administrator (Juers)

## 網路服務 (Network Services)
### 1. 內部服務 (Internal)
-   **Odoo POS**: http://192.168.50.249:8069
-   **Brain Node API**: http://192.168.50.249:8000 (Internal)

### 2. 外部存取 (Public Access)
-   **Domain**: https://wuchang.life (Cloudflare Tunnel)
-   **Tunnel Status**: *Configuration Pending (Origin Cert/DNS)*
-   **VPN Access**: Active (User verified connection to internal subnet).

## 路由配置 (Router Configuration)
-   **Port Forwarding**:
    -   External 80   -> 192.168.50.249:80
    -   External 443  -> 192.168.50.249:443
    -   External 8069 -> 192.168.50.249:8069
-   **DHCP Reservation**:
    -   MAC [Server-MAC] -> 192.168.50.249

## 最新更新 (Latest Updates)
-   **2026-02-05**: User confirmed IP 192.168.50.84. Photos received in isual_assets/avatar. Router domain conflict resolved.
