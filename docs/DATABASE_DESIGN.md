# TEJARATYAAR Database Design

## Database

PostgreSQL

## Core Entities

- users
- roles
- permissions
- teams
- customers
- customer_contacts
- customs
- pre_cases
- cases
- case_types
- tasks
- documents
- requests
- activities
- commitments
- milestones
- notifications
- audit_logs

## Main Relationship

Customer → Cases → Operations

Cases own operational history and workflow state.

## Future

Full ERD and migrations will be added during backend implementation.
