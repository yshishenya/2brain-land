# 2BRAIN SEO plan

## Scope

The current target is the Russian-language company landing page at `https://2brain.pro/`. The first phase is deliberately non-visual: preserve the visual composition, typography, spacing, colors, and interaction design while improving discoverability, metadata, structured data, crawlability, and delivery behavior.

Baseline audit: 20 August 2026, overall score 60/100.

## Guardrails

- Do not change the visual layout, copy hierarchy, typography, colors, spacing, or animation behavior without a separate approval.
- Do not change visible page text, browser title, or metadata copy without a separate approval.
- Do not add new public pages until their purpose, URL, canonical, metadata, and navigation relationship are defined.
- Do not claim live search, traffic, backlink, or field-performance data until Google Search Console, GA4, Yandex Webmaster, or another source is connected.
- Preserve the current deployment rollback path.
- Validate every release with the local site health check and a production smoke check.

## Phase 0 — technical foundation

1. Add a self-referencing canonical for `https://2brain.pro/`.
2. Publish `robots.txt` with the sitemap location.
3. Publish `sitemap.xml` for the current canonical URL.
4. Add Open Graph and Twitter Card metadata for Telegram and social sharing.
5. Add `WebPage`, `WebSite`, `Organization`, and `Person` JSON-LD without changing the visible page.
6. Add explicit `width`, `height`, `decoding`, and appropriate lazy loading to images.
7. Add crawlable HTML links to product domains; keep the current dialogs and visual interaction.

## Phase 1 — evidence and information architecture

1. Improve title and meta description using Russian search-demand evidence only after separate copy approval.
2. Strengthen founder, team, case, award, and result evidence without inventing claims.
3. Decide whether the site remains a single landing page or gains crawlable service/case pages.
4. If new pages are approved, create service and case URLs with independent metadata and schema.
5. Add `scroll-margin-top` for fixed-header anchor targets if testing confirms overlap.

## Phase 2 — measurement and growth

1. Connect Google Search Console and Yandex Webmaster.
2. Connect GA4 and/or Yandex Metrica with consent-aware conversion events.
3. Establish baseline measurements for impressions, clicks, CTR, indexed URLs, leads, and Core Web Vitals.
4. Build content around validated Russian commercial intent: AI implementation, AI transformation, AI product development, corporate AI infrastructure, and business-process automation.
5. Establish a backlink and authority plan through case studies, expert publications, awards, and industry events.

## Acceptance criteria for Phase 0

- `/robots.txt` returns HTTP 200 and references `/sitemap.xml`.
- `/sitemap.xml` returns valid XML and contains the canonical homepage.
- The homepage contains exactly one canonical URL matching `https://2brain.pro/`.
- Open Graph metadata points to an absolute, working image URL.
- JSON-LD parses without errors and uses only verifiable organization/person facts.
- Product URLs are present as real HTML links, not only injected by JavaScript.
- Existing screenshots remain visually equivalent at desktop and mobile viewports.
- CLS does not regress and improves from the current ~0.13 measurement.
- Docker health check passes locally and after deployment.
