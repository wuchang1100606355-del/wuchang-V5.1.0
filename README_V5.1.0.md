# Wuchang V5.1.0 - System Architecture

**Version:** 5.1.0 (Server Directed Optimization)
**Created Date:** 2026-01-12
**Architect:** Xiao J (Secretary General)

## Overview

Wuchang V5.1.0 has evolved into a **Server Directed** architecture, optimizing the collaboration between the Local Node (Windows) and the Central Server (Linux). This mode prioritizes centralized control, passive synchronization, and secure remote management.

## 📘 User Manual
**👉 [Click Here to Read the User Manual (Server Directed Mode)](docs/manuals/USER_MANUAL_SERVER_DIRECTED.md)**

## Directory Structure

-   **`remote_ui_control/`**: (Core) UI Control Server and Cloud Sync Service.
-   **`scripts/`**: Automation scripts, including system verification and handshake monitors.
-   **`wuchang_os/`**: Core Odoo addons and web assets.
-   **`config/`**: System configurations.
-   **`memory_store/`**: The AI's long-term memory.
-   **`docs/`**: System documentation and SOPs.

## Key Features

1.  **Server Directed Mode:** The local node operates passively, awaiting commands from the server.
2.  **UI Remote Control:** Server can trigger local UI actions (Odoo, AI, Browser).
3.  **Secure SSH Access:** Dedicated `wuchang` user with key-based authentication.
4.  **AI Core:** Fully integrated with Google Vertex AI (Gemini Pro).

## Quick Start

1.  **Start System:** `.\start_server_directed_mode.ps1`
2.  **Verify Status:** `.\scripts\verify_user_flow.ps1`
3.  **Monitor:** `python scripts/monitor_and_handshake.py`
