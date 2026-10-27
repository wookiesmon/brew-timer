# 02 · Business Model & Revenue

**Team:** Business Model & Revenue · **Product:** Ebb, a 12-week stress/cortisol and belly-fat program (free, private, offline PWA) · **Date:** 2026-10-27

> **Summary.** Keep the whole 12-week program free and on-device. Charge for things that cost money to run or that add real value: insights, the "after week 12" maintenance phase, encrypted backup, and an optional AI coach. Take payments on the web first (Stripe/Paddle globally, Toss in Korea) so most revenue avoids the 15–30% app-store fee. Earn affiliate income only on things the plan already prescribes (baseline and week-12 labs), always disclosed. Never sell an own-brand supplement. In the base case the business reaches about **$16k a month in revenue (~$190k ARR run-rate) by month 24**. In the conservative case it stays a side project (~$1.5k/month). In the optimistic case, where one channel catches fire, it reaches about $80k/month.

---

## 0. Starting point: what Ebb is and what that implies for money

| Fact about the product today | What it means for monetization |
|---|---|
| Single HTML file, data only in `localStorage`, works offline, no account | **Privacy is the brand.** Any paid feature that needs a server (AI, sync) must be opt-in and send as little data as possible. There's no login, so entitlement needs a license key or magic link. |
| Hosted on GitHub Pages as a PWA, not in the app stores | **No store fee today.** Web checkout keeps ~94–96% of each dollar. Store distribution can come later and is optional. |
| The full 12-week plan, Calm Score, logging, breathing pacer, charts and supplement tiers are already built and free | Taking any of these away would destroy trust. The paywall goes on **new** depth: insights, maintenance, coaching, backup. |
| The plan prescribes baseline and week-12 labs | This is a **natural, non-pushy affiliate moment** (at-home lab kits), because users are already told to get these labs. |
| The plan includes supplement guidance with evidence tiers and a medication safety screen | Supplement money is the biggest **trust conflict**. The section on supplements says to "skip" many products the industry pays well for. Commissions must never change a tier. |
| The founder is solo and builds with AI tools, likely in Korea or the US | Favor streams that are self-serve and low-ops. Human coaching and B2B are later options, not day-one work. Korea and the US both matter, so plan dual pricing (USD/KRW) and dual payments (Stripe/Paddle + Toss). |
| Competitors charge $30–$360 a year (Calm/Headspace ~$70/yr, Welltory ~$80–120/yr, WHOOP $199–359/yr, Zero Plus ~$70/yr) | There's room for a **$30/yr Plus** and a **~$90/yr Pro** that sit well under hardware subscriptions. |

---

## 1. Every realistic revenue stream, scored

Each stream gets a score from 1 to 5. **Revenue potential:** 5 is high. **Effort:** 5 is a lot of work. **Trust risk** and **regulatory risk:** 5 is high risk. The verdict is one of: **Build now**, **Build later**, **Partner/test**, or **Avoid**.

| # | Stream | Revenue potential | Effort | Trust risk | Reg. risk | Verdict |
|---|---|:-:|:-:|:-:|:-:|---|
| 1 | Freemium subscription (Plus) | 4 | 2 | 2 | 1 | **Build now** |
| 2 | One-time "12-week Program Pass" | 3 | 1 | 1 | 1 | **Build now** (as a Plus option) |
| 3 | AI coach (Pro) | 4 | 3 | 3 | 3 | **Build now**, opt-in, wellness scope only |
| 4 | Human coaching tier | 3 | 4 | 2 | 3 | Build later (month 9+), via contracted coaches |
| 5 | At-home lab test affiliate | 2 | 1 | 2 | 2 | **Build now**, disclosed |
| 6a | Supplement affiliate (neutral retailers) | 2 | 1 | 4 | 3 | Partner/test with strict guardrails (§5) |
| 6b | Own-brand supplements | 4 | 5 | **5** | 4 | **Avoid** |
| 7 | Wearable integrations | 1 direct, 3 indirect | 3 | 1 | 2 | Build later as a Plus feature, not a revenue line |
| 8 | B2B corporate wellness / insurers | 4 | 4 | 2 | 3 | Partner/test from month 12 |
| 9 | Clinic / doctor white-label | 3 | 4 | 2 | 4 | Build later, flat SaaS fee only |
| 10 | Paid cohort challenges | 2 | 2 | 1 | 1 | Test at month 6 (bundled into Pro) |
| 11 | Courses and ebooks | 2 | 2 | 1 | 1 | Test cheaply (Korean ebook on Naver/Kmong) |
| 12 | Creator partnerships | 3 (as a channel) | 2 | 2 | 2 | **Build now** as the main acquisition channel |
| 13 | Korean market specifics | multiplier | 2 | 1 | 3 | **Build now**: Toss payments, Kakao, Naver |
| 14 | Ads (display/network) | 1 | 1 | 4 | 2 | **Avoid**: it contradicts "calm" and "private" |
| 15 | Selling or sharing data | — | — | 5 | 5 | **Never** |

