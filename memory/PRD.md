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
- [x] Conversation History page (/dashboard/conversations) with:
  - Search by keyword, filter by chatbot/date range
  - Paginated list of conversations grouped by session_id
  - Click-to-view full conversation thread in dialog
  - CSV export with GDPR consent logging
- [x] Always-visible usage bar on dashboard (messages used/limit with color coding)
- [x] Message auto-delete cleanup endpoint (POST /api/maintenance/cleanup-expired) for GDPR 90-day retention
- [x] IP anonymization (SHA-256 hash at message collection - already in place since Phase 1)
- [x] Account deletion with 30-day grace period (already in place since Phase 1)
- [x] Sidebar navigation updated with Conversations link

### Phase 7 — Backend Refactoring (Apr 15, 2026)
- [x] Refactored server.py from 1852-line monolith → 62-line thin entrypoint
- [x] Created shared modules: database.py, config.py, models.py, auth_utils.py, templates_data.py
- [x] Created 12 modular route files under routes/:
  - auth.py, chatbots.py, chat.py, domain.py, analytics.py, billing.py
  - conversations.py, team.py, privacy.py, templates.py, embed.py, ai_config.py
- [x] Full regression test: 45/45 backend tests + all frontend tests passed (100%)

## Prioritized Backlog

### P0 (Critical)
- [x] ~~Backend Refactoring~~ — COMPLETED: server.py split into 12 modular routes + 5 shared modules

### P1 (High)
- [ ] User Rights Center — "Download my data" JSON export from /account/privacy page
- [ ] Invoice PDF generation (German tax §257 HGB)
- [ ] Data retention cron job (auto-delete messages after 90 days on schedule)
- [ ] Wire Ollama into chat endpoint based on ai_config
- [ ] Unanswered question logging and tracking

### P2 (Medium)
- [ ] CSV export for analytics page
- [ ] Embed.js domain lock — widget only loads on verified domain
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

## Next Tasks
1. User Rights Center (download my data JSON from /account/privacy)
2. Invoice PDF generation (German tax compliant)
3. Unanswered question logging
4. Embed.js domain lock (widget only on verified domain)
5. Data retention cron job
