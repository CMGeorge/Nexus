# Nexus SaaS — User Stories

Organized by bounded context, prioritized by role.

## Legend
- **Role**: Admin | Manager | Employee | Customer
- **Priority**: P0 (MVP) | P1 (v1.0) | P2 (v1.1) | P3 (future)

---

## 1. Auth & Security

| ID | Story | Role | Priority |
|----|-------|------|----------|
| AUTH-01 | As a new user, I want to register with email and password so that I can access the platform | Any | P0 |
| AUTH-02 | As a registered user, I want to log in and receive a JWT token so that I can use the platform securely | Any | P0 |
| AUTH-03 | As a logged-in user, I want my session to auto-refresh via refresh tokens so that I don't get logged out during work | Any | P0 |
| AUTH-04 | As a user, I want to log out and have my tokens invalidated so that my session is properly closed | Any | P0 |
| AUTH-05 | As a user, I want to reset my password via email so that I can regain access if I forget it | Any | P1 |
| AUTH-06 | As a user, I want to enable TOTP-based MFA so that my account is protected against password theft | Any | P1 |
| AUTH-07 | As an MFA user, I want to receive backup codes during enrollment so that I can still log in if I lose my authenticator device | Any | P1 |
| AUTH-08 | As an MFA user, I want a "remember this device" option so that I don't have to enter a code on my trusted devices every time | Any | P2 |
| AUTH-09 | As an MFA user, I want email OTP as a fallback so that I can authenticate even without my TOTP app | Any | P2 |
| AUTH-10 | As an admin, I want to force MFA enrollment for all users in my company so that tenant security is enforced | Admin | P2 |

## 2. Companies (Tenants)

| ID | Story | Role | Priority |
|----|-------|------|----------|
| COMP-01 | As a new user, I want to create a company (tenant) during registration so that I can start using the platform for my business | Any | P0 |
| COMP-02 | As an admin, I want to edit my company profile (name, logo, address, phone) so that my business information is accurate | Admin | P0 |
| COMP-03 | As an admin, I want to set my company's branding (colors, logo) so that the platform reflects my business identity | Admin | P2 |
| COMP-04 | As an admin, I want to manage my subscription tier (Free/Pro/Enterprise) so that I can access features appropriate for my business | Admin | P1 |
| COMP-05 | As an admin, I want to view my company's usage statistics (number of appointments, invoices, storage used) so that I can track platform adoption | Admin | P2 |

## 3. Users & Roles

| ID | Story | Role | Priority |
|----|-------|------|----------|
| USER-01 | As an admin, I want to invite team members (employees, managers) to my company so that they can use the platform | Admin | P0 |
| USER-02 | As an admin, I want to assign roles (Admin, Manager, Employee) to users so that they have appropriate permissions | Admin | P0 |
| USER-03 | As an admin, I want to deactivate or remove users from my company so that former employees no longer have access | Admin | P1 |
| USER-04 | As a user, I want to edit my profile (name, phone, avatar) so that my information stays current | Any | P1 |
| USER-05 | As an admin, I want to view the audit log showing who did what and when so that I have accountability across the platform | Admin | P2 |

## 4. Customers

| ID | Story | Role | Priority |
|----|-------|------|----------|
| CUST-01 | As an employee, I want to create a new customer with name, email, phone, and address so that I can manage my client list | Employee | P0 |
| CUST-02 | As an employee, I want to search my customer list by name, email, or phone so that I can quickly find a specific client | Employee | P0 |
| CUST-03 | As an employee, I want to view a customer's full history (appointments, jobs, invoices, files) so that I have complete context before interacting with them | Employee | P1 |
| CUST-04 | As an employee, I want to edit customer information so that it stays accurate over time | Employee | P0 |
| CUST-05 | As an employee, I want to add notes to a customer profile so that I can record important context | Employee | P2 |
| CUST-06 | As an employee, I want to import customers from a CSV file so that I can migrate from another system | Employee | P2 |

## 5. Appointments

| ID | Story | Role | Priority |
|----|-------|------|----------|
| APPT-01 | As an employee, I want to create an appointment with a date, time, customer, and service description so that it appears on my calendar | Employee | P0 |
| APPT-02 | As an employee, I want to view my appointments in a calendar view (day/week/month) so that I can plan my schedule | Employee | P0 |
| APPT-03 | As an employee, I want to set appointment status (confirmed, in-progress, completed, cancelled) so that I can track work progress | Employee | P0 |
| APPT-04 | As an employee, I want to receive reminders about upcoming appointments so that I don't miss scheduled work | Employee | P1 |
| APPT-05 | As a customer, I want to receive an email/SMS confirmation when an appointment is scheduled so that I know when the technician will arrive | Customer | P1 |
| APPT-06 | As an admin, I want to view all appointments across my team so that I can manage workload and scheduling conflicts | Admin | P1 |
| APPT-07 | As an employee, I want to drag-and-drop reschedule an appointment so that I can adapt to schedule changes quickly | Employee | P2 |

