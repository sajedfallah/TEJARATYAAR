# TEJARATYAAR Product Specification

## Product Goal

Build a customs operations CRM that manages the full lifecycle from customer request to closed shipment case.

## Core Concepts

### Case

The Case is the central operational entity.

A Case contains:

- Customer
- Customs
- Case Type
- Owner
- Tasks
- Documents
- Activities
- Requests
- Commitments
- Milestones
- Customer Updates
- Audit History

## Lifecycle

```
Customer Request
        ↓
Pre-Case
        ↓
Kotaaj Registration
        ↓
Active Case
        ↓
Workflow Execution
        ↓
Closure
        ↓
Customer Satisfaction
```

## Roles

- Manager
- Supervisor
- Employee
- Customer

## Main V1 Modules

- CRM
- Case Management
- Task Management
- Document Center
- Customer Requests
- Workflow Templates
- Notifications
- Dashboards
- Audit Logs

## Design Rules

1. Internal status and customer status are separated.
2. Customer only sees authorized information.
3. Every operational commitment must be trackable.
4. Every sensitive action must be audited.