### 1.1 Freemium subscription ("Ebb Plus")
- **What's paid.** Features that add depth or cost money to run. Nothing in the current free app moves behind the paywall:
  - **Insights engine.** Correlation cards computed on-device, for example "On nights you slept 7 h+, next-day stress averaged 1.6 lower". Research doc 04 shows this is the motivational feature that WHOOP, Welltory and Zero all charge for.
  - **Beyond week 12.** A maintenance phase for weeks 13–52, a "second round" plan, and specialized tracks: shift worker, perimenopause, desk-bound, Korean diet templates (한식 meal templates).
  - **Lab tracker and doctor-ready PDF.** Baseline vs. week-12 labs, trend view, and a one-page summary to hand to a physician.
  - **Encrypted backup and multi-device sync.** End-to-end encrypted with a user-held key, so the privacy promise survives.
  - **Wearable import.** Apple Health export, Health Connect, and Oura/WHOOP CSV or API.
  - **Guided audio downshifts** and sleep wind-downs. **Smart reminders:** web push, or Kakao 알림톡 in Korea.
- **Why it works.** It's low effort (mostly client-side code). Freemium health apps typically convert 2–5% of active users. Trust risk stays low as long as the free core stays complete.

### 1.2 One-time "12-week Program Pass"
- Pay once and get Plus for 12 weeks, **with no auto-renew**. This fits the product's natural arc and the "calm, no traps" brand. Korean users also tend to prefer one-time 결제 over subscriptions.
- Price it at parity with three months of monthly billing ($14.99 / ₩16,900). It's the "honest" option and works as a strong conversion anchor.
- Offer a "renew for maintenance" prompt at week 12. This is where annual plans get sold.

### 1.3 AI coach ("Ebb Pro")
- **What it does.**
  - A weekly review that reads the week's logs (habits, check-ins, waist, weight, HRV, sleep, PSS-10) and gives three specific suggestions.
  - Chat about the plan.
  - Plan adaptation suggestions, such as "HRV is down 3 days, so swap Thursday intervals for Zone 2".
  - A plain-language lab explainer that ends with "questions to ask your doctor".
- **Privacy design.**
  - Opt-in, with a server proxy (Cloudflare Worker).
  - Send a **compact summary** of the logs, not raw history.
  - Use a zero-data-retention API setting. Store nothing server-side by default.
  - Make the privacy page explicit about what leaves the device.
- **Scope guardrails.** Wellness coaching only:
  - No diagnosis.
  - No dosing beyond what's in the plan.
  - Hard-coded escalation to "see a doctor" for the plan's red flags (Cushing's signs, new hypertension, persistent low mood, possible sleep apnea).
  - Crisis-language detection that routes to local hotlines (988 in the US, 109 in Korea).
  - It must not be framed as "therapy". Some US states, such as Illinois from 2025, restrict AI-delivered therapy.
- **API cost estimate per Pro user per month.** Haiku-class pricing is about $1 per million input tokens and $5 per million output tokens, with cached input about 90% cheaper. A Sonnet-class model handles the weekly review at about $3 / $15 per million tokens.

| Component | Assumption | Cost |
|---|---|---|
| Chat message (Haiku-class) | ~3k cached system/plan tokens + ~4k fresh tokens (log summary + history) + ~400 output tokens ≈ $0.0003 + $0.004 + $0.002 | **≈ $0.0065 per message** |
| Typical user: 40 messages a month | 40 × $0.0065 | $0.26 |
| Weekly review (Sonnet-class) | 8k input + 1k output ≈ $0.039 per review × 4.3 a month | $0.17 |
| Safety classifier, retries, overhead | +20% | $0.09 |
| **Median Pro user** | | **≈ $0.50 a month** |
| Heavy user: 150-message fair-use cap | 150 × $0.0065 + $0.17 + 20% | **≈ $1.40 a month** |
| Planning figure used in the model | Blended, with headroom | **$0.60 a month** (+$0.05 infrastructure) |

AI cost is 5–10% of Pro revenue. It is **not** the margin problem. App-store fees are.

### 1.4 Human coaching tier
- **Offer.** $149/mo or ₩199,000/mo (12-week package $399 / ₩549,000). It covers a certified health coach (NBHWC in the US, 건강운동관리사 or a nutritionist in Korea), two video calls a month, and async chat. The coach sees the user's logs only with consent (share link or export).
- **Economics.** Pay coaches about 55% of revenue. The founder keeps about 45% (~$67 per client per month).
- **Scaling and timing.** It doesn't scale for a solo founder, so cap it and treat it as a premium proof point and a source of testimonials. Start around month 9, once there's demand evidence from Pro.

