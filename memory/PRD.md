# ChatEmbed AI — Product Requirements Document

## Original Problem Statement
Build a complete SaaS web app called "ChatEmbed AI" — an AI-powered chatbot builder for small businesses in Europe (with proper websites), fully optimized for the German market and 100% GDPR compliant. Business owners paste FAQ, and an embeddable chatbot is created. Domain verification required to prevent misuse.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI (Python) + MongoDB
- **AI**: Claude Sonnet via Emergent LLM Key (active) + Ollama config (self-hosted option)
- **Payments**: Stripe (test key, subscription model)
- **Auth**: JWT + Google OAuth via Emergent Auth
- **Email**: Mocked (console logging)
- **Design**: Swiss & High-Contrast (Klein Blue #002FA7, IBM Plex Sans + Clash Display)

## User Personas
1. **German Small Business Owner** (with website) — needs a simple chatbot for FAQ, values GDPR compliance
2. **Agency/Consultant** — manages multiple client chatbots, needs white-label
3. **EU-based Entrepreneur** — multilingual support across 15 European languages

## Core Requirements (Static)
- Website URL required at registration — businesses must have a website
- Domain verification (Meta Tag or DNS TXT) before chatbot widget goes live
- GDPR-compliant cookie consent banner (German law TDDDG)
- Impressum, Datenschutzerklärung, AGB, AVV pages
- Data export and deletion (DSGVO user rights)
- Multilingual AI chatbot (15 European languages)
- Stripe subscriptions with EUR pricing (4 tiers)

## What's Been Implemented

### Phase 1 — MVP
- [x] Landing page (DE/EN toggle), auth (JWT + Google), dashboard, chatbot CRUD
- [x] Claude AI chat API, embed code generator, chat widget preview
- [x] Pricing page (4 tiers), Stripe checkout, legal pages, privacy center
- [x] Cookie consent, consent logging, rate limiting

### Phase 2 — Templates & Team
- [x] 6 German business chatbot templates
- [x] Standalone embed.js widget, team management (Agency gated)

### Phase 3 — Auth Flows & Analytics
- [x] Email verification (double opt-in, mocked), password reset (mocked)
- [x] Enhanced analytics: recharts bar/pie charts, peak hours, top questions

### Phase 4 — Widget Customization, AI Engine & Billing
- [x] Dashboard email verification banner with one-click verify
- [x] Widget customization: colors, position, greeting, logo, corner style, branding removal (paid gated)
- [x] Enhanced Billing page with plan comparison and upgrade/downgrade
- [x] AI Engine settings (Claude vs Ollama) with config storage

### Phase 5 — Domain Verification System
- [x] Website URL required at registration (with URL normalization + domain extraction)
- [x] Domain verification page (/dashboard/verify-domain) with two methods:
  - Meta Tag: `<meta name="chatembed-verify" content="TOKEN">`
  - DNS TXT: `chatembed-verify=TOKEN`
- [x] Dashboard domain verification banner (yellow, links to verify page)
- [x] Public chatbot endpoint returns domain_verified and allowed_domain

### Phase 6 — Conversation History & GDPR Hardening (Apr 15, 2026)
- [x] Conversation History page (/dashboard/conversations) with search, filters, pagination
- [x] CSV export with GDPR consent logging
- [x] Always-visible usage bar on dashboard
- [x] Message auto-delete cleanup endpoint
- [x] IP anonymization, Account deletion with 30-day grace period

### Phase 7 — Backend Refactoring (Apr 15, 2026)
- [x] Refactored server.py from 1852-line monolith → thin entrypoint
- [x] Created shared modules: database.py, config.py, models.py, auth_utils.py, templates_data.py
- [x] Created 12+ modular route files under routes/

### Phase 8 — GDPR Features & Invoice System (Apr 15, 2026)
- [x] **P0: Data Export (User Rights Center)** — Enhanced GET /api/user/export with comprehensive JSON:
  - export_info (with Art. 20 DSGVO reference), account (password_hash excluded), subscription, chatbots, messages, payment_transactions, team_members, consent_logs
  - Consent logging on every export
- [x] **P1: Invoice PDF Generation** — GET /api/billing/invoice/{transaction_id}/pdf:
  - German tax-compliant PDF with Rechnungsnummer, Netto/Brutto, 19% MwSt
  - Legal references: § 14 UStG, § 257 HGB
  - Company details, bank info, VAT ID
  - Frontend PDF download button per paid transaction in Billing page
- [x] **P2: Data Retention Background Job** — Automatic GDPR cleanup:
  - Background asyncio task runs every 24h
  - Deletes messages older than 90 days (expires_at + created_at fallback)
  - Processes pending account deletion requests (30-day grace period)
  - Manual trigger via POST /api/maintenance/cleanup-expired
- [x] **P2: Embed.js Domain Lock** — Widget security:
  - embed.js checks window.location.hostname against allowed_domain
  - Blocks widget rendering on unauthorized domains (domain_verified required)
  - Console warning logged when blocked

## Code Architecture
```
/app/
├── backend/
│   ├── server.py (Thin entrypoint + GDPR retention background task)
│   ├── database.py, config.py, models.py, auth_utils.py, templates_data.py
│   ├── routes/
│   │   ├── auth.py, chatbots.py, chat.py, domain.py, analytics.py, billing.py
│   │   ├── conversations.py, team.py, privacy.py, templates.py, embed.py
│   │   ├── ai_config.py, invoices.py
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── App.js, App.css, index.css
│   │   ├── components/ (DashboardLayout, ChatWidgetPreview, CookieConsent, etc.)
│   │   ├── lib/ (api.js, auth.js, i18n.js)
│   │   └── pages/ (20+ pages)
└── memory/
    ├── PRD.md
    └── test_credentials.md
```

## Prioritized Backlog

### P0 (Critical)
- [x] All P0 items completed

### P1 (High)
- [x] User Rights Center — data export ✓
- [x] Invoice PDF generation ✓
- [x] Data retention cron job ✓
- [ ] Wire Ollama into chat endpoint based on ai_config
- [ ] Unanswered question logging and tracking

### P2 (Medium)
- [x] Embed.js domain lock ✓
- [ ] CSV export for analytics page
- [ ] Docker Compose deployment setup
- [ ] Domain whitelist per chatbot (CORS)
- [ ] Custom widget logo upload
- [ ] REST API access for Pro/Agentur plans

### P3 (Nice to have)
- [ ] 2FA support, Redis caching, robots.txt/sitemap
- [ ] More templates (Hotel, Autowerkstatt, Steuerberater)
- [ ] Backup scripts
- [ ] Sub-account management (Agency)
- [ ] Custom chat domain (Agency)
- [ ] Status page
- [ ] OpenAPI/Swagger documentation

## Mocked Services
- Email sending (logged to console, tokens returned in API for demo)
- Stripe (test key, no real charges)

## Next Tasks
1. Ollama integration in chat endpoint
2. Unanswered question logging
3. CSV export for analytics
4. Docker Compose setup
