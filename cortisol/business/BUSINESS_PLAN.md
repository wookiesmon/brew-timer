# Ebb: Business Plan (CEO summary)

This summary pulls together four team reports:
- [01 Market](01-market.md)
- [02 Business model](02-business-model.md)
- [03 Legal](03-legal.md) *(not legal advice)*
- [04 Growth & roadmap](04-growth-roadmap.md)

All numbers are planning estimates. Check them before committing money.

## 1. Thesis
"Cortisol" searches are up more than 5× since 2020, but the category is full of hype: "cortisol face", "detox" cocktails, and saliva panels. Doctors are publicly pushing back. Ebb's position is **"the cortisol trend, minus the nonsense"**:
- A **free, private, offline** 12-week program. It needs no wearable and no account.
- It is **measured with a tape measure, not a gimmick**. Success means waist, stress (PSS-10), resting HR and HRV all move the right way.
- **Honest supplement guidance:** evidence-graded, with a medication-safety screen, and never our own supplement brand.

## 2. Market
- **Total market:** about $4.5B a year is spent in health and fitness apps (2025, +13%), over half of it in the US. Stress management is the fastest-growing segment.
- **Realistic share:** $50k–400k ARR within 3 years. Only about 5% of health apps reach $10k in their first 2 years, so distribution is everything.
- **Korea:** 48.8% of men are obese (61.7% of men in their 40s), and the 저속노화 (slow-aging) trend is strong. Korean users prefer free apps, so cohorts, B2B and Toss/Kakao payments matter more there.
- **Personas:**
  1. US women aged 35–52 who are burned out and gaining weight at the waist. They'll pay $30–60 for a program. **This is the primary persona.**
  2. Korean office workers (영포티, men 33–49). They'll pay ₩9,900–19,900.
  3. People who own a wearable and track everything. They'll pay $20–40 a year as an add-on.

## 3. Business model: "free program, paid depth", web-first
Everything in today's app stays free forever, including all safety content. Payments are made on the web (Stripe, or Toss in Korea) to avoid the 15–30% app-store fee. Users unlock with a license key, so no account is needed.

| | Free | Plus | Pro |
|---|---|---|---|
| USD | $0 | $4.99/mo · $29.99/yr · **12-week Pass $14.99** (no auto-renew) | $12.99/mo · $89.99/yr |
| KRW (VAT incl.) | ₩0 | ₩5,900/mo · ₩34,900/yr · Pass ₩16,900 | ₩15,900/mo · ₩109,000/yr |
| What's in it | The whole current app | Insights engine, weeks 13–52 maintenance and special tracks, a lab tracker with a PDF for your doctor, encrypted backup and sync, wearable import, audio sessions, reminders | Everything in Plus, plus an opt-in **AI coach** (weekly review and up to 150 chat messages a month), and quarterly cohort challenges |

- **Add-ons:** human coaching at $149/mo, and paid Kakao/Discord **cohorts at $29 / ₩29,000**. Cohorts are the fastest first revenue, because they only need a payment link.
- **Why a 12-week Pass:** the median annual renewal for health apps is only about 25%. A one-time program purchase fits better than fighting churn.

**Unit economics**
- AI cost is about $0.50–1.40 per Pro user per month (5–10% of revenue).
- Gross margin is 90–96% on web payments, 82–87% through Toss after VAT, and 65–80% through the app stores.
- Blended lifetime value (LTV) is about $41 per paying user.
- Customer acquisition cost (CAC) is about $0–5 per payer from organic channels and $12–20 through creator revenue-share deals. Paid ads cost $45–110 and **don't pay back yet**.
- Fixed costs are about $100–150 a month, so **break-even is about 35 paying users**.

**Supplement guardrails** (these are what make the brand trustworthy)
- No own-brand supplements, ever.
- Evidence grades never depend on commissions.
- There are no links for anything on the "Skip" list.
- The disclosure sits right next to each link.
- The safety screen hides links when there is a risk.
- Supplement income is capped at 10% of revenue.

## 4. 24-month projection
| Case | Monthly users at M24 | Paid share | Monthly revenue at M24 | ARR run-rate | Revenue over 24 months |
|---|---|---|---|---|---|
| Conservative | 10k | 3% | $1.5k | $18k | $9.7k |
| **Base** | 40k | 4.5% | $16.0k | $192k | $115k |
| Optimistic | 180k | 6% | $80k | $963k | $490k |

In every case, the biggest lever is growth in monthly active users, not price.