### 1.5 At-home lab test partnerships (affiliate)
- **What it is.**
  - The plan already says "baseline + week 12 labs".
  - In the US: affiliate links to at-home or walk-in lab panels (Everlywell, LetsGetChecked, Quest/Labcorp direct-to-consumer). Third-party sources put Everlywell's affiliate commissions at roughly 5–12% of orders that average over $150.
  - In Korea: partner with 검진센터 booking platforms on a **flat listing or SaaS fee**, not per-patient fees (see the Korean legal note in §1.13).
- **Placement.** Show it only at the day-1 and week-12 checkpoints, next to the "ask your doctor or use your insurance labs" option, which is listed first.
- **Value.** About $10–15 per kit. Modest money, high fit, and low ops.

### 1.6 Supplements: affiliate vs. own brand
- **Own-brand: avoid.**
  - It creates a direct conflict with the evidence tiers.
  - It brings inventory, cash-flow, FDA (DSHEA, structure/function claims) and Korean 식약처 건강기능식품 rules, plus liability.
  - It invites the "you're telling me cortisol is the problem so you can sell me cortisol pills" critique that sinks credibility in this niche.
  - The plan's "Skip" list (cortisol blockers, adrenal glandulars) shows Ebb's value is precisely **not** being a supplement funnel.
