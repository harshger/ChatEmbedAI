# ChatEmbed AI — Product Requirements Document

## Original Problem Statement
Build a complete SaaS web app called "ChatEmbed AI" — an AI-powered chatbot builder for small businesses in Europe, fully optimized for the German market and 100% GDPR compliant. Business owners paste FAQ, and an embeddable chatbot is created.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI (Python) + MongoDB
- **AI**: Claude Sonnet via Emergent LLM Key (active) + Ollama config (self-hosted option)
- **Payments**: Stripe (test key, subscription model)
- **Auth**: JWT + Google OAuth via Emergent Auth
- **Email**: Mocked (console logging)
- **Design**: Swiss & High-Contrast (Klein Blue #002FA7, IBM Plex Sans + Clash Display)

## User Personas
1. **German Small Business Owner** — needs a simple chatbot for FAQ, values GDPR compliance
2. **Agency/Consultant** — manages multiple client chatbots, needs white-label
3. **EU-based Entrepreneur** — multilingual support across 15 European languages

## Core Requirements (Static)
- GDPR-compliant cookie consent banner (German law TDDDG)
- Impressum page (legally mandatory in Germany)
- Datenschutzerklärung, AGB, AVV pages
- Data export and deletion (DSGVO user rights)
- Multilingual AI chatbot (15 European languages)
- Stripe subscriptions with EUR pricing (4 tiers)

## What's Been Implemented

### Phase 1 — MVP (April 15, 2026)
- [x] Landing page (German/English toggle) with hero, features, testimonials, trust section
- [x] GDPR cookie consent banner (3 categories: necessary/analytics/marketing)
- [x] Auth: Registration, Login, Google OAuth, session management
- [x] Dashboard with chatbot cards, stats, usage tracking
- [x] Chatbot CRUD (create/read/update/delete)
- [x] AI Chat API with Claude Sonnet (multilingual system prompt)
- [x] Embed code generator (HTML/WordPress/Wix/Shopify tabs)
- [x] Chat widget preview with GDPR notice
- [x] Pricing page (Free/Starter/Pro/Agency, EUR pricing with MwSt.)
- [x] Stripe checkout integration for plan upgrades
- [x] Legal pages: Impressum, Datenschutz, AGB, AVV, Privacy Policy (EN), Terms (EN)
- [x] Privacy center: Data export (JSON), account deletion with LÖSCHEN confirmation
- [x] Analytics page (Pro+ gated)
- [x] Billing page with payment history
- [x] Consent logging to MongoDB
- [x] Rate limiting and plan message limits

### Phase 2 — Templates & Team (April 15, 2026)
- [x] Chatbot Templates (6 German business types)
- [x] Standalone embed.js widget
- [x] Team management page (Agency plan gated)
- [x] CORS fix for cross-origin auth

### Phase 3 — Auth Flows & Analytics (April 15, 2026)
- [x] Email verification flow (double opt-in) with mocked emails
- [x] Password reset flow with mocked emails
- [x] Enhanced Analytics with recharts (bar charts, pie chart, peak hours, top questions)
- [x] Forgot Password, Reset Password, Verify Email pages

### Phase 4 — Widget Customization, AI Engine & Billing (April 15, 2026)
- [x] Dashboard email verification banner with one-click verify (demo mode)
- [x] Widget customization: color picker, quick colors, corner style, position, greeting, logo URL
- [x] Branding removal toggle (gated to Starter+ plan)
- [x] Enhanced Billing page with plan comparison grid, upgrade/downgrade buttons
- [x] AI Engine settings page (Claude vs Ollama) with config fields
- [x] AI config endpoints (GET/PUT /api/ai/config)
- [x] Billing management endpoints (GET /api/billing/plans, POST /api/billing/change-plan)
- [x] ChatbotEdit now has 4 tabs: Edit, Widget Design, Embed Code, Preview
- [x] Public chatbot endpoint returns owner_plan and can_hide_branding

## Prioritized Backlog

### P1 (High)
- [ ] Invoice PDF generation (German tax compliant with §257 HGB)
- [ ] Data retention jobs (auto-delete messages after 90 days)
- [ ] Integrate Ollama into chat endpoint (use engine from ai_config, fall back to Claude)

### P2 (Medium)
- [ ] CSV export for analytics
- [ ] Docker Compose deployment setup for self-hosting
- [ ] Domain whitelist per chatbot (CORS)
- [ ] Chatbot-Analyse Enhancement (template usage statistics)

### P3 (Nice to have)
- [ ] 2FA support
- [ ] Redis caching for FAQ responses
- [ ] robots.txt and sitemap.xml
- [ ] Backup scripts
- [ ] More chatbot templates (Hotel, Autowerkstatt, Steuerberater)

## Next Tasks
1. Invoice PDF generation with German VAT
2. Data retention jobs (auto-delete messages after 90 days)
3. Integrate Ollama into the chat endpoint based on ai_config
4. CSV export for analytics
5. More chatbot templates
