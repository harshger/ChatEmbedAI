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
| Free | 0 EUR | 1 | 500 | - |
| Starter | 29 EUR/mo | 3 | 2,000 | - |
| Pro | 79 EUR/mo | 10 | 10,000 | - |
| **Growth** | **99 EUR/mo** | 10 | 10,000 | **34 skills, 50 runs/mo** |
| Agency | 199 EUR/mo | Unlimited | Unlimited | Unlimited |

Growth plan: 7-day free trial + 14-day EU money-back guarantee (Widerrufsrecht)

## What's Been Implemented

### Phases 1-9 (Previously completed)
- Full MVP with auth, chatbot CRUD, embed.js, templates, team management
- Billing with Stripe, legal pages, GDPR compliance
- Domain verification, conversation history, analytics, CSV exports
- Invoice PDF generation, data retention background jobs
- Customer satisfaction rating, Ollama integration, unanswered question logging
- Full DE/EN i18n translation pass

### Phase 10 — Marketing Assistent Module (Apr 15, 2026)
- [x] 10 initial marketing skills with German market context
- [x] Growth plan with 7-day trial and 14-day money-back guarantee
- [x] MarketingAssistant.js with 3-view pattern (grid, input, result)

### Phase 11 — 34-Skill Expansion + Website Scanner (Apr 15, 2026)
- [x] **34 Marketing Skills**: Expanded from 10 to 34 skills across 7 categories
- [x] **7 Categories**: Texte & Inhalte (5), Website & Conversion (6), E-Mail & Outreach (3), SEO & Sichtbarkeit (6), Werbung & Growth (5), Strategie & Planung (5), Vertrieb & Kunden (4)
- [x] **24 New SKILL.md Files**: copy-editing, content-strategy, ad-creative, signup-flow-cro, onboarding-cro, form-cro, popup-cro, paywall-upgrade-cro, lead-magnets, ai-seo, programmatic-seo, site-architecture, schema-markup, analytics-tracking, paid-ads, ab-test-setup, free-tool-strategy, marketing-ideas, competitor-alternatives, marketing-psychology, product-marketing-context, sales-enablement, revops, customer-research
- [x] **Category Tabs**: Horizontal scrollable tabs with "Alle" default + 7 category filters
- [x] **Radically Simple UI**: One-click skill cards, pre-filled placeholders, single "Erstellen" button
- [x] **Marketing Profiles**: One-time 4-field setup (product, target customer, USP, competitors) auto-loaded as AI context
- [x] **GDPR Website Scanner**: Consent-based scraper (httpx + BeautifulSoup4), smart skill selector, 2 free AI analyses
- [x] **Welcome Page**: Post-signup experience with 3 states (scanning, results, no-scan)
- [x] **Signup Update**: Optional website URL with GDPR scan consent checkbox
- [x] **Background Scan**: FastAPI BackgroundTasks triggers analysis on registration
- [x] **Locked Skills Preview**: 32 locked skill teasers with personalized copy from scraped data
- [x] **Upgrade CTA**: Drives users to Growth plan after showing free insights
- [x] **i18n**: All new strings in both DE and EN

## Code Architecture
```
/app/
  backend/
    server.py
    config.py (PLAN_LIMITS, PLAN_PRICES, MARKETING_USAGE_LIMITS)
    routes/
      marketing.py (34 skills, profile CRUD, website scan, 7 categories)
      auth.py (register with scan_consent + BackgroundTasks)
      billing.py (5 plans including Growth)
      ... (15 route files total)
    marketingskills/
      skills/ (35 directories: german-market-context + 34 skills)
    tests/
  frontend/
    src/
      pages/MarketingAssistant.js (rebuilt: 3-view, 7 categories, profile setup)
      pages/Welcome.js (NEW: post-signup scan experience)
      pages/Signup.js (updated: optional website, scan consent)
      pages/Pricing.js (updated: 5 plans, 34 skills in Growth)
      pages/Landing.js (updated: marketing section)
      components/DashboardLayout.js (sidebar with marketing nav)
      lib/api.js (new endpoints: profile, scan, dismiss)
      lib/i18n.js (updated: 34 skills translations DE/EN)
  memory/
```

## Key DB Collections
- `users`: {user_id, email, plan, website_url, scan_banner_dismissed...}
- `chatbots`: {user_id, business_name, faq_content...}
- `marketing_profiles`: {user_id, product_description, target_customer, usp, competitors}
- `marketing_usage`: {user_id, skill_name, created_at}
- `marketing_results`: {user_id, skill_name, prompt, result, created_at}
- `marketing_trials`: {user_id, trial_start, trial_end}
- `website_scans`: {user_id, url, scraped_data, skill1, analysis1, skill2, analysis2, teasers, status}
- `consent_logs`: {user_id, consent_type, url, granted, created_at}

## Prioritized Backlog

### P1 (High)
- [ ] 14-day EU cooling-off automated refund via Stripe webhook
- [ ] Dashboard reminder banner for users with scan results (dismissible)
- [ ] Rescan in settings page (website URL edit + re-analyze)

### P2 (Medium)
- [ ] Docker Compose deployment setup
- [ ] Domain whitelist per chatbot (CORS)
- [ ] Custom widget logo upload
- [ ] REST API access for Pro/Agentur plans
- [ ] Marketing results PDF export
- [ ] OpenAPI/Swagger documentation
- [ ] Marketing Score Dashboard (gamification)

### P3 (Nice to have)
- [ ] 2FA support, Redis caching, robots.txt/sitemap
- [ ] More templates (Hotel, Autowerkstatt, Steuerberater)
- [ ] Sub-account management (Agency)

## Mocked Services
- Email sending (logged to console)
- Stripe (test key, no real charges)