## 6. Jobs (Work Orders)

| ID | Story | Role | Priority |
|----|-------|------|----------|
| JOB-01 | As an employee, I want to create a job from an appointment (or directly) with a description, customer, and assigned employee so that work is tracked | Employee | P0 |
| JOB-02 | As an employee, I want to update job status (pending, in-progress, completed, invoiced) so that I can track work through its lifecycle | Employee | P0 |
| JOB-03 | As an employee, I want to add photos to a job (before/after) so that I have visual documentation of the work | Employee | P1 |
| JOB-04 | As an employee, I want to add parts/materials used to a job so that costs are tracked for invoicing | Employee | P1 |
| JOB-05 | As an employee, I want to record time spent on a job so that labor costs are tracked for invoicing | Employee | P1 |
| JOB-06 | As an admin, I want to view job completion rates and average duration so that I can measure team performance | Admin | P2 |

## 7. Invoices

| ID | Story | Role | Priority |
|----|-------|------|----------|
| INV-01 | As an employee, I want to generate an invoice from a completed job (auto-populated with parts, labor, customer) so that I don't double-enter data | Employee | P0 |
| INV-02 | As an employee, I want to create an invoice manually (for work without a job) so that I can bill for any service | Employee | P0 |
| INV-03 | As an employee, I want to send an invoice to a customer via email so that they can review and pay | Employee | P0 |
| INV-04 | As an employee, I want to mark an invoice as paid so that my records are up to date | Employee | P0 |
| INV-05 | As an employee, I want to generate a PDF of an invoice so that I can print or share it | Employee | P1 |
| INV-06 | As an admin, I want to view all invoices with status (draft, sent, paid, overdue) so that I can manage cash flow | Admin | P1 |
| INV-07 | As an admin, I want to export invoices to CSV for accounting so that I can integrate with external accounting software | Admin | P2 |
| INV-08 | As a customer, I want to view and pay my invoices through a customer portal so that I can manage my account online | Customer | P2 |

## 8. Notifications

| ID | Story | Role | Priority |
|----|-------|------|----------|
| NOTIF-01 | As a user, I want to receive email notifications for important events (appointment scheduled, invoice sent) so that I stay informed | Any | P1 |
| NOTIF-02 | As an admin, I want to configure which notification types my company sends so that we don't spam customers | Admin | P2 |
| NOTIF-03 | As an employee, I want to receive push notifications on mobile for upcoming appointments so that I'm reminded on the go | Employee | P2 |
| NOTIF-04 | As a customer, I want to opt out of marketing notifications so that I only receive transactional messages | Customer | P2 |

## 9. Files & Documents

| ID | Story | Role | Priority |
|----|-------|------|----------|
| FILE-01 | As an employee, I want to upload files (photos, documents, PDFs) to a customer or job so that all related documents are in one place | Employee | P0 |
| FILE-02 | As an employee, I want to view and download uploaded files so that I can reference them | Employee | P0 |
| FILE-03 | As an employee, I want to generate and store invoice PDFs automatically so that they are always available | Employee | P1 |
| FILE-04 | As an employee, I want to see a thumbnail preview of uploaded images so that I can quickly identify files | Employee | P2 |
| FILE-05 | As an admin, I want to see total storage usage per company so that I can manage quotas | Admin | P2 |

## 10. Search & Reporting

| ID | Story | Role | Priority |
|----|-------|------|----------|
| SRCH-01 | As a user, I want a global search that finds customers, appointments, jobs, and invoices by keyword so that I don't have to navigate to each section | Any | P2 |
| SRCH-02 | As an admin, I want to generate reports (revenue by period, jobs by employee, customer activity) so that I can make business decisions | Admin | P2 |
| SRCH-03 | As an employee, I want to filter any list by date range, status, and assigned user so that I can narrow down results | Employee | P1 |

---

## Summary

| Domain | Stories | P0 (MVP) | P1 (v1.0) | P2 (v1.1) |
|--------|---------|----------|-----------|-----------|
| Auth & Security | 10 | 4 | 3 | 3 |
| Companies | 5 | 2 | 1 | 2 |
| Users & Roles | 5 | 2 | 2 | 1 |
| Customers | 6 | 3 | 1 | 2 |
| Appointments | 7 | 3 | 2 | 2 |
| Jobs | 6 | 2 | 3 | 1 |
| Invoices | 8 | 4 | 2 | 2 |
| Notifications | 4 | 0 | 1 | 3 |
| Files | 5 | 2 | 1 | 2 |
| Search & Reporting | 3 | 0 | 1 | 2 |
| **Total** | **59** | **22** | **17** | **20** |

### MVP Boundary (22 stories)
The minimum viable product covers: registration/login, company creation, user invites with roles, customer CRUD, appointment scheduling with status tracking, job creation, invoice generation from jobs, and file uploads. A business can manage its full workflow with these 22 stories.
