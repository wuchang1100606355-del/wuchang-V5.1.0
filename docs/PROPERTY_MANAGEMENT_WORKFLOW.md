# Property Management Workflow Analysis & Design

## 1. Overview
This document outlines the standard operating procedures (SOP) and system workflows implemented in the `wuchang_property_toolkits` module. It addresses the previous gap where property management lacked defined digital workflows.

## 2. Core Workflows

### 2.1 Maintenance Request Workflow (報修流程)
The primary workflow handles resident maintenance requests for public areas or private units.

**State Machine:**
1.  **Draft (草稿)**: Resident creates a request but hasn't submitted it.
2.  **Submitted (已提交)**: Request is sent to the Property Management Office.
3.  **In Progress (處理中)**: Manager assigns the task to a maintenance staff member.
4.  **Done (已完成)**: Work is completed and verified.
5.  **Cancelled (已取消)**: Request is invalid or withdrawn.

**Actors:**
- **Reporter (Resident)**: Initiates the request.
- **Manager**: Reviews, prioritizes (Low/Normal/High/Urgent), and assigns tasks.
- **Assignee (Staff)**: Performs the work and updates status.

**Data Model (`wuchang.property.maintenance`):**
- `subject`: Brief title of the issue.
- `category`: Public Area, Electrical, Plumbing, Structural, Other.
- `priority`: 0 (Low) to 3 (Urgent).
- `location`: Specific block/unit or facility name.

### 2.2 Future Workflows (Planned)
- **Facility Booking**: Reservation system for clubhouse/gym.
- **Fee Management**: Integration with `wuchang_finance` for management fee collection.
- **Visitor Pass**: QR code generation for visitor access.

## 3. Implementation Details
- **Module**: `wuchang_os/addons/wuchang_property_toolkits`
- **Model**: `models/property_maintenance.py`
- **Views**: `views/property_maintenance.xml` (Tree, Form, Kanban, Search)
- **Security**: Access rights defined in `security/ir.model.access.csv`.

## 4. User Interface
- **Backend**: Dedicated "Property Mgmt" menu item.
- **Frontend**: Accessible via `/hoa/site` (Maintenance Card) -> *Updated to link to new form in future iteration*.
