# ChatEmbed AI — Product Requirements Document

## Original Problem Statement
Build a complete SaaS web app called "ChatEmbed AI" — an AI-powered chatbot builder for small businesses in Europe, fully optimized for the German market and 100% GDPR compliant. Business owners paste FAQ and an embeddable chatbot is created. Domain verification required to prevent misuse.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI (Python) + MongoDB
- **AI**: Claude Sonnet via Emergent LLM Key (chatbot + marketing skills)
- **Payments**: Stripe (test key, subscription model)
- **Auth**: JWT + Google OAuth via Emergent Auth
- **Email**: Mocked (console logging)
- **Design**: Swiss & High-Contrast (Klein Blue #002FA7, IBM Plex Sans + Clash Display)

## Plans
| Plan | Price | Chatbots | Messages | Marketing |
|------|-------|----------|----------|-----------|
| Free | €0 | 1 | 500 | - |
| Starter | €29/mo | 3 | 2,000 | - |
| Pro | €79/mo | 10 | 10,000 | - |
| **Growth** | **€99/mo** | 10 | 10,000 | **10 skills, 50 runs/mo** |
| Agency | €199/mo | Unlimited | Unlimited | Unlimited |

Growth plan: 7-day free trial + 14-day EU money-back guarantee (Widerrufsrecht)

## What's Been Implemented

### Phases 1–9 (Previously completed)
- Full MVP with auth, chatbot CRUD, embed.js, templates, team management
- Billing with Stripe, legal pages, GDPR compliance
- Domain verification, conversation history, analytics, CSV exports
- Invoice PDF generation, data retention background jobs
- Customer satisfaction rating, Ollama integration, unanswered question logging
- Full DE/EN i18n translation pass

### Phase 10 — Marketing Assistent Module (Apr 15, 2026)
- [x] **11 Marketing Skill Files**: german-market-context + 10 specialized skills (copywriting, cold-email, page-cro, pricing-strategy, email-sequence, seo-audit, social-content, launch-strategy, churn-prevention, referral-program)
- [x] **German Market Context**: Loaded before every skill with formal Sie-form, DSGVO rules, Mittelstand B2B psychology, pricing in EUR zzgl. MwSt.
- [x] **Marketing Backend Routes**: GET /api/marketing/skills, /usage, POST /run, /save, /start-trial, GET /history
- [x] **Plan Gating**: Growth/Agency plan or active 7-day trial required for /run
- [x] **7-Day Free Trial**: POST /api/marketing/start-trial, one-time only per user
- [x] **14-Day Money-Back Guarantee**: EU Consumer Rights Directive (Fernabsatzgesetz/Widerrufsrecht) text displayed
- [x] **Growth Plan €99/mo**: Added to config, billing, pricing page (5 tiers now)
- [x] **MarketingAssistant.js**: 3-view component (skill grid → input form → markdown results with copy/save/new)
- [x] **Sidebar**: "Marketing Assistent" with green "NEU" badge
- [x] **Upgrade Prompt**: For non-Growth users with trial CTA and EU guarantee text
- [x] **Landing Page Section**: "Mehr als ein Chatbot — Ihr KI-Marketing-Assistent" with 6 feature cards and Growth CTA
- [x] **Usage Tracking**: 50 runs/month for Growth, 999 for Agency, progress bar

## Code Architecture
```
/app/
├── backend/
│   ├── server.py
│   ├── config.py (PLAN_LIMITS, PLAN_PRICES, MARKETING_USAGE_LIMITS)
│   ├── routes/
│   │   ├── marketing.py (NEW: skills, usage, run, save, trial, history)
│   │   ├── billing.py (Updated: 5 plans including Growth)
│   │   └── ... (13 route files total)
│   ├── marketingskills/
│   │   └── skills/ (11 directories with SKILL.md files)
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── pages/MarketingAssistant.js (NEW)
│   │   ├── pages/Pricing.js (Updated: 5 plans)
│   │   ├── pages/Landing.js (Updated: marketing section)
│   │   ├── components/DashboardLayout.js (Updated: marketing nav)
│   │   └── lib/i18n.js (Updated: marketing translations DE/EN)
└── memory/
```

## Prioritized Backlog

### Completed
- [x] All Phase 1-10 features

### P2 (Medium)
- [ ] Docker Compose deployment setup
- [ ] Domain whitelist per chatbot (CORS)
- [ ] Custom widget logo upload
- [ ] REST API access for Pro/Agentur plans
- [ ] Marketing results PDF export

### P3 (Nice to have)
- [ ] 2FA support, Redis caching, robots.txt/sitemap
- [ ] More templates (Hotel, Autowerkstatt, Steuerberater)
- [ ] Sub-account management (Agency)
- [ ] OpenAPI/Swagger documentation

## Mocked Services
- Email sending (logged to console)
- Stripe (test key, no real charges)
