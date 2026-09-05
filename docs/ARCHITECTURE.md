# TEJARATYAAR Architecture

## High Level

```
Telegram
   |
   +-- Bot
   |
   +-- Mini App
          |
       API Layer
          |
   Business Modules
          |
 PostgreSQL + Redis + Storage
```

## Planned Backend Modules

- Authentication
- Users and Permissions
- CRM
- Cases
- Tasks
- Documents
- Requests
- Workflow
- Notifications
- Reports
- Audit

## Architecture Decision

V1 uses a modular monolith approach.

Microservices are intentionally postponed until scale requires separation.

## Security

- Role Based Access Control
- Case Level Access
- Document Permissions
- Audit Trail
- Secure Configuration
