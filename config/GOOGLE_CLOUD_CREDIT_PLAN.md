# Google Cloud Performance & Credit Offset Plan (效能抵免額規劃)

## 1. Objective (目標)
Maximize the utilization of Google Cloud resources across managed accounts to offset performance costs, leveraging Free Tiers, Trial Credits, and **Google for Nonprofits (G4NP)** benefits.

## 2. Account Strategy (帳號策略)

### A. Ulter Computing Node (wuchagn1100606355@gmail.com)
*   **Role**: Primary Compute Offload (Ulter Power).
*   **Action Plan**:
    1.  **Activate GCP Free Trial**: Claim $300 credit for initial high-performance burst.
    2.  **Always Free Tier**: Deploy `e2-micro` instance (US regions) for continuous low-power tasks.
    3.  **Cloud Run**: Utilize 2 million requests/month free tier for stateless microservices.
    4.  **Purpose**: Dedicated "Ulter" computing tasks (Odoo data processing, background jobs).

### B. Wuchang Life Admin (admin@wuchang.life)
*   **Role**: Nonprofit & Production Stability.
*   **Action Plan**:
    1.  **Google for Nonprofits (G4NP)**: **High Priority**.
        *   **Workspace**: Activate "Google Workspace for Nonprofits" (Free Edition).
        *   **Cloud Credits**: Apply for $2,000/year (or more) in Google Cloud credits.
        *   **Ad Grants**: Activate $10,000/month Google Ads grant for community visibility.
        *   **Maps Platform**: Utilize $250/month credit for Spatiotemporal System maps.
    2.  **Verification**: Requires TechSoup validation token (User to provide).
    3.  **Purpose**: Hosting critical community services (DNS, Web Commander, Public Interface).

### C. Founder Account (o970106@gmail.com)
*   **Role**: Control & Backup.
*   **Action Plan**:
    1.  **Legacy Resources**: Maintain existing projects.
    2.  **BigQuery Sandbox**: Use for data analytics without credit card (1TB/month queries).
    3.  **Purpose**: Monitoring and architectural oversight.

## 3. Implementation Steps (執行步驟)
1.  [ ] **Ulter Setup**: Log in to `wuchagn1100606355` and activate GCP Free Trial.
2.  [ ] **Nonprofit Verification**:
    *   Log in to `admin@wuchang.life` (Google for Nonprofits).
    *   Submit TechSoup token for "Wuchang Life" (or associated association).
    *   Activate "Google Cloud Credits" product in G4NP portal.
3.  [ ] **Deployment**: Launch "Ulter-Node-01" (Dockerized worker).

## 4. Expected Benefits (預期效益)
*   **Cost Reduction**: Near-zero cost for initial 3 months + $2,000/year nonprofit credits covering ongoing usage.
*   **Performance**: Distributed load across multiple free-tier instances.
*   **Sustainability**: G4NP credits provide a renewable resource for community operations.

