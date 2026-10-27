# 04: Growth & Product Roadmap

*Growth & Product Roadmap team · monetization division · prepared 2026-10-27*

**Product:** Ebb, a free, private, offline PWA (one HTML file, `localStorage`, no accounts, no backend) that runs a 12-week program to lower stress and belly fat. It has a Calm Score, check-ins, waist/weight/HRV logging, a breathing pacer, charts and tiered supplement guidance.
**Founder:** a solo builder who uses AI coding tools heavily, is probably Korean-speaking, and has close to no budget.
**Goal of this doc:** (1) go-to-market, (2) CAC by channel plus plans for the first 1,000 users and first 100 payers, (3) a technical roadmap to monetization with effort estimates, (4) a 90-day launch plan with KPIs, (5) the org chart of the "virtual company" with a budget.

> **Working assumptions.** Pricing is not settled here; the pricing/business-model doc should own it. For the funnel maths this doc assumes **Ebb Pro at $5.99/mo or $34.99/yr (₩6,900/mo or ₩39,000/yr)**, a 7-day free trial on annual, plus a one-off **"Guided Cohort" at $29 / ₩29,000** for 12 weeks of group coaching. The free core program stays free forever. That free core is the brand and the growth engine.

> **Guardrails for all growth work.** Ebb never says it measures or "lowers cortisol" as a clinical claim. The Calm Score is a habit index (see PLAN.md). The cortisol trend is full of overclaiming ("cortisol face", "cortisol detox"), and doctors are pushing back in public ([Healthline](https://www.healthline.com/health-news/cortisol-face-tiktok), [2 Minute Medicine](https://www.2minutemedicine.com/tiktoks-cortisol-face-trend-meets-endocrine-reality/), [DocCheck](https://www.doccheck.com/de/detail/articles/53846-cortisol-detox-und-abnehmen-was-steckt-hinter-dem-social-media-hype)). **Our wedge is to be the honest, evidence-based voice in a hype category.** "The cortisol trend, minus the nonsense" is both safer and better positioning.

---

## 1. Go-to-market for a near-zero budget

### 1.1 Positioning in one line
- **EN:** *"The free 12-week reset for stress belly: sleep, light, breath, protein and walking. No cortisol 'detox', no account, no subscription needed."*
- **KR:** *"스트레스 뱃살 12주 리셋: 수면·햇빛·호흡·단백질·걷기. 코르티솔 디톡스 같은 과장 없이, 가입 없이 무료로."*

Three proof points to repeat everywhere:
1. **Free and private.** No signup, and the data never leaves the phone. That is rare in health apps and makes a great hook.
2. **Measurable.** Waist tape plus resting HR/HRV, not vibes.
3. **Honest.** The evidence is ranked, and supplements are called "the smallest lever" (PLAN.md).

### 1.2 Content-led growth: TikTok, Reels, Shorts (English)

**Why it works:** "cortisol" is now an evergreen short-form topic. It began on TikTok and spread to Reels and Shorts ([Bobcat Prowl](https://thebobcatprowl.com/20613/opinion/the-cortisol-craze-of-2026)), and Europe has a low-cortisol diet wave under #cortisolcontrol ([W Korea](https://www.wkorea.com/?p=367342)). Demand exists; trustworthy supply does not.

**Format system** (one shoot gives three platforms). Post the same 9:16 video to TikTok, Reels and Shorts with platform-native captions.

| Pillar | Share | Example | CTA |
|---|---|---|---|
| **Myth vs evidence** ("Doctor-reviewed or not?") | 30% | "'Cortisol face' is probably salt and sleep. Here's what does move stress belly." | "Free 12-week plan, link in bio" |
| **Founder build-in-public: 12 weeks on camera** | 25% | Weekly waist/RHR/HRV update with real numbers, including bad weeks | "Track yours free" |
| **Do-it-with-me rituals** | 20% | 5-minute cyclic sighing with the Ebb pacer on screen; the 06:40 light walk | Save/duet |
| **Data and insight** | 15% | "My HRV vs sleep, 30 days" chart from the app | Comment keyword → email DM |
| **App demo / UGC stitch** | 10% | "This app has no signup and no paywall. Here's why." | Link |

**Cadence:** 1 short a day for 90 days (AI pipeline in section 1.9 makes this ~45 min/day). One long YouTube video every 2 weeks.

**Comment-to-DM loop:** "Comment RESET and I'll send you the 12-week PDF." Use ManyChat on Instagram (free tier) to auto-DM the lead-magnet link. This is the single highest-converting tactic for building an email list from Reels.

### 1.3 Korean strategy: YouTube, Naver Blog, Threads

The Korean market is attractive: a strong "다이어트" and "저속노화" (slow-aging) culture, high smartphone wearable use (Galaxy Watch, Apple Watch), and few Korean-language cortisol tools. The domestic trend has been "slow aging" more than "cortisol" ([W Korea](https://www.wkorea.com/?p=367342)), so **frame Ebb as "저속노화 + 스트레스 뱃살"** instead of importing the TikTok cortisol hype as-is.

| Channel | Role | Plan |
|---|---|---|
| **YouTube (KR)** | Trust + search | Shorts every day (dubbed/re-shot KR versions) plus a long video every 2 weeks: "12주 코르티솔 리셋 1주차 기록", "마그네슘 종류별 차이, 약사·논문 기준". Faceless is fine; voice and on-screen data work. |
| **Naver Blog** | Search traffic (Naver holds ~55–63% of KR search: [Interad](https://interad.com/en/insights/naver-seo-guide), [Inquivix](https://inquivix.com/korean-search-engines/)) | 3 posts a week in one topical lane to build **C-Rank** (topic consistency over time) and **D.I.A.** (post depth, dwell time) ([Interad on the VIEW algorithm](https://interad.com/en/insights/naver-view-algorithm)). Write long posts with original photos, charts from the app and a personal log. Avoid exact-match keyword stuffing. Add a monthly "12주 기록 정리" post. |
| **Naver Cafe** | Community | Join existing 다이어트/러닝/직장인 건강 cafes; give value, link only where allowed. |
| **Threads (KR)** | Founder voice | Threads is popular in Korea with a text-heavy, build-in-public culture. Post daily notes: "1인 개발자가 무료 건강앱 만드는 기록", revenue screenshots later. Draws other builders + early adopters. |
| **Kakao open chat** | Cohorts (see 1.7) | |
| **Brunch / 디스콰이엇 (Disquiet)** | Launch | Disquiet is Korea's maker community, the local Product Hunt. Launch there the same week as PH. |

**Korea-specific compliance:** do not market supplements as treating disease (식품표시광고법 rules apply to health functional food claims), and **disclose all paid partnerships** ("유료광고 포함"; the KFTC endorsement guideline cracked down on hidden ads, "뒷광고", in 2020). Health data counts as sensitive information under PIPA (개인정보보호법), which matters once there is a backend (section 3.1).

### 1.4 Ten specific viral content ideas

1. **"I tracked my waist, HRV and stress for 84 days. Here's every number."** A 12-part series, one per week, ending in a full reveal. Includes the weeks nothing changed. Hook: honesty.
2. **"Rating every cortisol TikTok hack from 0 to 10, using actual studies."** Cortisol mocktail, adrenal cocktail, "cortisol face", lemon water, ashwagandha. Stitch-able and recurring.
3. **"The 5-minute breathing pattern that beat meditation in a Stanford study"** (cyclic sighing). Breathe along with the Ebb pacer on screen. Highly saveable.
4. **"Mayo Clinic: 2 weeks of short sleep added 11% belly fat."** Green-screen the study, then show the Ebb sleep habit. Uses PLAN.md's top-ranked lever.
5. **"Supplements ranked by how much belly fat they actually remove"** (tier list format, with the honest result: 1–3 cm at best). Contrarian, and tier lists perform reliably.
6. **"My HRV the morning after: beer vs. no beer vs. late dinner vs. 10 pm bedtime."** Experiment format with chart reveal.
7. **"POV: an app that doesn't want your email, your data or your money."** Screen recording of airplane mode → app still works. Plays on privacy fatigue.
8. **"Day in the life on a 'calm' fat-loss protocol"** walking through the PLAN.md daily rhythm (06:30 → 22:30) in 45 seconds. Aesthetic, sage/sand visuals.
9. **KR: "직장인 스트레스 뱃살, 회사에서 할 수 있는 5가지"** (desk breathing, after-lunch 10-min walk, 12 pm last coffee, protein lunch, 21:00 screens down). Very relatable for Korean office workers.
10. **KR: "한국인 식단으로 코르티솔 리셋하기: 국밥 vs 샐러드가 아니다"** Korean-food protein/fibre swaps (두부, 계란, 잡곡밥, 나물) with an honest look at sodium and the "cortisol face" myth.

Bonus evergreen: duet/stitch any viral "cortisol cocktail" video with a calm 20-second evidence response. These ride other people's reach for free.

### 1.5 SEO keywords

Target: one evergreen landing page per keyword cluster on the GitHub Pages site (static HTML, no backend), plus Naver Blog for Korean. Volumes are not verified here; check them in Google Keyword Planner / Ahrefs free tools and **Naver DataLab / 검색광고 키워드도구** before writing.

**English**
| Cluster | Keywords | Intent / page |
|---|---|---|
| Core | how to lower cortisol naturally; lower cortisol fast; cortisol reset; 12 week cortisol reset | Lead-magnet landing page |
| Belly | cortisol belly; stress belly fat; how to lose cortisol belly; cortisol belly vs hormonal belly | Pillar article + waist tracker |
| Diet | low cortisol diet; foods that lower cortisol; cortisol diet plan | Article + PDF meal guide |
| Supplements | magnesium glycinate for cortisol; ashwagandha cortisol weight loss; best supplements to lower cortisol; L-theanine with coffee | Evidence tier article (high commercial intent) |
| Symptoms (careful) | signs of high cortisol in women; cortisol face real? | Myth-busting article with "see a doctor if" list |
| Tools | cortisol tracker app; free stress tracker app; HRV tracker no subscription; waist tracker app | App landing page |
| Breath | cyclic sighing; 5 minute breathing for stress | Pacer page (works as a standalone tool) |

**Korean (한국어)**
| 클러스터 | 키워드 |
|---|---|
| 핵심 | 코르티솔 낮추는 법; 코르티솔 수치 낮추기; 코르티솔 다이어트; 코르티솔 리셋 |
| 뱃살 | 스트레스 뱃살; 코르티솔 뱃살; 뱃살 빼는 법 직장인; 내장지방 빼는 법 |
| 식단 | 코르티솔 낮추는 음식; 저코르티솔 식단; 저속노화 식단 |
| 영양제 | 마그네슘 글리시네이트 효과; 아쉬와간다 효과 부작용; 테아닌 커피; 오메가3 복용시간 |
| 증상 | 코르티솔 높으면 증상; 코르티솔 얼굴; 부신피로 (myth-busting) |
| 도구 | 스트레스 관리 앱; 무료 다이어트 앱 가입없이; 심박변이도 HRV 앱; 허리둘레 기록 앱 |
| 호흡 | 스트레스 호흡법; 4-7-8 호흡; 한숨 호흡 |

Tactics: answer-first headings (helps Google AI Overviews and Naver AI Briefing ([Inblog](https://inblog.ai/glossary/naver-seo))), FAQ schema, original charts, a cited sources list (the research folder already has this, which makes it a moat), and internal links into the app.

### 1.6 Lead magnet: the free "12-Week Cortisol Reset" + email list

The app works without an email, and it should stay that way. The email list is a **separate, optional** layer:

- **Asset:** "The 12-Week Stress-Belly Reset" PDF (EN + KR), generated from PLAN.md: phases, daily rhythm, training week, supplement tiers, lab checklist, "see a doctor if" box. Add a printable 84-day habit grid. ~1 day to produce with AI.
- **Capture points:** link in bio → landing page; in-app "Get the weekly guide by email" card at day 3 (after the first win, not on first open); comment-to-DM.
- **Sequence: 12 weekly emails** that track the program week ("Week 3: add intervals"), plus 3 onboarding emails on days 0, 2 and 5. Each weekly email has one tip, one study, one action and a "log your waist" nudge back into the app. The week 4, 8 and 12 checkpoints are where Pro upsells sit (charts, AI report).
- **Tools:** **Kit** free up to 10,000 subscribers (branding; limited automations) or **Beehiiv** free up to 2,500 ([Sender](https://www.sender.net/compare/beehiiv-vs-kit/), [Dupple](https://dupple.com/learn/best-free-email-marketing-tools)). In Korea, **Stibee (스티비)** is the local default for newsletters; check current free limits. Start on Kit; move to a paid tier (~$30–40/mo) when sequences are needed.
- **Target:** 25–35% of landing visitors → email; 40%+ open rate on the weekly program emails.

### 1.7 Community without spam

**Reddit.** Reddit punishes promotion; the 9:1 (≈10% self-promo) norm is etiquette, not law, and each subreddit sets its own rules ([Redship](https://redship.io/blog/reddit-self-promotion-rules-2026), [Analytics Insight](https://www.analyticsinsight.net/business/how-to-promote-your-website-or-business-on-reddit-without-being-flagged-as-spam)).
- **Rule 1: be useful first, for 4 weeks.** Answer questions in r/loseit, r/Biohackers, r/Supplements, r/HRV, r/sleep, r/PCOS, r/Anxiety (carefully), r/intermittentfasting, r/AskWomenOver30. Cite studies. No links.
- **Rule 2: post the data, not the app.** "I logged 84 days of waist/HRV/sleep. Here's what correlated" as a text post with charts. Put the link in a comment only if someone asks, or if the sub allows it.
- **Rule 3: use the right places for the app.** r/SideProject, r/InternetIsBeautiful (it fits: free, no signup, offline), r/selfhosted-adjacent privacy crowds, r/PWA, r/webdev "Show-off Saturday", r/indiehackers. These allow showing a project.
- **Rule 4: one account, real identity, disclose you built it.** Never astroturf.

**Kakao open chat cohorts (카카오톡 오픈채팅).** Cohorts are the Korean growth engine and the first paid product:
- **Free "12주 리셋 동기" cohort.** It starts on the 1st Monday of each month, with 50–150 people per room and an anonymous profile allowed. Daily rhythm: morning check-in emoji, 1 tip, Sunday waist-log screenshot from the app. Cohort start dates create urgency and FOMO.
- **Paid "가이드 코호트" (₩29,000).** A smaller room (≤30) with a weekly live Q&A (voice/YouTube live), weekly AI-generated personal report, completion certificate and a refund if you log 70%+ of days (commitment device). This is the fastest route to the **first 100 paying users**, because it needs Toss/payment links only, no in-app paywall.
- Mirror it in English with a **Discord or WhatsApp Community** cohort.
- Moderation rule: no supplement selling, no medical advice; refer red-flag symptoms to a doctor (PLAN.md "See a doctor if" list).

### 1.8 Micro-influencers and Product Hunt

**Micro-influencers (10k–50k).** Published rates vary widely, from ~$25–125 to $500–2,000 per post ([Socially Powerful](https://sociallypowerful.com/influencer/marketing/cost), [Hootsuite](https://blog.hootsuite.com/tiktok-influencers), [DesignRush](https://www.designrush.com/agency/social-media-marketing/instagram/trends/influencer-rates), [Hypefy](https://hypefy.ai/blog/cost-of-influencer-marketing)). A realistic budget for health/wellness creators is **$100–400 per Reel**.
- Who to target: registered dietitians, physios, nurses, PTs, "perimenopause" and "PCOS" creators, run clubs, Korean 직장인 vlog and 홈트 creators. Credentialed creators lower the medical-claims risk.
- **Zero-cash offer first:** lifetime Pro + a co-branded cohort + **30–40% revenue share via an affiliate link** (Lemon Squeezy has built-in affiliates). Pay cash only after a creator converts on affiliate.
- **Gifted "12-week challenge" format:** the creator runs the program on camera with weekly updates. Their audience joins via a custom cohort link. Measure by unique link / UTM / promo code.
- Budget: $0 in months 1–2; $500–1,000/mo from month 3, only for creators whose affiliate test converted.
- Disclosure: #ad / "유료광고 포함" every time.

**Product Hunt (+ Disquiet in Korea, Hacker News "Show HN").**
- When: week 8–10 of the 90-day plan, after the paywall and AI weekly report exist, because PH users are builders who try and then leave. The goal is backlinks, press and a credibility badge, not long-term users.
- Prep: 4 weeks of "coming soon" page follows, a 60-second demo video, 5 screenshots, a maker comment telling the story ("I built a free, offline, no-signup health app because…"), launch at 00:01 PT on a Tuesday–Thursday, and personally message 100+ supporters (no vote-begging, which PH penalizes).
- **Show HN** angle: "Show HN: A 12-week stress/belly-fat program in one offline HTML file (no backend)". HN loves single-file, privacy-first apps; that is our best tech angle.
- Expected: 500–3,000 visits; 150–600 activated users; useful for the first 1,000.

### 1.9 AI-assisted content production pipeline

A solo founder needs **~1 daily short, 3 Naver posts/week, 1 newsletter/week and 1 long video every 2 weeks** in two languages. The pipeline:

```
 Research bank (research/*.md, PubMed alerts, Reddit/TikTok comments)
        │  weekly, Mon: Claude extracts 10 hooks + claims with citations
        ▼
 Content calendar (Notion/Sheet) ── human picks 7 hooks (15 min)
        │
        ▼
 Script agent (Claude): EN 45-sec script + KR adaptation (not literal translation),
   on-screen text, caption, hashtags, CTA, a "claims check" list linking each claim to a source
        │
        ▼  HUMAN GATE 1: fact/claims check (10 min/day). Medical advisor spot-checks weekly.
        ▼
 Production: founder films 3–4 talking-heads in one 60-min batch (Sunday)
   + app screen recordings; CapCut / VREW (KR auto-subtitles) for edit & captions;
   ElevenLabs voice for faceless KR/EN versions (disclose AI voice); Canva for carousels/thumbnails
        │
        ▼
 Repurpose agent: short → Naver Blog post (1,500+ chars, with own charts), Threads thread,
   Reddit-safe text post draft, newsletter section, X post
        │
        ▼
 Scheduling: Postiz / Buffer / Metricool (free tiers) → TikTok, IG, YT, Threads
        │
        ▼
 Weekly analytics review agent: pulls views/saves/link clicks/email signups,
   ranks hooks, writes next week's brief  ── HUMAN GATE 2: strategy decisions
```

Time budget: about **7 hours/week** for all content once the pipeline runs. Rules: AI never posts unreviewed health claims; every claim maps to a source in `research/`; AI voices and avatars are disclosed.

---

## 2. CAC by channel, first 1,000 users, first 100 paying users

### 2.1 Definitions
- **User** = someone who opened the app and **activated** (completed onboarding + logged a first check-in or a first measurement). Without accounts, count activations with privacy-friendly analytics events (section 3.8).
- **Cash CAC** = money spent ÷ activated users. **Loaded CAC** adds the founder's time at a notional $25/h, so channels can be compared honestly.
- **Paid CAC** = cash CAC ÷ free-to-paid conversion. With the ~4–6% conversion assumed for organic health users, a $1 cash CAC per activated user is about $20 per payer.

### 2.2 Channel CAC estimates (ballpark, to be replaced with real data by week 6)

| Channel | Cash cost | Assumptions | Cash CAC / activated user | Loaded CAC | Scales? | Verdict |
|---|---|---|---|---|---|---|
| Short-form organic (EN TikTok/Reels/Shorts) | $0–30/mo tools | ~5k–20k views/video avg, 0.3–0.8% bio-link click, 40% activation | **≈$0** | $1–4 | High, but lumpy | **Core channel** |
| Korean YouTube Shorts + long-form | $0–20/mo | Slower to start; long-form search compounds | ≈$0 | $2–5 | Medium-high | Core for KR |
| Naver Blog SEO | $0 | 3 posts/week; traffic from month 2–3 as C-Rank builds | ≈$0 | $1–3 (after month 3) | Medium, compounding | Core for KR |
| Google SEO (EN landing pages) | $0 | Slow (3–6 months) | ≈$0 | $2–6 early, <$1 later | High long-term | Invest early, harvest later |
| Reddit (value-first) | $0 | 2–4 data posts/month; 50–500 visits each | ≈$0 | $1–3 | Low-medium | High-quality early users |
| Kakao open chat cohorts | $0 | Seeded from KR content; 50–150/cohort | ≈$0 | $1–2 | Medium | **Best KR activation + conversion** |
| Product Hunt / Show HN / Disquiet | $0 | One-off spikes | ≈$0 | $0.5–2 | One-off | Do once, well |
| Micro-influencers (affiliate first) | $0 cash on affiliate; $100–400/post paid | 20k views × 0.5% click × 40% activation ≈ 40 users/post | **$2.50–10** | $3–12 | Medium | Only after affiliate proves conversion |
| Email (own list) | $0–40/mo | Re-activation and upgrade channel | n/a | n/a | — | Conversion engine |
| Paid social (Meta/TikTok ads) | $300+ test | Health & fitness CPI often $2–5 in the US; similar or higher in KR; web-app funnels lose more | **$4–12** | $5–14 | High | **Don't** until LTV > 3× CAC is proven |
| Apple Search Ads (if native) | $200+ test | Only after the App Store build | $3–8 per install | — | Medium | Phase 3 |

Paid acquisition is off the table until the economics work: at $34.99/yr with ~25–35% churn and fees, a payer is worth maybe $40–60 LTV in year one, which supports at most ~$15–20 paid CAC per payer, i.e. under ~$1 per activated user. **Only organic and affiliate channels clear that bar at launch.**

### 2.3 First 1,000 users plan (weeks 1–8)

| Source | Target users | How |
|---|---|---|
| Founder's network + Threads (KR) build-in-public | 80 | Personal posts, KakaoTalk friends, Disquiet profile |
| Short-form EN (TikTok/Reels/Shorts, 50+ videos) | 300 | Daily posting; comment-to-DM; pin the best 3 |
| Korean Shorts + Naver Blog (25 posts) | 200 | Daily Shorts; Naver blog 3×/week |
| Kakao open chat cohort #1 and #2 | 150 | Recruit from KR content; "12주 리셋 동기" |
| Reddit (4 data posts + r/InternetIsBeautiful + r/SideProject) | 150 | Value-first, see 1.7 |
| Show HN + Disquiet (soft launch, week 6–7) | 120 | Single-file/offline technical story |
| **Total** | **1,000** | Cash spend < $100 |

Milestones: 100 users by week 3 (network + Reddit + first videos), 400 by week 5, 1,000 by week 8. If short-form is under 100 users by week 4, shift effort to Korean cohorts and Reddit data posts.

### 2.4 First 100 paying users plan (weeks 6–13)

The fastest money does **not** need the full tech stack. It needs a payment link:

| Offer | Price | Target payers | Mechanism | Needs |
|---|---|---|---|---|
| **Paid KR "가이드 코호트"** (₩29,000, 12 weeks, ≤30 per room) | ₩29,000 | 40 | Upsell from the free Kakao cohort + KR newsletter | Toss Payments link / 스마트스토어 or Lemon Squeezy KRW checkout; no code |
| **EN Guided Cohort** (Discord, $29) | $29 | 20 | Newsletter weeks 2–4 + Reddit/short-form audience | Lemon Squeezy checkout link |
| **Founding Member Pro** (lifetime-ish annual at $24.99 first year, locked) | $24.99/yr | 30 | In-app banner after the week-4 checkpoint; email | License key unlocks Pro features locally (section 3.2, phase A) |
| **Affiliate / creator cohorts** | $29 | 10 | 2–3 micro-creators on revenue share | Affiliate links |
| **Total** | | **100** | ≈ $2,500–3,000 revenue | |

Conversion maths: from ~1,500 activated users by week 12, with ~400 on the email list and ~300 in Kakao cohorts, 100 payers is ~6–7% of activated users. That is ambitious but realistic for cohort products, whose conversion runs higher than self-serve apps. For reference, RevenueCat reports a median **trial-to-paid** rate of ~40% in Health & Fitness for apps that run trials, and longer trials (17–32 days) convert best ([RevenueCat SOSA 2025](https://revenuecat.com/state-of-subscription-apps-2025), [Athletech News](https://athletechnews.com/fitness-apps-monetizable-winner-take-all-or-most/), [SaaStr](https://www.saastr.com/the-top-10-learnings-from-revenuecats-state-of-subscription-apps/)). The challenge is getting users to *start* a trial, which is why the week-4 checkpoint is the place to ask.

---

## 3. Technical roadmap to monetization

Estimates are for **one developer using AI coding tools** (Claude Code / Cursor), in focused days (~6 h). "AI multiplier" is already included. The rule throughout is that **the free offline core stays account-free**. Every server feature is opt-in.

### 3.0 Architecture target

```
 [Ebb PWA: single HTML today → small Vite build when needed]
     │  local-first: localStorage → IndexedDB (Dexie) as source of truth
     │
     ├── Free mode (default): no network, no account; export/import JSON
     │
     └── Ebb Pro (opt-in): Supabase Auth (magic link / Kakao / Apple / Google)
            ├── Sync: encrypted snapshots or row-level sync (RLS) to Postgres
            ├── Edge Functions: payment webhooks (Lemon Squeezy/Stripe, Toss),
            │                   Claude API weekly report, push sender, referral credits
            └── Entitlements table: source of truth for Pro (web + RevenueCat if native)
```

### 3.1 Accounts and cloud sync (Supabase), with a privacy-first option

- **Phase A: privacy-first sync without an account (2–3 days).** Encrypted backup: the app encrypts the JSON export with a passphrase (WebCrypto AES-GCM) and stores the blob in Supabase Storage under a random ID. This gives "sync" and a device restore with zero personal data on the server. It can also be a Pro feature.
- **Phase B: real accounts (5–7 days).** Supabase Auth (email magic link, Google, Apple; **Kakao login** via OAuth for Korea), Postgres tables (`profiles`, `daily_logs`, `measurements`, `entitlements`, `referrals`) with **Row Level Security**, last-write-wins sync per record, and migration from `localStorage` to IndexedDB. Keep a "Local only" toggle and a one-tap "Delete my cloud data".
- **Cost:** Supabase free tier for launch (it pauses after inactivity and has limited MAU/storage), then **Pro at $25/mo** with compute credits included ([Supabase pricing](https://supabase.com/pricing.md), [MakerKit](https://makerkit.dev/blog/saas/supabase-pricing)). Health data counts as **sensitive data** under Korean PIPA and as special-category data under GDPR. Get explicit consent, choose an EU or Seoul region deliberately, and publish a plain-language privacy page.
- **Effort total: ~8–10 days.**

### 3.2 Payments: Lemon Squeezy / Stripe on web, Toss in Korea, RevenueCat if native

| Option | Fees | Why / when | Effort |
|---|---|---|---|
| **Lemon Squeezy** (Merchant of Record, now owned by Stripe) | 5% + 50¢, plus surcharges for international cards/PayPal/subscriptions ([Dodo](https://dodopayments.com/blogs/lemonsqueezy-review), [Fungies](https://fungies.io/alternatives/lemon-squeezy)) | **Start here.** As MoR it handles global VAT/sales tax, which a solo Korean founder cannot do. Built-in affiliates and license keys. | 2–3 days |
| **Stripe** (direct) | ~2.9% + 30¢ (US) + Stripe Tax | Cheaper at scale, but you own tax compliance. Paddle is the other MoR option. Switch at roughly >$10k MRR. | 3–4 days |
| **Toss Payments (토스페이먼츠)** | Card ~3.4%, bank transfer 2.0% (VAT extra); signup fee ₩220,000 + annual ₩110,000, varies by contract ([Toss fee page](https://www.tosspayments.com/about/fee)) | For Korean users who expect 카드/간편결제/토스페이/카카오페이. Billing-key (자동결제) recurring requires a separate review. Needs a 사업자등록 (business registration). | 3–5 days + review |
| **RevenueCat** | Free up to a revenue threshold, then a % of tracked revenue | Only if going native: it unifies App Store/Play receipts with web entitlements | 2–3 days |

**Staged rollout:**
- **A (week 3, 1 day):** payment *links* for cohorts. Pro is unlocked with a **license key** checked against the Lemon Squeezy license API and cached locally, so no account is needed and privacy is preserved.
- **B (week 8, 3 days):** in-app checkout overlay + webhooks → `entitlements` table (needs 3.1 phase B).
- **C (month 4+):** Toss billing for KRW subscriptions.

### 3.3 Wrapping the PWA for App Store / Play (Capacitor), and when it's worth it

- **What:** Capacitor wraps the existing web app in a native shell with native plugins (HealthKit/Health Connect, local notifications, in-app purchase).
- **Worth it when** (any two of these are true): (a) PWA retention is proven (D30 ≥ 15%) and the binding constraint is discovery/trust ("is this a real app?"); (b) users ask for Apple Health / Health Connect import, which **requires native**; (c) iOS push reliability is hurting retention; (d) ≥$1k MRR to absorb store fees.
- **Not before:** a thin webview risks App Store **guideline 4.2 (minimum functionality)** rejection. Ship it with native value (HealthKit import, local notifications, widgets), not as a bare wrapper.
- **Store economics:** Apple's Small Business Program and Google subscriptions are 15% ([Appbot](https://appbot.co/blog/app-developers-apple-google-small-business-programs/), [D-TT](https://www.d-tt.nl/en/articles/app-store-commissions-how-much-do-you-pay-apple-and-google-and-how-can-you-keep-costs-down)). In Korea, alternative billing is allowed by law (Google's fee drops to ~11%) ([The Register](https://www.theregister.com/2021/10/21/google_subscription_fees/)). In the US, Apple was ordered to allow external purchase links in 2025, but the Ninth Circuit has since allowed some commission, so the status is unsettled ([Macworld](https://www.macworld.com/article/2769359/court-orders-apple-to-allow-external-purchase-links-in-apps.html), [Fenwick](https://www.fenwick.com/insights/publications/ninth-circuit-largely-upholds-ruling-in-epic-v-apple)). Plan IAP via RevenueCat as the default and keep web checkout for web users.
- **Effort:** a Capacitor shell + icons/splash + store listings + review = **5–8 days**; Apple Developer $99/yr, Play $25 once.

### 3.4 Apple Health / Health Connect / Oura / WHOOP import

| Source | How | Requires | Effort |
|---|---|---|---|
| **Manual + CSV import** (any wearable export) | Parse Apple Health export / Oura CSV / Galaxy Health CSV in-browser | Nothing (works in the PWA) | 2–3 days |
| **Oura** | OAuth2 REST API v2 (personal access tokens are being deprecated) ([Oura support](https://support.ouraring.com/hc/en-us/articles/4415266939155-The-Oura-API), [oura-api lib](https://jsr.io/@pinta365/oura-api)) | Backend for OAuth tokens (Supabase Edge Function) | 3–4 days |
| **WHOOP** | OAuth2 REST API v2 (recovery incl. HRV as RMSSD, RHR, sleep), webhooks, rate limits ([Thryve](https://www.thryve.health/blog/whoop-api-data-access-integration)) | Backend + developer app approval | 3–4 days |
| **Apple HealthKit** | Native only: Capacitor plugin (`@capawesome-team/capacitor-health`, `@capgo/capacitor-health`) ([Capawesome](https://capawesome.io/blog/announcing-the-capacitor-health-plugin/), [Capgo](https://capgo.app/docs/plugins/health/getting-started/)). Check HRV type support per plugin; may need a small custom Swift bridge for HRV SDNN | Capacitor iOS app | 4–6 days |
| **Health Connect (Android, incl. Samsung Health sync)** | Same plugins | Capacitor Android app | 3–4 days |

Normalization note: WHOOP/Oura report HRV as RMSSD, Apple as SDNN, so **show each source's trend against its own baseline** and never mix the absolute values. Order: CSV import (PWA, now) → Oura/WHOOP (Pro, needs backend) → HealthKit/Health Connect (with the native app).

### 3.5 AI coach (Claude API) with weekly report generation

- **Feature:** each Sunday, a **Weekly Calm Report**: what changed (waist 7-day trend, RHR/HRV vs baseline, sleep nights ≥7 h, Calm Score average), the top correlation ("on 10 pm bedtimes your next-day stress averaged 1.4 lower"), one focus for next week by phase, and red-flag routing ("waist unchanged after 8 honest weeks → see a doctor", per PLAN.md). Pro users can also ask questions in chat, with limits.
- **Design:** the app computes stats locally and sends **only aggregates** (no name, no free text unless the user opts in) to a Supabase Edge Function → Claude API. The system prompt holds the PLAN.md + research rules: no diagnosis, no supplement dosing beyond the plan's tiers, never claims to measure cortisol. Cache the system prompt (prompt caching) and generate the reports in the batch API overnight.
- **Model + cost:** a small model is enough for weekly reports. Haiku 4.5 is ~$1 / $5 per million input/output tokens, Sonnet ~$3 / $15; batch saves 50% and cache reads up to 90% ([Morph](https://www.morphllm.com/anthropic-claude-api-pricing), [MetaCTO](https://metacto.com/blogs/anthropic-api-pricing-a-full-breakdown-of-costs-and-integration); check the [official pricing page](https://platform.claude.com/docs/en/about-claude/pricing)). One report ≈ 3k input + 800 output tokens ≈ **$0.004–0.01**, so 1,000 Pro users × 4 reports/mo ≈ **$15–40/mo**. Chat at 20 messages/user/mo adds ~$20–60 per 1,000 users. Cap it per user.
- **Safety:** an output-checking pass (a regex + small-model classifier for dosing/diagnosis language) and a "report a bad answer" button. The medical advisor reviews 20 random reports a month.
- **Effort:** weekly report **4–5 days**; chat coach +3–4 days; KR language prompts +1 day.

### 3.6 Push reminders

- **PWA web push** works on iOS 16.4+ **only when installed to the Home Screen** and after a user gesture ([Apple Dev Forums](https://developer.apple.com/forums/thread/732594), [OneSignal](https://documentation.onesignal.com/docs/web-push-for-ios)); Android/desktop work normally. This needs a sender (Edge Function + VAPID keys, or OneSignal free tier) and stores a push subscription. That is a small server footprint; make it opt-in.
- Reminders: morning light, 12:00 last caffeine, 21:00 wind-down, Sunday waist log, checkpoint days 28/56/84. Respect quiet hours. Calm tone, no guilt (research/04 design principles).
- Native (Capacitor) local notifications need no server at all, which is another argument for the native build later.
- **Effort:** 2–3 days (web push), 1 day (native local notifications).

### 3.7 Referral program

- **Mechanic:** "Give 1 month of Pro, get 1 month" (EN), and "친구 초대하면 둘 다 코호트 50% 할인" (KR). Referral codes live in the Supabase `referrals` table; credits apply via a Lemon Squeezy discount code or entitlement extension.
- **Privacy-first variant:** a shareable **"My 12-week result" card** (waist −X cm, Calm Score trend) rendered as an image on the device with a link. This is free virality without accounts and probably the best referral driver. Build it first.
- **Effort:** share card 1–2 days; full referral credits 3–4 days (after accounts and payments).

### 3.8 Privacy-friendly analytics

- **Plausible** (from ~$9/mo for 10k pageviews, cookieless) for traffic and goals; or **PostHog** (free for the first 1M events per month; funnels, retention, feature flags and A/B tests) ([PostHog pricing](https://posthog.com/pricing), [PostHog vs Plausible](https://posthog.com/blog/posthog-vs-plausible)).
- **Recommendation:** PostHog EU cloud with **cookieless/anonymous mode**, autocapture off, a **fixed event list** (`onboarding_complete`, `checkin_logged`, `measurement_logged`, `breath_session`, `week_n_reached`, `checkpoint_completed`, `paywall_view`, `trial_start`, `purchase`), a random install ID, and **never health values in events**. Add an analytics opt-out in settings and say so in the "your data stays on this device" note.
- **Effort:** 1–2 days.

### 3.9 A/B-tested paywall

- **What gets gated (Pro):** AI weekly report + coach, cloud sync/backup, wearable import, advanced correlation insights, Korean cohort perks, PDF export of the 12-week report. **Never gated:** the program, checklist, Calm Score, logging, breathing pacer, basic charts.
- **Where it appears:** soft paywall after the first **weekly report preview** (show a blurred report on day 7), at the **week-4 checkpoint**, and in settings. Never on first open.
- **Tests (PostHog feature flags, one at a time, ≥300 paywall views per arm):**
  1. Annual-first vs monthly-first anchor.
  2. Trial length: 7 days vs 14 days (RevenueCat data favours longer trials for this category).
  3. Price: $29.99 vs $39.99/yr (₩33,000 vs ₩45,000).
  4. Copy: "Your coach" (outcome) vs "Unlock insights" (feature).
  5. Placement: day 7 report vs week 4 checkpoint.
- **Effort:** paywall UI + flags 2–3 days; each test ≈ 0.5 day to set up.

### 3.10 Phased milestones (weeks)

| Phase | Weeks | Milestone | Ships | Effort (solo + AI) |
|---|---|---|---|---|
| **0. Instrument** | 1–2 | Know the funnel | PostHog anonymous events; landing pages (EN/KR); lead-magnet PDF + Kit; share-result card; CSV import | 6–8 days |
| **1. First revenue, no backend** | 3–4 | First ₩/$ | Cohort payment links (Lemon Squeezy + Toss link/스마트스토어); **license-key Pro unlock** cached locally; founding-member offer | 3–4 days |
| **2. Backend foundation** | 5–7 | Opt-in cloud | Supabase: encrypted backup → accounts (magic link, Google, Apple, Kakao), RLS sync, entitlements; web push reminders | 10–12 days |
| **3. Pro value** | 7–9 | Pro worth paying for | Claude weekly report + limited coach; Oura/WHOOP OAuth import; in-app checkout + webhooks | 10–12 days |
| **4. Optimize** | 9–12 | Conversion | Paywall v1 + A/B tests; referral credits; Product Hunt / Show HN launch assets; KR Toss billing-key review started | 6–8 days |
| **5. Native (gated)** | 13–18 | Store presence | Capacitor iOS/Android, HealthKit/Health Connect, local notifications, RevenueCat IAP; store listings EN/KR | 15–20 days |

Total to Phase 4 ≈ **35–45 dev-days**, which fits the 90 days alongside ~7 h/week of content. Phase 5 starts only if the native gate criteria in 3.3 are met.

---

## 4. 90-day launch plan (week by week)

**Weekly rhythm for the founder:** Mon is planning + AI content batch; Tue–Thu build; Fri community + Reddit; Sun film + KPI review (30 min).

| Wk | Product / tech | Growth | Money | Exit criteria |
|---|---|---|---|---|
| **1** | PostHog events; EN/KR landing pages; fix onboarding friction | Set up TikTok/IG/YT/Threads/Naver; build AI content pipeline; start Reddit value-commenting | — | Funnel visible end to end |
| **2** | Lead-magnet PDF (EN/KR) + Kit sequence; share-result card | Daily shorts start (#1 "84 days on camera", #2 "rating cortisol hacks"); Naver posts 1–3 | — | 10 videos live; email capture working |
| **3** | License-key Pro unlock (cached locally) | Open **Kakao cohort #1 (free)**; first Reddit data post | Cohort payment links live | 100 activated users; 50 emails |
| **4** | CSV import (Apple Health/Oura/Galaxy); calm bug fixes | Comment-to-DM automation; KR Shorts daily | **Founding-member offer** at the week-4 checkpoint | First 10 payers |
| **5** | Supabase project; encrypted backup | Outreach to 30 micro-creators (affiliate-only offer) | Paid KR cohort #1 recruiting | 400 users; D7 measured |
| **6** | Accounts (magic link/Google/Apple/Kakao), RLS sync | Disquiet + **Show HN** soft launch | — | 30 payers |
| **7** | Web push reminders; entitlements | Reddit data post #2 (the 6-week founder log) | **Paid KR cohort #1 starts** (≤30) | 700 users |
| **8** | **Claude weekly report** (preview free, full in Pro) | First creator affiliate cohorts | EN Discord cohort open | **1,000 activated users** |
| **9** | Oura/WHOOP import; in-app checkout + webhooks | Product Hunt prep (teaser, supporters list) | — | 50 payers |
| **10** | Paywall v1 + test 1 (anchor) | **Product Hunt launch** (Tue) + Disquiet relaunch | Launch discount, 72 hours | PH top-10 of the day (stretch) |
| **11** | Referral credits; AI coach chat (capped) | Paid micro-creators only where affiliate converted ($500 cap) | Cohort #2 (KR + EN) | 75 payers |
| **12** | Paywall test 2 (trial length); KR Toss billing-key application | Founder's 84-day reveal video (#1 series finale), EN + KR | Annual-plan push to cohort #1 grads | D30 measured |
| **13** | Retro; decide on native (gate check in 3.3) | Content retro: double down on the top 2 pillars | — | **100 payers, ~$2.5–3k cumulative revenue** |

---

## 5. KPIs and targets

Definitions are anchored to the 12-week program. Targets are for the first 90 days; "good" is the bar to keep going, "great" means scale the channel.

| KPI | Definition | 90-day target (good) | Great | Notes |
|---|---|---|---|---|
| **Activation** | % of first opens who complete onboarding + log one check-in or measurement within 24 h | **≥ 45%** | ≥ 60% | No signup wall helps a lot |
| **D1 retention** | % of activated users with any log on day 1 | ≥ 40% | ≥ 50% | |
| **D7 retention** | % of activated users who log on day 7 (±1) | **≥ 25%** | ≥ 35% | Health & fitness app D7 is typically low (often ~10–20%); the cohort and checklist should beat it |
| **D30 retention** | % logging on day 30 (±2) | **≥ 12%** | ≥ 20% | Gate for going native |
| **Week-4 checkpoint completion** | % of activated users who log the day-28 measurements | ≥ 15% | ≥ 25% | Main paywall moment |
| **12-week completion** | % of activated users who log the day-84 checkpoint | **≥ 6%** (all users); **≥ 40%** (cohort members) | ≥ 10% / ≥ 60% | Lagging, first readout at ~week 13+ |
| **Email capture** | % of landing visitors who join the list | ≥ 25% | ≥ 35% | |
| **Free → paid conversion** | Payers ÷ activated users (cumulative, 90 days) | **≥ 4%** | ≥ 7% | Includes cohorts |
| **Trial → paid** | Once trials exist (weeks 9+) | ≥ 35% | ≥ 50% | RevenueCat H&F median ~40% |
| **Refund rate** | | ≤ 5% | ≤ 2% | |
| **NPS** | In-app at day 14 and day 84 | **≥ 40** | ≥ 55 | Ask "why?" in 1 line; feed into AI analysis |
| **Outcome KPI** | Median waist change of week-12 finishers | −3 cm | −5 cm | Self-reported; the product's real proof |
| **Content** | Shorts posted; median views; saves/1k views | 80 shorts; 3k median | 10k median | Leading indicator |
| **Revenue** | Cumulative by day 90 | **$2.5k** | $5k | MRR ≥ $500 entering month 4 |

North-star metric: **weekly active loggers** (users who log ≥ 3 days in a week). It predicts completion, outcomes and conversion together.

---

## 6. The "virtual company": org chart and budget

```
                              ┌─────────────────────────────┐
                              │ FOUNDER / CEO (human)        │
                              │ product, filming, final say  │
                              │ on claims, money, community  │
                              └──────────────┬──────────────┘
          ┌─────────────────┬────────────────┼────────────────┬───────────────────┐
          ▼                 ▼                ▼                ▼                   ▼
   ENGINEERING        CONTENT & GROWTH   COMMUNITY &       DATA & PRICING     TRUST & SAFETY
   (AI + founder)     (AI + founder)     SUPPORT           (AI)               (HUMAN-LED)
   • Coding agent     • Research agent   (AI + human)      • Analytics agent  • Medical advisor (MD/RD,
     (Claude Code)    • Script agent     • Support agent     (weekly KPI        contractor) ★human
   • QA/test agent    • KR localization    (FAQ, email,      memo)            • Claims reviewer
   • Code review        agent              triage)         • A/B test agent     (founder + advisor)
     agent            • Repurpose agent  • Cohort host     • Finance/tax      • Privacy/legal:
   • Release/          • Scheduler          ★human            bookkeeping        one-off lawyer ★human
     monitoring       • Thumbnail/design   (founder, later   agent            • Tax accountant
                        agent              part-time        ★human: KR tax     (세무사) ★human
                      • Creator outreach   moderator)        accountant
                        drafting agent
```

### 6.1 Roles: AI or human?

| Role | AI agent can do | Human needed for | Who |
|---|---|---|---|
| **CEO / product lead** | Drafts specs, roadmaps, competitor scans | Decisions, priorities, taste, accountability | **Founder** |
| **Engineering** | ~80% of code, tests, refactors, docs (Claude Code) | Architecture calls, security review of auth/payments/RLS, App Store submissions | Founder + AI |
| **Content production** | Research → hooks → scripts → captions → KR adaptation → repurposing → scheduling | **On-camera presence** (trust), final claims check | Founder + AI |
| **Medical / scientific advisor** | Literature summaries for review | **Must be human**: reviews program content, AI coach prompt rules, red-flag routing, monthly sample of AI reports; adds credibility for press/creators | **Contract MD (endocrinology/family medicine) or registered dietitian**, 4–6 h/month |
| **Community / cohort host** | Daily prompts, FAQ answers, recap posts, sentiment summaries | Live Q&A, empathy, moderation of sensitive topics (eating disorders, anxiety) | Founder → part-time moderator when > 3 cohorts |
| **Customer support** | 80–90% of tickets (refunds policy, how-tos) | Escalations, refunds, data-deletion requests | AI + founder |
| **Growth analytics / pricing** | Weekly KPI memo, A/B test analysis, cohort curves | Choosing tests and prices | AI + founder |
| **Creator partnerships** | Finding creators, drafting outreach, tracking | Relationship calls, negotiation | AI + founder |
| **Legal / privacy** | Draft privacy policy/terms, PIPA/GDPR checklists | **Lawyer review** before accounts and payments go live (one-off) | Contract lawyer |
| **Finance / tax** | Bookkeeping, revenue reconciliation | **세무사 (tax accountant)** for 사업자 VAT/income tax filings | Contract |
| **Design** | UI variants, store screenshots, thumbnails | Brand taste, final picks | Founder |

### 6.2 Monthly budget (USD, approx.)

| Item | Months 1–3 (launch) | Month 4–6 (scaling, if KPIs hit) | Notes |
|---|---|---|---|
| AI coding + assistant (Claude Pro/Max or similar) | $20–100 | $100–200 | The main "employee" |
| Claude API (reports, coach, content agents) | $10–30 | $50–150 | Scales with Pro users |
| Supabase | $0 | $25–35 | Pro plan when real users sync |
| Analytics (PostHog free / Plausible) | $0–9 | $0–19 | |
| Email (Kit/Beehiiv free → paid) | $0 | $30–40 | |
| Video/design (CapCut Pro, Canva Pro, VREW, ElevenLabs starter) | $30–50 | $50–70 | |
| Scheduling (Postiz/Buffer/Metricool) | $0–15 | $15–30 | |
| ManyChat (IG DM automation) | $0–15 | $15 | |
| Domain + misc (ebb domain, Kakao channel) | $2–5 | $5 | |
| Payments (Lemon Squeezy/Toss fees) | % of revenue | % of revenue | Toss one-off ₩220k signup + ₩110k/yr |
| Apple / Google developer accounts | — | $8/mo amortized ($99/yr + $25 once) | Only with native |
| **Medical advisor** (contract MD/RD, 4–6 h/mo) | $300–600 | $300–600 | Non-negotiable before paid coaching |
| Micro-creator cash fees | $0 (affiliate only) | $500–1,000 | Only proven creators |
| Part-time community moderator (KR) | $0 | $300–500 | When > 3 concurrent cohorts |
| Lawyer (privacy/terms) + 세무사 | ~$100–150/mo amortized ($500–800 one-off) | $100–150 (세무사 retainer) | |
| **Total** | **≈ $500–1,000/mo** | **≈ $1,500–2,800/mo** | Month 1–3 is mostly the medical advisor |

**Break-even check:** month-4 costs of ~$1.5k need roughly 45 annual Pro subs/month at $34.99 plus ~20 cohort seats at $29. That is reachable at ~3,000–5,000 monthly activated users with the 4% target conversion. Paid scale should start only past that point.

---

## 7. Top risks and mitigations

| Risk | Mitigation |
|---|---|
| Medical overclaim / platform takedown ("cortisol" content is under scrutiny) | Honest positioning; medical advisor; claims-check gate; never "lowers cortisol" as a promise; red-flag routing |
| Trend fades | Keep the brand on "stress belly + sleep + calm habits", with "cortisol" as a keyword rather than the identity; Korean "저속노화" framing |
| Privacy promise eroded by monetization | Free tier stays offline forever; all server features opt-in; aggregates-only AI; publish a data map |
| Solo founder burnout (ironic for a stress app) | AI pipeline, batch filming once a week, 7 h/week content cap, no daily live features |
| Low PWA retention on iOS (no push unless installed) | Install prompt at the right moment; email + Kakao cohort as the retention layer; native build gated on data |
| Store rejection (guideline 4.2) | Ship native only with native features (HealthKit, notifications, widgets) |

---

## Sources

**Market and trend**
- Healthline, "Cortisol face" TikTok trend: https://www.healthline.com/health-news/cortisol-face-tiktok
- 2 Minute Medicine, "TikTok's cortisol face trend meets endocrine reality": https://www.2minutemedicine.com/tiktoks-cortisol-face-trend-meets-endocrine-reality/
- W Korea, 저코르티솔 식단 trend (May 2025): https://www.wkorea.com/?p=367342
- The Bobcat Prowl, "The cortisol craze of 2026": https://thebobcatprowl.com/20613/opinion/the-cortisol-craze-of-2026
- DocCheck, Cortisol-Detox social-media hype: https://www.doccheck.com/de/detail/articles/53846-cortisol-detox-und-abnehmen-was-steckt-hinter-dem-social-media-hype
- Internal: `../PLAN.md`, `../research/04-apps-and-design.md` (competitors, design principles)

**Subscription benchmarks**
- RevenueCat, State of Subscription Apps 2025: https://revenuecat.com/state-of-subscription-apps-2025
- Athletech News on RevenueCat health & fitness data: https://athletechnews.com/fitness-apps-monetizable-winner-take-all-or-most/
- SaaStr, top learnings from RevenueCat SOSA: https://www.saastr.com/the-top-10-learnings-from-revenuecats-state-of-subscription-apps/

**SEO and community**
- Interad, Naver SEO guide and VIEW algorithm: https://interad.com/en/insights/naver-seo-guide · https://interad.com/en/insights/naver-view-algorithm
- Inquivix, Korean search engines: https://inquivix.com/korean-search-engines/
- Inblog, Naver SEO glossary: https://inblog.ai/glossary/naver-seo
- Redship, Reddit self-promotion rules 2026: https://redship.io/blog/reddit-self-promotion-rules-2026
- Analytics Insight, promoting on Reddit without spam: https://www.analyticsinsight.net/business/how-to-promote-your-website-or-business-on-reddit-without-being-flagged-as-spam

**Influencer costs**
- Socially Powerful: https://sociallypowerful.com/influencer/marketing/cost
- Hootsuite, TikTok influencers: https://blog.hootsuite.com/tiktok-influencers
- DesignRush, influencer rates: https://www.designrush.com/agency/social-media-marketing/instagram/trends/influencer-rates
- Hypefy, cost of influencer marketing: https://hypefy.ai/blog/cost-of-influencer-marketing

**Email tools**
- Sender, Beehiiv vs Kit: https://www.sender.net/compare/beehiiv-vs-kit/
- Dupple, best free email tools 2026: https://dupple.com/learn/best-free-email-marketing-tools

**Tech stack and fees**
- Supabase pricing: https://supabase.com/pricing.md · MakerKit breakdown: https://makerkit.dev/blog/saas/supabase-pricing
- Lemon Squeezy fees (competitor reviews; verify on LS pricing page): https://dodopayments.com/blogs/lemonsqueezy-review · https://fungies.io/alternatives/lemon-squeezy
- Toss Payments fees: https://www.tosspayments.com/about/fee
- Claude API pricing (third-party summaries; verify on official page): https://www.morphllm.com/anthropic-claude-api-pricing · https://metacto.com/blogs/anthropic-api-pricing-a-full-breakdown-of-costs-and-integration · https://platform.claude.com/docs/en/about-claude/pricing
- PostHog pricing and Plausible comparison: https://posthog.com/pricing · https://posthog.com/blog/posthog-vs-plausible
- iOS web push requirements: https://developer.apple.com/forums/thread/732594 · https://documentation.onesignal.com/docs/web-push-for-ios
- Capacitor health plugins: https://capawesome.io/blog/announcing-the-capacitor-health-plugin/ · https://capgo.app/docs/plugins/health/getting-started/ · https://capacitorjs.com/docs/apis/health-fitness
- Oura API: https://support.ouraring.com/hc/en-us/articles/4415266939155-The-Oura-API · https://jsr.io/@pinta365/oura-api
- WHOOP API overview: https://www.thryve.health/blog/whoop-api-data-access-integration
- App store commissions: https://appbot.co/blog/app-developers-apple-google-small-business-programs/ · https://www.d-tt.nl/en/articles/app-store-commissions-how-much-do-you-pay-apple-and-google-and-how-can-you-keep-costs-down
- Korea alternative billing (Google): https://www.theregister.com/2021/10/21/google_subscription_fees/
- Epic v. Apple external links: https://www.macworld.com/article/2769359/court-orders-apple-to-allow-external-purchase-links-in-apps.html · https://www.fenwick.com/insights/publications/ninth-circuit-largely-upholds-ruling-in-epic-v-apple

*Caveats: many prices come from third-party or competitor pages and change often. CAC, conversion and retention figures are planning estimates to be replaced by measured data from week 2. Keyword volumes were not measured; verify in Naver DataLab and Google Keyword Planner. Nothing here is legal or tax advice.*