- **Affiliate: allowed only under the §5 guardrails.**
  - Use neutral retailers: iHerb (officially "up to" ~5–25% depending on region and program), Amazon, and Coupang Partners in Korea (low single-digit %).
  - Link only to third-party-tested products (USP, NSF, Informed Choice/Sport) in Tier 1 and Tier 2.
  - Revenue is small and is **excluded from the projections** (it's upside). Trust risk is the highest of any live option.

### 1.7 Wearable integrations
- Not a revenue line by itself. It's a Plus feature that raises retention and conversion: HRV and resting HR are the plan's physiological outcome metrics.
- Start with **file import**: Apple Health XML export, Health Connect, Oura/WHOOP CSV. That's zero backend.
- Native HealthKit needs a native wrapper (Capacitor) and therefore app-store distribution. The Oura and WHOOP APIs need OAuth and a server.
- Possible later upside: co-marketing or referral deals with Oura or WHOOP (their referral programs offer credits rather than meaningful cash).

### 1.8 B2B corporate wellness / insurers
- **US.** Sell through wellness platforms and EAP marketplaces at $2–4 per employee per month (PEPM), or $15–30 per enrolled employee per 12-week cohort. Burnout and stress are top HR priorities, and "measurable waist + stress change in 12 weeks" makes a good pitch.
- **Korea.** Use corporate welfare malls (기업 복지몰, e.g. 이지웰, 베네피아) for B2B2C distribution. Insurers' 건강증진형 보험 programs give health-management benefits within regulatory value limits.
- **What it requires.** An admin dashboard with aggregate, anonymized data only (minimum group size of 10, no individual data to the employer), SSO-free access codes, invoices, and possibly a security questionnaire. It's a long sales cycle (3–9 months), so **start with 1–2 paid pilots in month 12+**.

### 1.9 Clinic and doctor white-label
- **Offer.** Functional-medicine clinics, obesity clinics, 한의원 and 가정의학과 clinics can give Ebb, under their own logo, to patients between visits. The patient exports a PDF or share link to the clinic.
- **Pricing.** A **flat SaaS fee** ($49–199/month per clinic), never per-referral. In Korea, 의료법 Article 27(3) prohibits inducing or brokering patients for a fee. In the US, anti-kickback and fee-splitting rules apply when federal payers are involved.
- **Regulatory caution.** Once clinicians use it in care, HIPAA (business associate agreement) and Korean 의료기기/디지털의료제품 rules can come into play. Keep it a wellness tool with no diagnostic claims. Build later.

### 1.10 Paid cohort challenges
- **Format.** Quarterly "Ebb 12" cohort starting on fixed dates. A group chat (Kakao 오픈채팅 in Korea, Discord or WhatsApp in the US), weekly live Q&A, and an anonymous leaderboard of habit consistency, **never weight**.
- **Price.** Standalone $29 / ₩35,000, or included in Pro.
- **Why.** Cohorts lift completion and word of mouth, and create fresh launch moments four times a year.

### 1.11 Courses and ebooks
- A "12-Week Calm Core" ebook or video course: $19–39 (Gumroad/Lemon Squeezy), and in Korea ₩19,000–29,000 on Naver SmartStore, Kmong or Class101.
- **Effort.** Low, because research docs 01–03 are already 80% of the content.
- **Role.** Mainly a top-of-funnel product and an SEO asset, not a core line.

### 1.12 Creator partnerships
- **Who.** Micro-creators (10k–100k followers) in stress, menopause, desk fitness, and Korean 다이어트/갓생 content.
- **Deal.** 30% revenue share on first-year subscription revenue via referral codes, plus free Pro.
- **Rules.** Disclosure is mandatory: the FTC Endorsement Guides in the US, and the 공정위 추천·보증 심사지침 in Korea ("유료 광고 포함").
- This is the **best paid-acquisition channel** for a solo founder because cost is only incurred on conversion.

### 1.13 Korean market specifics
| Item | Recommendation |
|---|---|
| Payments | **Toss Payments** for card and easy-pay (official list rate 3.4%, bank transfer 2.0%; ₩220k setup fee and ₩110k annual fee per the published schedule, negotiable). Recurring billing uses Toss's 빌링 (auto-billing) product. Add **KakaoPay** and **Naver Pay** as easy-pay methods (via Toss or directly). You need 사업자등록 and 통신판매업 신고 first. |
| App stores (later) | Korean law lets apps use alternative in-app payment systems. Apple's commission on those sales is 26% (with Toss, KCP, Inicis and NICE among the approved PGs), so the saving over 30% is small once PG fees are added. For a PWA, web checkout remains far cheaper. |
| VAT | Korean consumer prices **include 10% VAT**, so ₩34,900 nets ₩31,727 before PG fees. |
| Distribution | Naver Blog and Naver Cafe SEO (e.g. "코르티솔 낮추는 법", "뱃살 스트레스"); Kakao Channel for reminders and 알림톡 (paid per message); Instagram Reels and YouTube Shorts. |
| Privacy law | Health data is 민감정보 under 개인정보보호법, so any server-side storage (AI, sync) needs **separate explicit consent**. On-device-only stays the default. |
| Health-claim rules | Advertising 건강기능식품 is subject to self-regulatory pre-review (한국건강기능식품협회). Affiliate posts must carry disclosure. Don't describe the Calm Score as diagnosing or measuring cortisol (the 의료기기 boundary). |
| Pricing psychology | Monthly prices under ₩10,000 and one-time passes convert well. Annual plans need a clear discount (about 50%). |

---

## 2. Recommended model

**A "free program, paid depth" freemium model, sold on the web.** The free tier is the complete 12-week program. Plus sells continuity and insight. Pro sells personalization through AI. Human coaching, cohorts, and B2B are layered on later. Affiliate revenue is limited to disclosed, plan-prescribed items.

### 2.1 Tier table

| | **Free** | **Plus** | **Pro** |
|---|---|---|---|
| **USD monthly** | $0 | $4.99 | $12.99 |
| **USD annual** | $0 | $29.99 (≈$2.50/mo, −50%) | $89.99 (≈$7.50/mo, −42%) |
| **USD one-time** | — | **12-week Program Pass $14.99** (no auto-renew) | — |
| **KRW monthly** (VAT included) | ₩0 | ₩5,900 | ₩15,900 |
| **KRW annual** | ₩0 | ₩34,900 | ₩109,000 |
| **KRW one-time** | — | 12주 프로그램 패스 ₩16,900 | — |
| Full 12-week phased plan, daily checklist, Calm Score | ✓ | ✓ | ✓ |
| Daily and weekly check-ins; waist, weight and HRV logging; PSS-10 | ✓ | ✓ | ✓ |
| Breathing pacer (all presets), progress charts | ✓ | ✓ | ✓ |
| Tiered supplement guidance + medication safety screen | ✓ (**never paywalled**) | ✓ | ✓ |
| "See a doctor" red flags, export/import, offline, no account | ✓ (**never paywalled**) | ✓ | ✓ |
| Insights engine (on-device correlations, "what moves your score") | — | ✓ | ✓ |
| Maintenance phase (weeks 13–52) + specialty tracks (shift work, perimenopause, desk, 한식 templates) | — | ✓ | ✓ |
| Lab tracker + doctor-ready PDF summary | — | ✓ | ✓ |
| Encrypted backup and multi-device sync (opt-in, end-to-end encrypted) | — | ✓ | ✓ |
| Wearable import (Apple Health, Health Connect, Oura/WHOOP files) | — | ✓ | ✓ |
| Guided audio downshifts and sleep wind-downs; smart reminders (web push / Kakao) | — | ✓ | ✓ |
| **AI coach:** weekly review, chat (150 messages/month fair use), plan adaptation, plain-language lab explainer | — | — | ✓ |
| Quarterly live cohort challenge + group Q&A | — | — | ✓ |
| Early access to new tracks | — | — | ✓ |
| **Add-on:** human coach, $149/mo or $399 per 12 weeks (₩199,000 / ₩549,000) | — | available | available (−10%) |

**Trial and refunds.**
- Pro gets a **14-day free trial**. RevenueCat's 2025 data shows longer trials of 17–32 days convert best (~46% median), so test a 21-day trial as well.
- Plus doesn't need a trial because the free tier is the trial.
- Offer a no-questions 14-day refund on everything.

**Entitlements without accounts.** Checkout emails a magic link or license key. The app stores a signed entitlement token in `localStorage` and re-validates it occasionally. Only Plus sync and Pro AI need the server.

---

## 3. Unit economics

### 3.1 Payment fees and gross margin by channel

| Product (gross price) | Web: Stripe (~2.9% + $0.30) | Web: Paddle/Lemon Squeezy MoR (~5% + $0.50, handles VAT/sales tax) | Korea: Toss (3.4%) | App store 15% (Small Business Program / subscriptions after year 1) | App store 30% |
|---|---|---|---|---|---|
| Plus monthly $4.99 | fee $0.44 (8.9%) → **GM 91%** | fee $0.75 (15%) → GM 85% | ₩5,900: fee ₩201 + VAT ₩536 → **GM 87% of the sticker price** (96% of the ex-VAT price) | fee $0.75 → GM 85% | fee $1.50 → GM 70% |
| Plus annual $29.99 | $1.17 (3.9%) → **GM 96%** | $2.00 (6.7%) → GM 93% | ₩34,900: ₩1,187 fee → GM 87% of sticker (97% ex-VAT) | GM 85% | GM 70% |
| Program Pass $14.99 | $0.73 (4.9%) → GM 95% | $1.25 → GM 92% | ₩16,900 → GM 87% of sticker | GM 85% | GM 70% |
| Pro monthly $12.99 (AI $0.60 + infra $0.05) | $0.68 fee → **GM 90%** | $1.15 → GM 86% | ₩15,900: fee ₩541, AI ≈₩900, VAT ₩1,445 → GM 82% of sticker (90% ex-VAT) | $1.95 → **GM 80%** | $3.90 → **GM 65%** |
| Pro annual $89.99 (AI $7.80 a year) | $2.91 → GM 88% | $5.00 → GM 86% | ₩109,000 → GM 81% of sticker | GM 76% | GM 61% |

US sales tax and EU VAT are owed on top of these in many places. A merchant of record (Paddle or Lemon Squeezy) collects and remits them, which is why its fee is higher. Recommendation: **Stripe for US-only to start, Paddle or Lemon Squeezy once EU/UK sales appear, and Toss for Korea.**

**Takeaways.**
1. **Web-first is worth 10–25 points of margin.**
   - The PWA needs no store at all.
   - If a store build is added later for discovery, enroll in the Small Business Program (15%).
   - In the US, link out to web checkout where the Epic v. Apple anti-steering rulings allow it. The commission status of linked-out purchases was still being litigated after Dec 2025, so verify it before relying on it.
2. **Push annual plans.** On monthly web plans, Stripe's $0.30 fixed fee eats 9% of a $4.99 charge.
3. AI is a 5–10% cost line on Pro. Cap usage with the fair-use limit, not the price.

### 3.2 Blended revenue per paying user

Assumed mix:
- **Plus buyers:** 55% annual, 25% Program Pass, 20% monthly.
- **Pro buyers:** 60% annual, 40% monthly.
- **Geography:** 60% US/global, 40% Korea at about a 0.9 price level.

| | Gross ARPPU (monthly equivalent) | Net after fees, VAT and AI (web-first) | Average paid lifetime | **Net LTV** |
|---|---|---|---|---|
| Plus | $3.48 | ~$3.13 | ~11 months (passes ~3 mo; annual plans 12 mo with ~35% renewal; monthly plans ~7 mo) | **≈ $34** |
| Pro | $9.31 | ~$7.75 | ~9 months | **≈ $70** |
| Blended (82% Plus / 18% Pro) | $4.53 | ~$3.96 | ~10.6 months | **≈ $41** |
| Human coaching client | $149 | ~$67 founder margin | ~4 months | **≈ $270** |

### 3.3 CAC by channel and payback

The funnel assumption: a web visitor activates (finishes onboarding) about 30% of the time, and about 4% of activated users eventually pay. Paid ads also bring a lower-intent mix.

| Channel | Cost basis | **CAC per paying user** | Payback (on ~$3.96 net per month) | LTV:CAC | Use? |
|---|---|---|---|---|---|
| Organic SEO / Naver blog / Reddit / communities | Founder time (AI-assisted content) | $0–5 cash | Immediate | >8× | **Primary** |
| Product-led sharing (share a week-12 "before/after" card, referral gives both people 1 free month) | Cost of free months | $3–8 | 1–2 months | 5–10× | **Primary** |
| Creator partnerships (30% first-year rev share) | Paid only on conversion | $12–20 effective | 3–5 months | 2–3× (no cash risk) | **Primary paid channel** |
| Korea: Naver search ads (CPC ~₩300–1,500) | Visitor ~$0.5–1 | $40–80 | 10–20 months | 0.5–1× | Test small; scale only for Pro |
| US: Meta/TikTok paid social to a web quiz funnel | Visitor ~$0.8–1.5; quiz plus upfront Pro trial raises conversion | $45–110 | 11–28 months | 0.4–0.9× | **Not until** blended LTV is above $90 (i.e. Pro-heavy) |
| App store (Apple Search Ads), later | CPI $2–5 | $60–120 | >15 months | <1× | No |
| B2B pilot (founder-led sales) | ~40–80 h of founder time per deal | $2k–8k per account | 3–9 months per account | 2–5× | From month 12 |

**Rule:** spend cash on acquisition only where 12-month net revenue per payer exceeds CAC. With blended 12-month net of about $45, that rules out broad paid ads until Pro is proven.

### 3.4 Fixed costs (solo founder, months 1–24)
| Item | Monthly |
|---|---|
| Hosting: GitHub Pages ($0) + Cloudflare Workers/KV for entitlements, AI proxy and sync | $5–50 |
| Email (magic links) | $0–20 |
| Domain, legal templates, privacy and terms review (amortized) | ~$50 |
| Korean business registration + Toss annual fee (amortized) | ~₩30,000 |
| AI cost | Variable, already included in the margins above |
| **Total fixed (excluding founder salary)** | **≈ $100–150 a month**. Break-even is about 35 paying users. |

---

## 4. 24-month revenue projection

### 4.1 Assumptions (all cases)
- **Month 1** is the month payments go live. Plus launches in month 3 and Pro in month 6.
- **MAU** (monthly active users) grows geometrically from the starting to the ending value.
- **Paid % of MAU** ramps linearly from month 3 to month 24.
- **Gross ARPPU:** Plus $3.48 and Pro $9.31 per month equivalent (§3.2).
- **"MRR" here is monthly revenue**, including one-time passes and affiliate income spread over the month. ARR run-rate = monthly revenue × 12.
- **Lab affiliate income:** a share of MAU buys a kit each month (0.2%, 0.3% or 0.4% by case) at ~$12 commission, starting month 4.
- **Coaching:** base case adds 2 clients a month from month 9, capped at 25. Optimistic adds 4 a month, capped at 60. Conservative has none. Revenue is shown gross. Coach payout (55%) appears in net contribution only.
- **B2B:** base case runs 1 pilot from month 13 and grows to 6 accounts × 150 seats × $3 PEPM. Optimistic starts in month 10 and reaches 15 accounts × 250 seats × $3. Conservative has none.
- **Store share of revenue** (15% fee): conservative 0% → 20% from month 12; base 0% → 30% from month 9; optimistic 0% → 40% from month 7.
- **Supplement affiliate, ebooks and standalone cohorts: $0** (upside only).
- **Net contribution** = revenue − payment/store fees − VAT/tax − AI cost − coach payout − 10% B2B delivery cost, before founder time and fixed costs.

| Case | MAU at month 1 → 24 | Paid % of MAU (m3 → m24) | Pro share of payers | What has to be true |
|---|---|---|---|---|
| **Conservative** | 400 → 10,000 | 1.5% → 3.0% | 12% | Organic only. Slow SEO. One market. No B2B. |
| **Base** | 1,200 → 40,000 | 2.0% → 4.5% | 18% | SEO in both languages, 10–20 creator partners, a Korean launch with Toss/Kakao, 6 B2B pilots. |
| **Optimistic** | 3,000 → 180,000 | 2.5% → 6.0% | 22% | One viral channel (TikTok/Shorts or Korean media), strong week-12 sharing, and an insurer or welfare-mall deal. |

### 4.2 Conservative case
| Month | MAU | Paid % | Paying users | Pro | Subscription MRR | Other MRR (labs, coaching, B2B) | **Total MRR** | ARR run-rate | Cumulative revenue |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 400 | 0.0% | 0 | 0 | $0 | $0 | $0 | $0 | $0 |
| 3 | 529 | 1.5% | 8 | 0 | $28 | $0 | $28 | $331 | $28 |
| 6 | 805 | 1.7% | 14 | 2 | $58 | $19 | $77 | $924 | $209 |
| 9 | 1,225 | 1.9% | 24 | 3 | $99 | $29 | $128 | $1,537 | $537 |
| 12 | 1,865 | 2.1% | 40 | 5 | $167 | $45 | $212 | $2,540 | $1,079 |
| 15 | 2,838 | 2.4% | 67 | 8 | $279 | $68 | $347 | $4,170 | $1,971 |
| 18 | 4,318 | 2.6% | 111 | 13 | $464 | $104 | $567 | $6,809 | $3,430 |
| 21 | 6,571 | 2.8% | 183 | 22 | $765 | $158 | $922 | $11,067 | $5,805 |
| 24 | 10,000 | 3.0% | 300 | 36 | $1,253 | $240 | **$1,493** | **$17,916** | **$9,653** |

Year 1 revenue: ~$1.1k. Year 2: ~$8.6k. Net contribution at month 24: ~$1.3k a month.

### 4.3 Base case
| Month | MAU | Paid % | Paying users | Pro | Subscription MRR | Other MRR (labs, coaching, B2B) | **Total MRR** | ARR run-rate | Cumulative revenue |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1,200 | 0.0% | 0 | 0 | $0 | $0 | $0 | $0 | $0 |
| 3 | 1,628 | 2.0% | 33 | 0 | $113 | $0 | $113 | $1,358 | $113 |
| 6 | 2,572 | 2.4% | 61 | 11 | $274 | $93 | $367 | $4,404 | $939 |
| 9 | 4,063 | 2.7% | 110 | 20 | $499 | $444 | $943 | $11,322 | $2,862 |
| 12 | 6,420 | 3.1% | 197 | 35 | $892 | $1,423 | $2,316 | $27,787 | $8,380 |
| 15 | 10,143 | 3.4% | 348 | 63 | $1,574 | $3,351 | $4,925 | $59,102 | $20,450 |
| 18 | 16,025 | 3.8% | 607 | 109 | $2,746 | $4,907 | $7,653 | $91,834 | $40,520 |
| 21 | 25,318 | 4.1% | 1,049 | 189 | $4,748 | $6,886 | $11,634 | $139,609 | $71,320 |
| 24 | 40,000 | 4.5% | 1,800 | 324 | $8,148 | $7,865 | **$16,013** | **$192,150** | **$114,529** |

- Year 1 revenue: ~$8.4k. Year 2: ~$106k.
- Other MRR at month 24 is labs ~$1.4k + coaching ~$3.7k + B2B ~$2.7k.
- Net contribution at month 24: ~$12.5k a month.

### 4.4 Optimistic case
| Month | MAU | Paid % | Paying users | Pro | Subscription MRR | Other MRR (labs, coaching, B2B) | **Total MRR** | ARR run-rate | Cumulative revenue |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 3,000 | 0.0% | 0 | 0 | $0 | $0 | $0 | $0 | $0 |
| 3 | 4,283 | 2.5% | 107 | 0 | $372 | $0 | $372 | $4,467 | $372 |
| 6 | 7,306 | 3.0% | 219 | 48 | $1,043 | $351 | $1,394 | $16,727 | $3,382 |
| 9 | 12,463 | 3.5% | 436 | 96 | $2,076 | $1,194 | $3,270 | $39,244 | $10,543 |
| 12 | 21,259 | 4.0% | 850 | 187 | $4,047 | $5,654 | $9,702 | $116,422 | $32,888 |
| 15 | 36,264 | 4.5% | 1,632 | 359 | $7,767 | $10,413 | $18,180 | $218,157 | $78,347 |
| 18 | 61,860 | 5.0% | 3,093 | 680 | $14,721 | $15,679 | $30,401 | $364,808 | $156,229 |
| 21 | 105,521 | 5.5% | 5,804 | 1,277 | $27,623 | $21,813 | $49,436 | $593,235 | $283,505 |
| 24 | 180,000 | 6.0% | 10,800 | 2,376 | $51,404 | $28,830 | **$80,234** | **$962,807** | **$490,388** |

- Year 1 revenue: ~$33k. Year 2: ~$457k.
- Net contribution at month 24: ~$66k a month.
- At this scale, coaching and B2B need hired help.

### 4.5 Summary
| Case | Month-12 MRR | Month-24 MRR | Month-24 ARR run-rate | 24-month cumulative revenue | Paying users at month 24 |
|---|---|---|---|---|---|
| Conservative | $212 | $1.5k | $18k | $9.7k | 300 |
| **Base** | **$2.3k** | **$16.0k** | **$192k** | **$115k** | **1,800** |
| Optimistic | $9.7k | $80.2k | $963k | $490k | 10,800 |

**Sensitivities.**
- MAU is the dominant driver; every case is mostly a distribution bet.
- In the base case, each +1 point of paid conversion at month 24 adds about $1.8k MRR.
- If 60% of subscription revenue went through stores at a 30% fee (instead of 30% at 15%), base-case month-24 net contribution would fall by about $950 (~8%).
- AI cost even at 3× the estimate ($1.80 per Pro user) reduces base-case month-24 net by only about $390.

---

## 5. Ethics guardrails: earning money from supplements without bias

Publish these on a public "How Ebb makes money" page and treat them as product requirements, not marketing copy.

1. **No own-brand supplements, ever.** Also no white-label, no "Ebb blend", and no equity in a supplement company.
2. **Evidence grades are set before commerce and frozen against it.**
   - Tier assignments (1, 2, 3 and Skip) come from the research docs and change only through a written evidence review.
   - Each change is logged in a public changelog with citations.
   - Affiliate status is never an input.
   - Run a quarterly self-audit: list every tier change and confirm that none was linked to a commission change.
3. **Skip-list items never get links.** No links to the "Skip" list (green tea extract, CLA, "cortisol blockers", adrenal glandulars, and the rest). Never accept sponsored placement for any supplement.
4. **Same treatment with or without a commission.**
   - Every recommended item shows the generic ingredient and dose first, and a "buy anywhere" note.
   - Affiliate links (if any) are secondary, and they're shown even when the commission is $0.
   - Picks are ranked by third-party testing (USP, NSF, Informed Choice/Sport) and price per effective dose, never by commission rate.
5. **Clear disclosure at the point of the link.**
   - Show "Ebb earns a commission if you buy through this link. It never changes our recommendations." in plain text next to the link, not in a footer.
   - Korean pages carry "이 링크를 통해 구매 시 수수료를 받을 수 있습니다". Coupang links need Coupang's required disclosure sentence.
   - This complies with the FTC Endorsement Guides and the 공정위 추천·보증 심사지침.
6. **Safety first.**
   - The medication safety screen runs before any supplement link appears. If a user flags SSRIs, thyroid medication, pregnancy and so on, the relevant links disappear and the "talk to your doctor" message shows instead.
   - Tier 2 links appear only after week 5 and only once the user confirms clearance.
   - Tier 3 items get no links at all.
7. **The paywall never hides safety.** Red flags, the safety screen, dosing limits (e.g. stop ashwagandha by week 12) and "see a doctor" content stay free forever.
8. **Supplements stay the smallest lever.** The UI must reflect the plan's ranking: supplements appear below sleep, diet, exercise and alcohol. Supplement affiliate revenue is capped at **10% of total revenue**. If it ever exceeds that, review whether the product is drifting into a funnel.
9. **No data sale, no ad targeting.** Health logs never feed affiliate targeting. Links are the same for every user who passes the same safety screen, so no profile-based upsells.
10. **Honest claims everywhere.**
    - The Calm Score is a habit and feeling index, not a cortisol reading.
    - Marketing never promises spot fat loss or a lowered cortisol level. Use "habits linked to lower stress and waist size".
    - Supplement copy uses structure/function language at most, with the plan's own caveat that supplements are worth about 1–3 cm at best.
11. **Same principles for labs and partners.**
    - Lab-kit affiliates sit **after** the free option ("ask your doctor or use your insurance labs").
    - Clinics pay flat fees, never per-patient fees.
    - Employer dashboards show only anonymized aggregates for groups of at least 10.
12. **Independent review.** Once revenue exceeds about $5k MRR, pay a clinician or registered dietitian to review the supplement page each year, and publish their name and any conflicts.

---

## 6. Top 3 revenue streams to build first

1. **Plus with a Program Pass, sold on the web (months 1–3).**
   - Build: on-device insights engine, maintenance phase (weeks 13–52), lab tracker plus doctor PDF, and file-based wearable import.
   - Payments: Stripe (US/global) and Toss (Korea), with license-key or magic-link entitlements. No accounts and no store.
   - The fastest, lowest-risk revenue. It keeps 87–96% of gross.
2. **Pro AI coach (months 4–6).**
   - Opt-in, using a summary of the logs only, with zero retention and Haiku-class chat plus a Sonnet-class weekly review (~$0.50–0.60 per user per month).
   - Hard safety rails and a 14–21 day trial.
   - Lifts blended ARPPU by about 30% and is the main reason to upgrade.
3. **Disclosed lab-test affiliate at the day-1 and week-12 checkpoints, plus creator partnerships as the growth engine (months 3–6).**
   - Lab-test affiliate: near-zero build effort, and it fits the existing plan.
   - Creator revenue-share: brings in payers at an effective CAC of $12–20 with no upfront cash.

**Later (month 9+):** human coaching add-on → quarterly cohorts (bundled into Pro) → B2B pilots (Korean welfare malls; US wellness platforms) → clinic white-label. **Avoid:** own-brand supplements, ads, and any data monetization.

---

## Sources
- RevenueCat, *State of Subscription Apps 2025* (trial length vs. conversion; health and fitness benchmarks): https://www.revenuecat.com/state-of-subscription-apps-2025 ; secondary summary: https://www.saastr.com/the-top-10-learnings-from-revenuecats-state-of-subscription-apps/
- Toss Payments fee schedule: https://www.tosspayments.com/about/service/fee
- Apple third-party payments in South Korea (26% commission): https://www.cnbc.com/2022/06/30/apple-opens-up-third-party-app-payments-in-korea-will-take-26percent-cut-.html ; https://techcrunch.com/2022/06/30/apple-says-developers-will-have-to-submit-a-new-version-to-use-third-party-payment-systems-in-south-korea
- Epic v. Apple link-out commissions (status still evolving): https://9to5mac.com/2025/12/11/apple-defeats-ban-on-charging-commission-on-linked-out-purchases-from-ios-apps/ ; https://www.fenwick.com/insights/publications/ninth-circuit-largely-upholds-ruling-in-epic-v-apple
- Claude Haiku 4.5 pricing ($1 / $5 per million tokens): https://pricepertoken.com/pricing-page/model/anthropic-claude-haiku-4.5 (verify against Anthropic's pricing page)
- Everlywell affiliate terms (third-party, rates vary): https://getlasso.co/affiliate/everlywell/ ; iHerb affiliates: https://uk.iherb.com/affiliates
- Competitor pricing: [`../research/04-apps-and-design.md`](../research/04-apps-and-design.md)
- Program content and lab/supplement tiers: [`../PLAN.md`](../PLAN.md)

*Figures marked approximate come from third-party sources or modeling assumptions. Re-check fees, store rules and legal points before launch. This is not legal or tax advice.*
