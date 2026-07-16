# ADR-0012: Mock-First Validation Strategy

## Status
Accepted

## Date
2026-07-16

## Context
Before investing months in full-stack development, we need to validate that the Nexus Admin Portal matches real-world business workflows. The target users (business owners, managers, technicians) have domain-specific processes that may not be obvious to developers.

Building a static HTML/CSS/JS mock allows us to:
- Validate workflows with real users in hours, not months
- Get feedback on screen layout, data visibility, and navigation
- Confirm the hierarchical tenant model (institution → branch) works intuitively
- Discover missing features before they become expensive rework

## Decision
**Build a static mock site first, deploy to beta, iterate with users, THEN build the real app.**

### Mock covers 3 personas
| Persona | Screens | Key Actions |
|---|---|---|
| Business Owner (Admin) | Dashboard, All Appointments, All Customers, Revenue | Switch branches, see KPIs |
| Manager | Dashboard, Appointments, Jobs, Invoices | Schedule, assign techs, approve invoices |
| Technician | My Jobs Today, Job Detail | View address, mark complete, add notes |

### Mock Architecture
```
mock/
├── Dockerfile              # nginx:alpine serving static files
├── public/
│   ├── index.html          # SPA entry (hash-based routing)
│   ├── css/style.css       # Nexus design tokens
│   └── js/
│       ├── mock-data.js    # Realistic fake data
│       ├── router.js       # Hash-based navigation
│       └── app.js          # Screen rendering, interactions
```

### Validation Process
1. Deploy to beta (192.168.1.31:3678)
2. Share URL with 2-3 business owners
3. Watch them use it (screen share)
4. Collect feedback, update mock (hours)
5. Repeat until workflows confirmed
6. Lock confirmed mock as spec for real implementation

## Rationale
- **Static HTML, not React**: Zero build step, instant feedback, no framework lock-in
- **Hash-based routing**: Works with nginx static serving, zero config
- **Not Figma**: Users treat a browser page as "working software" and give more honest feedback

## Consequences
- 10x faster feedback than building real app first
- Zero backend rework if mock reveals wrong assumptions
- Mock serves as living documentation for real implementation
- Risk: mock may set unrealistic timeline expectations (mitigated by labeling as "Preview")