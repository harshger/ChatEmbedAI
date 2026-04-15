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

## What's Been Implemented (April 15, 2026)
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

## Prioritized Backlog

### P0 (Critical)
- [ ] Embeddable widget (embed.js standalone script)
- [ ] Email verification flow (double opt-in)
- [ ] Stripe webhook handling for subscription lifecycle

### P1 (High)
- [ ] Local AI (Ollama) integration as primary AI engine
- [ ] Team management (Agency plan sub-accounts)
- [ ] Invoice PDF generation (German tax compliant)
- [ ] Password reset flow
- [ ] Data retention jobs (auto-delete messages after 90 days)

### P2 (Medium)
- [ ] Advanced analytics (word cloud, peak hours, language pie chart)
- [ ] CSV export for analytics
- [ ] Widget customization (colors, logo, branding removal)
- [ ] Docker Compose deployment setup
- [ ] Nginx configuration for self-hosting

### P3 (Nice to have)
- [ ] 2FA support
- [ ] Redis caching for FAQ responses
- [ ] Domain whitelist per chatbot (CORS)
- [ ] robots.txt and sitemap.xml
- [ ] Backup scripts

## Next Tasks
1. Build the standalone embed.js widget script
2. Implement Stripe webhook for subscription updates
3. Add Ollama/local AI as primary engine with Claude fallback
4. Invoice PDF generation
5. Team management for Agency plan
