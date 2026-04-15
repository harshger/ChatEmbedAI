# ChatEmbed AI — Product Requirements Document

## Original Problem Statement
Build a complete SaaS web app called "ChatEmbed AI" — an AI-powered chatbot builder for small businesses in Europe, fully optimized for the German market and 100% GDPR compliant. Business owners paste FAQ, and an embeddable chatbot is created.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI (Python) + MongoDB
- **AI**: Claude Sonnet via Emergent LLM Key (fallback; local AI planned as primary)
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
- [x] Chatbot Templates (6 German business types): Bäckerei, Zahnarzt, Restaurant, Friseur, Immobilien, Anwalt
- [x] Standalone embed.js widget served from /api/embed.js (self-contained, no framework deps)
- [x] Improved Stripe webhooks with subscription lifecycle handling
- [x] Team management page (Agency plan gated) with invite/remove
- [x] Template banner on chatbot creation page linking to templates
- [x] CORS fix for cross-origin auth (removed credentials:include, using Bearer tokens)

### Phase 3 — Auth Flows & Analytics (April 15, 2026)
- [x] Email verification flow (double opt-in) with mocked emails + demo token display
- [x] Password reset flow (forgot password → token → reset) with mocked emails
- [x] Enhanced Analytics with recharts: messages/day bar chart, language distribution pie chart, peak hours bar chart, top 10 questions table, per-chatbot stats
- [x] Forgot Password page (/forgot-password)
- [x] Reset Password page (/reset-password?token=xxx)
- [x] Verify Email page (/verify-email?token=xxx)
- [x] Signup page shows verification notice with mock verify link
- [x] Login page has "Forgot Password?" link
- [x] /api/auth/me and /api/auth/login return email_verified field

## Prioritized Backlog

### P0 (Critical)
- All P0 items completed!

### P1 (High)
- [ ] Local AI (Ollama) integration as primary AI engine
- [ ] Invoice PDF generation (German tax compliant with §257 HGB)
- [ ] Data retention jobs (auto-delete messages after 90 days)
- [ ] Widget customization (colors, logo, branding removal for paid)
- [ ] Stripe Checkout & Billing Portal wire-up (ensure UI triggers checkout correctly)

### P2 (Medium)
- [ ] CSV export for analytics
- [ ] Docker Compose deployment setup for self-hosting
- [ ] Nginx configuration
- [ ] Domain whitelist per chatbot (CORS)
- [ ] Chatbot-Analyse Enhancement (template usage statistics)

### P3 (Nice to have)
- [ ] 2FA support
- [ ] Redis caching for FAQ responses
- [ ] robots.txt and sitemap.xml
- [ ] Backup scripts
- [ ] More chatbot templates (Hotel, Autowerkstatt, Steuerberater)

## Next Tasks
1. Widget customization (colors, logo, branding removal for paid)
2. Stripe Checkout & Billing Portal proper wire-up
3. Build Ollama/local AI integration as primary engine
4. Invoice PDF generation with German VAT
5. Data retention jobs
