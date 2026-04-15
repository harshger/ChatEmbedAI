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
- [x] Google OAuth users get empty domain fields, can set website later
- [x] Domain verification endpoints: GET /api/domain/status, POST /api/domain/init, POST /api/domain/verify
- [x] Sidebar "Domain" link in dashboard navigation

## Prioritized Backlog

### P1 (High)
- [ ] Conversation History page — browse/search/filter past chatbot conversations, CSV export
- [ ] Invoice PDF generation (German tax §257 HGB)
- [ ] Data retention jobs (auto-delete messages after 90 days)
- [ ] Wire Ollama into chat endpoint based on ai_config

### P2 (Medium)
- [ ] CSV export for analytics
- [ ] Embed.js domain lock — widget only loads on verified domain
- [ ] Docker Compose deployment setup
- [ ] Domain whitelist per chatbot (CORS)

### P3 (Nice to have)
- [ ] 2FA support, Redis caching, robots.txt/sitemap
- [ ] More templates (Hotel, Autowerkstatt, Steuerberater)
- [ ] Backup scripts

## Next Tasks
1. Conversation History page (browse, search, filter, CSV export)
2. Invoice PDF generation (German tax compliant)
3. Data retention jobs
4. Embed.js domain lock (widget only on verified domain)
