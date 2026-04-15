# ChatEmbed AI — Product Requirements Document

## Original Problem Statement
Build a complete SaaS web app called "ChatEmbed AI" — an AI-powered chatbot builder for small businesses in Europe (with proper websites), fully optimized for the German market and 100% GDPR compliant. Business owners paste FAQ, and an embeddable chatbot is created. Domain verification required to prevent misuse.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI (Python) + MongoDB
- **AI**: Claude Sonnet via Emergent LLM Key (active) + Ollama (self-hosted option, now wired in)
- **Payments**: Stripe (test key, subscription model)
- **Auth**: JWT + Google OAuth via Emergent Auth
- **Email**: Mocked (console logging)
- **Design**: Swiss & High-Contrast (Klein Blue #002FA7, IBM Plex Sans + Clash Display)

## User Personas
1. **German Small Business Owner** (with website) — needs a simple chatbot for FAQ, values GDPR compliance
2. **Agency/Consultant** — manages multiple client chatbots, needs white-label
3. **EU-based Entrepreneur** — multilingual support across 15 European languages

## Core Requirements (Static)
- Website URL required at registration
- Domain verification (Meta Tag or DNS TXT) before widget goes live
- GDPR-compliant cookie consent banner (German law TDDDG)
- Legal pages: Impressum, Datenschutzerklärung, AGB, AVV
- Data export and deletion (DSGVO Art. 20 user rights)
- Multilingual AI chatbot (15 European languages)
- Stripe subscriptions with EUR pricing (4 tiers)
- Full DE/EN i18n across all dashboard pages

## What's Been Implemented

### Phase 1–7 — MVP through Backend Refactoring
- [x] Landing page, auth (JWT + Google), dashboard, chatbot CRUD
- [x] Claude AI chat, embed.js, pricing, legal pages, cookie consent
- [x] Templates, team management, email verification, password reset
- [x] Analytics, widget customization, billing, AI engine settings
- [x] Domain verification, conversation history, CSV export
- [x] Backend refactoring (modular routes)

### Phase 8 — GDPR Features & Invoice System (Apr 15, 2026)
- [x] Data Export (Art. 20 DSGVO) with comprehensive JSON
- [x] Invoice PDF Generation (German tax-compliant, §14 UStG, §257 HGB)
- [x] Data Retention Background Job (24h auto-cleanup of 90-day expired messages)
- [x] Embed.js Domain Lock (widget blocked on unauthorized domains)

### Phase 9 — Features & Full i18n (Apr 15, 2026)
- [x] **Customer Satisfaction Rating**: Thumbs up/down in embed.js widget, POST /api/chat/rate, satisfaction stats in Analytics
- [x] **Ollama Integration**: Chat endpoint checks ai_config, tries Ollama first if configured, falls back to Claude gracefully
- [x] **Unanswered Question Logging**: Auto-detects "can't answer" patterns in AI responses, logs to unanswered_questions collection, displayed in Analytics
- [x] **Analytics CSV Export**: GET /api/analytics/export/csv with Messages/Day, Top Questions, Chatbot Performance, Unanswered, Satisfaction
- [x] **Full i18n Translation Pass**: All dashboard pages (Billing, Analytics, AI Settings, Privacy Center, Dashboard, DashboardLayout sidebar) now use t.* translations for DE/EN

## Code Architecture
```
/app/
├── backend/
│   ├── server.py (Entrypoint + GDPR retention background task)
│   ├── database.py, config.py, models.py, auth_utils.py, templates_data.py
│   ├── routes/
│   │   ├── auth.py, chatbots.py, chat.py (Ollama + unanswered + ratings)
│   │   ├── domain.py, analytics.py (CSV export + unanswered + satisfaction)
│   │   ├── billing.py, invoices.py (PDF generation)
│   │   ├── conversations.py, team.py, privacy.py (data export)
│   │   ├── templates.py, embed.py (domain lock + satisfaction rating)
│   │   ├── ai_config.py
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── lib/ (api.js, auth.js, i18n.js — full DE/EN translations)
│   │   ├── components/ (DashboardLayout — translated sidebar)
│   │   └── pages/ (20+ pages, all using i18n)
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
- [x] Ollama integration ✓
- [x] Unanswered question logging ✓
- [x] Full i18n pass ✓

### P2 (Medium)
- [x] Embed.js domain lock ✓
- [x] CSV export for analytics ✓
- [x] Customer satisfaction rating ✓
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
- Ollama (no server running, falls back to Claude)

## Next Tasks
1. Docker Compose deployment setup
2. Domain whitelist per chatbot
3. REST API for Pro/Agentur plans
4. More German business templates