## 5. Go-to-market (zero budget, founder-led)
1. **Post one short video a day for 90 days** across TikTok, Reels and Shorts. The anchor is the founder's own 84 days tracked on camera ("I measured my waist for 84 days"). Commenting a keyword triggers a DM with the free 12-week PDF, which builds the email list.
2. **Korean push:** "12주 뱃살·스트레스 리셋 / 저속노화" on YouTube Shorts, Naver Blog three times a week, and Threads. Launch on Disquiet.
3. **Kakao open-chat cohorts:** free monthly rooms that lead into a paid ₩29,000 guided cohort.
4. **Value-first Reddit data posts**, then Show HN in week 6 and Product Hunt in week 10.
5. **Micro-influencers paid by revenue share** (30%), never paid ads before LTV is at least 3× CAC.

The first 1,000 users should arrive by week 8 for less than $100. The first 100 paying users should arrive by week 13 (about $2.5–3k): cohort seats, founding-member annual plans, and affiliate sales.

## 6. Product roadmap (solo developer + AI)
| Weeks | Build | Dev-days |
|---|---|---|
| 1–2 | Privacy-friendly analytics, landing page, lead-magnet PDF, shareable result card | 6–8 |
| 3–4 | Cohort payment links, Plus/Pro license-key unlock | 3–4 |
| 5–7 | Opt-in encrypted backup, accounts (Google/Apple/Kakao), sync, web push | 10–12 |
| 7–9 | AI weekly report (Claude API, aggregate data only), Oura/WHOOP import, checkout | 10–12 |
| 9–12 | Paywall A/B test, referrals, Toss billing for Korea | 6–8 |
| 13–18 | Native apps (Capacitor + RevenueCat, Apple Health) **only if** D30 retention is at least 15% or MRR is at least $1k | 15–20 |

**90-day KPI targets**

| KPI | Target |
|---|---|
| Activation | ≥45% |
| Day-7 retention | ≥25% |
| Day-30 retention | ≥12% |
| Free to paid | ≥4% |
| Trial to paid | ≥35% |
| Finish the 12 weeks | ≥6% of all users (≥40% of cohort members) |
| NPS | ≥40 |
| Revenue by day 90 | $2.5k |

The **north-star metric** is weekly active loggers: users who log on 3 or more days a week.

## 7. Legal gates (do these before charging anyone)
1. **Wellness, not medical.**
   - No doses for named conditions.
   - No "lowers cortisol", "burns belly fat", "treats", or "clinically proven".
   - Lab tests are "tests to discuss with your doctor".
   - *These wording fixes have been applied in the app.*
2. **Pre-monetization** (about $2–7k): a doctor or dietitian reviews the content, an evidence file of citations is kept, an 18+ gate is added, a privacy notice is published, and a trademark check is done on "Ebb".
3. **Paid launch** (about $10–35k):
   - a legal entity;
   - lawyer-drafted terms of service and privacy policy (including Washington's My Health My Data Act);
   - compliant auto-renew and cancellation;
   - affiliate disclosures;
   - insurance.
4. **AI coach:**
   - a no-retention, no-training contract with the AI provider;
   - a red-flag screen that runs before the AI (crisis lines 988 / 109 / 119);
   - testing with 300+ adversarial prompts;
   - AI disclosure under the EU AI Act and Korea's AI Basic Act.
5. **Korea:** local counsel; separate consent for health data and for overseas data transfer; a privacy officer; an MFDS review of each supplement.
6. **Clinic partnerships in Korea:** flat fees only. Korean medical law bans paying per patient referral.

## 8. Virtual company
| Role | Who |
|---|---|
| CEO / face on camera / final say on health claims | Founder (human) |
| Engineering, QA, deploy checks, weekly improvement | AI agents (the **Ebb Living Bot** runs weekly; see `../LIVING_BOT.md`) |
| Research, scripts, Korean localization, content repurposing, support drafts, analytics | AI agents |
| Medical advisor (doctor or dietitian, 4–6 h a month) | **Human, required before paid coaching** |
| Community moderator (once there are more than 3 cohorts at a time) | Human, part-time |
| Lawyer (privacy and terms), tax accountant (세무사) | Human, one-off or as needed |

**Budget:** about $500–1,000 a month in months 1–3, mostly the medical advisor. About $1.5–2.8k a month in months 4–6.

## 9. Founder decisions (27 Oct 2026)
1. **Launch order:** US first (English, lb/in, Stripe), then Korea (Toss/Kakao, Korean UI already built), then Spanish-speaking markets (the app is ready for `i18n/es.js`).
2. **84-day on-camera challenge:** yes, the founder films it. See [05-84-day-film-playbook.md](05-84-day-film-playbook.md).
3. **Still open:** approve the gated backlog items (analytics, license-key unlock) in `../BACKLOG.md` by adding `[approved]`.
