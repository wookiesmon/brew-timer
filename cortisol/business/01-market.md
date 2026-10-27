# 01 — Market Intelligence: Ebb

*Monetization division · Market Intelligence team · researched 2026-10-27*

Product: **Ebb**, a free, private, offline PWA that runs a 12-week program to lower stress and cortisol-related habits and reduce belly fat. It includes a daily checklist with a Calm Score, stress and sleep check-ins, weekly waist, weight and HRV logging, a breathing pacer, charts, a phased plan, and tiered supplement guidance with a medication screen. Markets in scope are the US (with the wider English-speaking world) and South Korea.

> **How to read the numbers.** Market-research firms define these categories very differently, so 2025 estimates for the same "market" can differ by 10x. Each figure below names its source and scope. Most benchmark figures come from secondary write-ups of RevenueCat, Adapty and Sensor Tower reports, because the primary pages could not be fetched from this environment. Treat them as directional. The competitor feature survey is in `../research/04-apps-and-design.md` and is not repeated here.

---

## 1. Market size

### 1.1 Third-party category estimates (global)

| Category | 2025 size | Growth | Source / scope |
|---|---|---|---|
| Mental-health apps (stress management is called the fastest-growing segment) | $8.5–10.0B | ~14–16% CAGR | Roots Analysis ($8.54B 2025 → $33.5B 2035); MRFR ($10.0B); Grand View ($17.5B by 2030, 14.6% CAGR). Includes B2B and clinical. |
| Workplace stress management (B2B) | $5.4B | 8.8% CAGR | MRFR, to $11.6B by 2034 |
| Weight-loss apps (narrow) | $1.0–1.8B | ~17% CAGR | Coherent ($0.99B → $3.05B 2032); Reportprime ($1.80B → $5.57B 2032) |
| Diet & nutrition apps (broad) | $6.1–14.1B | 17–20% CAGR | Roots ($6.13B); TBRC ($14.06B) |
| **Health & fitness app consumer spending (in-app purchases, actual)** | **$4.5B** (+13% YoY) | downloads flat (+0.8%, 3.96B installs) | Sensor Tower 2025, via secondary sources. The US is more than 50% of category spend and the UK about 8%. |
| US wellness spend (all categories) | >$500B | 4–5%/yr | McKinsey Future of Wellness 2025. Gen Z and Millennials over-index; sleep is the top priority. |
| Ashwagandha, US mainstream retail (cortisol-adjacent supplement) | $144.5M (+13.8%) | — | American Botanical Council, Sept 2025 |
| Korea digital health | $1.6B–$10.8B | 14–24% CAGR | MarketsandMarkets vs IMARC (scope differs) |
| Korea health functional foods (건강기능식품) | ₩5.96조 (~$4.3B) | 5–10%/yr historically | Korea Health Supplements Association, via Segye, May 2026 |

The Sensor Tower IAP figure is the most reliable proxy for real money changing hands: about **$4.5B/yr in consumer app spend** in health and fitness. The "cortisol/stress + belly fat" intersection is a slice of that plus part of meditation spend (Calm is estimated at roughly $300M revenue and 4M+ subscribers; Headspace at about $195M, both 2023).

### 1.2 Ebb-specific TAM / SAM / SOM (bottom-up, our assumptions)

| Layer | Definition | Estimate | Logic |
|---|---|---|---|
| **TAM** | Global consumer spend on self-pay stress, sleep and weight/metabolic apps | **~$6–7B/yr** | $4.5B H&F IAP plus roughly $1.5–2.5B of meditation/mental-wellness consumer subscriptions and web-billed programs (Noom alone was about $1B ARR in 2023, much of it web-billed) |
| **SAM** | English and Korean-speaking adults aged 30–55 who use health apps and have both stress and waist/weight goals | **~$150–250M/yr** | US: 92.4M health/fitness app users (eMarketer 2025) × ~30% with stress plus weight intent × ~4% paying × ~$50/yr ≈ $55M. Add UK/CA/AU (≈0.6× US) and Korea (≈43M adults, 34–49% obese by survey, high stress among 30–40s; assume ~4M app-engaged target × 3% paying × ~$30) ≈ $4M. Then roughly 2–3× for one-off programs, supplements affiliate and B2B. |
| **SOM (3-year)** | What an indie, unpaid-acquisition PWA can realistically capture | **$50k–$400k ARR** | 50k–250k cumulative installs/yr from organic and creator traffic × 2–4% paid × $30–45 net/yr. Only 5% of H&F apps reach $10k total revenue in their first two years (RevenueCat 2025), so even the low end is above median. |

**Implication:** the market is large and growing, but Ebb's obtainable share depends on distribution (creator/TikTok, Korean communities, SEO for "lower cortisol" queries), not on market size.

### 1.3 The "cortisol" trend: search and social evidence

| Signal | Data | Source |
|---|---|---|
| Google searches for "cortisol" | Up **more than 5x since 2020** (Google Trends) | Allara Health, Aug 2025 |
| | "Nearly doubled" from the start of 2026 to April 2026 | Scope Weekly, Apr 2026 |
| Long-tail queries | "cortisol meter" up from 30 to 9,900 searches/month (Apr 2025 → Mar 2026); "cortisol spike" up 1,041% in 6 months | Rising Trends (vendor data, unverified) |
| TikTok "cortisol mocktail/cocktail" | Views **up more than 20,000% YoY** (Spate). The drink went viral in 2023 and was still circulating in 2025. | Yahoo/Spate; Wikipedia; Hola 2025 |
| #cortisolface vs #moonface | About 2.5M vs 93.9M hashtag views (undated) | Face Value newsletter |
| What "cortisol" videos are about (Sept 2026) | Sleep 28%, energy 19%, skin 16%, blood sugar 13%. "Cortisol" has become shorthand for stress. | Syncly Social Index |
| Expert backlash | Healthline, Calm, Stronger By Science and German pharmacists debunk "cortisol face" and "cortisol detox" | multiple |
| New hardware | Eli Health saliva Hormometer launched Sept 2025 at **$8.25/test** (US/CA). WHOOP Advanced Labs opened to non-members at about $150 (Aug 2026). | Fitt Insider; Android Authority |

**Read:** demand is real, sustained (three-plus years) and moving from meme ("cortisol face") to measurement (saliva tests, labs, "cortisol meter"). The backlash is an opening for an *honest* product. Ebb's "behaviour index, not a cortisol reading" stance fits the direction the trend is heading.

### 1.4 South Korea snapshot

| Indicator | Data | Source |
|---|---|---|
| Adult obesity (BMI ≥25, measured) | Men **48.8%**, women 26.2% (2024). Men in their 40s: **61.7%**. | KNHANES 2024 via Newsis |
| Adult obesity (self-reported) | 34.4% (2024), up from 26.3% in 2015 | KDCA Community Health Survey |
| Stress perception rate (스트레스 인지율) | 23.7% (2024), 23.9% (2025). Peaks at **women in their 30s (41.5%)** and **men in their 40s (36.3%)**. Main drivers are work and finances. | KDCA CHS |
| Diet-app leaders | 필라이즈 (Pillyze): 1.4M+ cumulative members, #1 in App Store H&F (Jan 2026, +150k in one month). 인아웃 (InOut): about 1.4M downloads. Noom Korea: about 4M lifetime KR downloads (undated), historically #1 grossing in Google Play Health. | Money Today Feb 2026; Disquiet; JobPlanet |
| GLP-1 demand | Wegovy launched in Korea Oct 2024: **395,379 prescriptions** by June 2025. Illegal-import seizures were 4.2x the prior year. | Hankyung / BizHankook 2025 |
| Wellness culture | The **저속노화 (slow-aging)** boom: Baemin stores using the keyword rose from 8,300 to 24,500 (2021 → 2025), and 54% of consumers say blood-sugar control is the top diet factor. Fashion media frames "저코르티솔 식단" as the European counterpart. | Maeil; W Korea 2025 |
| Supplements | ₩5.96조 market; red ginseng declining, vitamins rising | KHSA |
| Gap | No public Korean MAU or willingness-to-pay data for diet or stress apps was found. Korean users skew to free and reward models (Cashwalk). Validate with 와이즈앱/모바일인덱스 before committing. | — |

**Read:** Korea has a sharper fit than the US on two axes. Men in their 30s–40s combine the highest obesity with high stress, and the slow-aging/blood-sugar culture already frames diet as calm and longevity rather than restriction. "Cortisol" as a keyword is less mainstream in Korea than in the US, so Korean positioning should lead with 저속노화, 뱃살 (belly fat) and 스트레스.

---

## 2. Competitor pricing and business models

### 2.1 Price points (US unless noted; approximate, 2025–26)

| Product | Free tier | Monthly | Annual | Trial | Other revenue lines |
|---|---|---|---|---|---|
| **Noom** (Weight) | Minimal | ~$70 | ~$209 (~$17.42/mo) | 7 days (some promos 14) | **GLP-1Rx from $129/mo; Microdose GLP-1 from $79**. About $1B ARR and 1.5M subscribers (Sacra est., 2023). Web-funnel quiz, then paywall. |
| **WHOOP** | None (hardware bundled) | — | One $199 / Peak $239 / Life $359 | — | **Advanced Labs** blood tests ($150–$299/panel; $199–$899 bundles). About $1.1B annualized bookings in 2025 (+103%), 2.5M+ members (Sacra est.). |
| **Oura** | Basic data only | $5.99 | $69.99 | 1 month | Ring $299+; Health Panels blood tests. About $1B TTM revenue and ~$11B valuation (Sacra). |
| **Calm** | Limited | $14.99–16.99 | ~$69.99–79.99 (price rise Feb 2026) | 7 days | Calm Sleep Premium $69.99/yr (Sept 2025); Calm Business/Health (B2B). About $300M revenue (2023 est.). |
| **Lumen** | No (device required) | ~$19 after the initial plan | Bundles $199–$349 incl. device | — | **Hardware** CO2 breath device |
| **Zero** | Yes (timer) | $9.99 | $69.99 (launch offer $49.99); some users see annual-only | 7 days | Plus adds coaching content and a protein score |
| **Welltory** | Yes (measurements) | — | $99.99–$119.99 (Plus/Premium; EU €79.99–99.99) | Yes | CEO cites $99/yr. Raising up to $30M (2026). |
| **Bevel** | Yes; tracking free since Dec 2025 | $5.99 → $14.99 | $49.99 → $99.99 | Yes | Pro = AI coach, health records, biological age |
| **Blueprint / Don't Die** (Bryan Johnson) | App free | — | — | — | **Supplements and food**: launched at $333/mo plus a $999 entry (2024); reportedly break-even (2025, unverified). The app is a funnel to products. |
| **Eli Health** | — | — | — | — | **Consumables**: $8.25 per saliva cortisol test, subscription |
| Midlife women's telehealth (Alloy, Evernow) | — | $40–49 + Rx | $50/yr fee (Alloy) | — | Cash-pay hormone care; Midi (insurance) $1B+ valuation |
| Korea: 필라이즈, 인아웃, 눔 | Generous free | (KR prices not verified) | — | — | Pillyze and InOut monetize through **commerce** (healthy food, supplements) as much as subscriptions |

### 2.2 How the money is made: five models

1. **Hardware + membership** (WHOOP, Oura, Lumen): $70–$360/yr recurring on top of a $199–$400 device. Highest ARPU, but a large capital and inventory burden.
2. **Labs and consumables** (WHOOP Advanced Labs, Oura Health Panels, Eli Health): blood or saliva testing is the newest upsell layer, priced $8–$300 per test. It turns "measure stress" into a recurring purchase.
3. **Coaching / Rx escalation** (Noom → Noom Med GLP-1): a $17–70/mo app ladders into $79–199/mo prescription programs. That is where Noom's growth now comes from.
4. **Supplements/commerce** (Blueprint, Korean diet apps): the app is the free funnel and products carry the margin. Bryan Johnson's experience shows that supplement D2C can still end up only break-even.
5. **Pure software subscription** (Calm, Zero, Welltory, Bevel): $50–120/yr, freemium plus trial. Bevel's December 2025 move to free tracking shows how hard pure-software tiers are being squeezed.

### 2.3 Conversion, retention and LTV benchmarks (health & fitness)

| Metric | Benchmark | Source |
|---|---|---|
| Install → paid (median) | **~3.8–4.2%** (top 10% ≈ 12%) | Adapty 2025 H&F |
| Freemium vs hard paywall install → paid | **2.18% freemium** vs 12.11% hard paywall (median) | Adapty |
| Paywall view → trial | ~11% median | Adapty 2025 (secondary) |
| Trial → paid | **39.9% median, 68.3% top decile** (RC 2025); **37.7% median, >51.4% top quartile** (RC 2026); 35% (Adapty 2026) | RevenueCat / Adapty |
| Trial length | 17–32-day trials convert best (45.7% median) vs ≤4 days (26.8%). 3–7-day trials have the most Day-0/1 cancels. | RevenueCat 2025 |
| Value before paywall | Showing value before gating gives 1.5–2x trial → paid vs an immediate hard paywall (agency claim) | RC 2025 via RocketShip |
| iOS vs Android | H&F conversion about 2x higher on iOS | Athletech (RC 2025) |
| Early cancellation | 30% of annual subscribers cancel (turn off auto-renew) within the first month | RevenueCat 2025 |
| Annual renewal (yr 1 → yr 2) | **Median 25%** (lower quartile 16%, upper 37%) | RevenueCat 2026 renewal benchmarks |
| Monthly plan 12-month retention | ~17% | Adapty 2025 |
| Monthly churn (consumer subs, general) | ~6.5%/mo; fitness ~7.2% (unverified) | Recurly 2024; Focus Digital |
| Revenue mix | ~59–68% of H&F revenue comes from annual plans | RevenueCat 2026 (figures conflict) |
| Revenue per install | $0.48 at D14 (RC 2026); $0.63 at D60 (RC 2025). H&F is the highest of any category. | RevenueCat |
| LTV | Realized LTV per payer after 1 month: **$24.23 median**, >$39 top quartile (RC 2026). 1-year install LTV $1.21 median (Adapty 2026). Trials raise annual-plan LTV in H&F. | RevenueCat / Adapty |
| Success distribution | Only **5%** of H&F apps reach $10k total revenue within two years | RevenueCat 2025 |
| Common price anchors | $9.99/mo; $29.99–$69.99/yr; mid-market H&F $59.99–$89.99/yr | RC 2024 via Eka VC; AppsOps |

**What this means for Ebb:** a 12-week program is a natural fit for a **one-time or 3-month purchase**. Annual subscriptions renew at only about 25% in this category, so most annual revenue is effectively a one-off payment anyway. Ebb is a PWA, so it sits outside App Store IAP. Web checkout (Stripe/Paddle; Toss/KakaoPay in Korea) avoids the 15–30% store fee, but web-funnel conversion depends on the onboarding quiz, which is Noom's playbook.

---

## 3. Who pays: personas

### Persona A: "Wired-and-tired" midlife woman (US/global, 35–52)
- **Profile:** a professional or parent in perimenopause who has noticed new belly fat despite "eating the same". She follows cortisol and "moon face" content on TikTok and Instagram and already buys magnesium and ashwagandha.
- **Pain:** "Dieting harder makes it worse." She is burned out on calorie counting and wants a calm, structured plan with visible proof (waist going down).
- **Evidence of spend:** midlife cash-pay care at $40–50/mo (Alloy, Evernow); Noom's $17–70/mo; the supplement habit; Gen Z/Millennials drive 41% of US wellness spend.
- **Willingness to pay:** **$30–60 for the full 12-week program** (one-time) or $8–10/mo. She is a natural buyer for a curated supplement or lab add-on. This is the highest-intent segment and should be the primary US target.

### Persona B: "영포티" Korean office worker (KR, men 33–49; women in their 30s as secondary)
- **Profile:** a salaried worker with long hours, after-work drinking and a sedentary commute. Belly fat is flagged at the company health check (건강검진). 61.7% of men in their 40s are obese and stress perception peaks for men in their 40s (36.3%) and women in their 30s (41.5%).
- **Pain:** has tried diet apps and quit logging. He is attracted to 저속노화 and blood-sugar framing and is interested in Wegovy but not prescribed it.
- **Willingness to pay:** low for subscriptions (the Korean market defaults to free, rewards and commerce). **₩9,900–19,900 one-time program** or ₩4,900/mo. Better monetized through **B2B/employer wellness** (EAP, insurer programs) and Korean health-supplement affiliates. The bilingual UI is a moat here.

### Persona C: Quantified-self wearable owner (US/KR, 28–45, mostly male)
- **Profile:** already pays for WHOOP, Oura, Garmin or Apple Watch, sees HRV and "stress" numbers daily, and doesn't know what to *do* about them.
- **Pain:** wearables describe but don't prescribe. He wants a protocol that links HRV and RHR to his waist.
- **Evidence of spend:** $70–$360/yr memberships, $150–300 lab panels, $8.25 saliva tests.
- **Willingness to pay:** **$20–40/yr add-on**, or a one-time $15–25 "protocol pack". He is price-tolerant but feature-demanding (Apple Health/CSV import, HRV trend charts). He is a strong word-of-mouth and Reddit channel.

---

## 4. The three most defensible positioning angles

### 1. "The honest cortisol program": evidence over hype
The cortisol trend is huge, but its credibility is collapsing under expert debunking ("cortisol face", "cortisol detox"), and new apps overclaim (CalmTide and Cortisol+ present estimates as measurements). Ebb is explicit that the Calm Score is a behaviour index, not a cortisol reading. It ships tiered, evidence-graded supplement guidance and a **medication-safety screen** that no consumer cortisol app offers. That trust is hard to copy without rebuilding content and taking on liability. It also positions Ebb as the safe partner for creators and clinicians who want to ride the trend without embarrassment. *Tagline direction: "Calm your stress system, not your feed."*

### 2. Private, offline, hardware-optional: the anti-wearable
Every physiology competitor requires a device plus a subscription ($70–360/yr, plus $150–300 labs). Ebb works with a tape measure and accepts HRV typed in from any device or none. It has no account and no server, so the data never leaves the phone. That matters for stress and weight data, for Korean PIPA-sensitive users, and in a post-Flo privacy climate. It also gives Ebb near-zero marginal cost per user, so it can stay **free at the core** while competitors (Bevel going free in Dec 2025) race toward freemium. This angle is structurally defensible because venture-funded rivals monetize data, devices or labs and can't easily follow.

### 3. Waist-first, 12-week, time-boxed outcome: calm *and* belly fat in one plan
No product joins stress physiology, a waist-circumference outcome and a finite phased program. Calm apps measure nothing physical, fat-loss apps add restriction stress, and wearables never end. A 12-week arc matches how people buy transformation (a "program", like Noom's quiz funnel and GLP-1 courses). It fits the benchmark data: annual renewals are only about 25% in H&F, so a **one-time program purchase** captures most of the value honestly. It also translates cleanly to Korea as "12주 뱃살·스트레스 리셋", riding 저속노화 rather than the less-known "cortisol" keyword. It can extend into sequels (maintenance phase, perimenopause edition, couples or workplace cohorts).

**Angles to avoid:** claiming cortisol measurement (regulatory and trust risk), competing on content volume with Calm, or competing on GLP-1 (medical, capital-intensive).

---

## 5. Sources

**Market size**
- Mental-health apps: https://www.rootsanalysis.com/reports/mental-health-apps-market.html · https://www.marketresearchfuture.com/reports/mental-health-apps-market · https://www.giikorea.co.kr/report/grvi1679420-mental-health-apps-market-size-share-trends.html · https://m.giikorea.co.kr/report/grvi1633783-workplace-stress-management-market-size-share.html
- Weight-loss / diet apps: https://www.reportprime.com/weight-loss-app-r11156.md · https://www.gii.co.jp/report/coh1671891-exercise-weight-loss-apps-market-by-type-by.html · https://www.rootsanalysis.com/reports/diet-and-nutrition-apps-market.html · https://cn.gii.tw/report/tbrc1849263-diet-nutrition-apps-global-market-report.html
- H&F consumer spend: https://sensortower.com/blog/state-of-mobile-health-and-fitness-in-2025 · https://voxbooster.com/blog/fitness-app-statistics-2026
- US users: https://www.emarketer.com/content/consumers-use-mobile-apps-track-fitness-health
- McKinsey wellness: https://europeanspamagazine.com/mckinsey-reveals-the-future-of-wellness-report-2025/ · https://www.leisureopportunities.co.uk/news/McKinsey-Report-Younger-demographics-are-changing-the-US2-trillion-global-wellness-industry/355965
- Ashwagandha: https://www.supplysidesj.com/supplements/ashwagandha-goes-mainstream-in-u-s-as-sales-boom · https://www.researchandmarkets.com/reports/6036428/ashwagandha-supplements-market-global-industry
- Calm/Headspace: https://www.businessofapps.com/?p=60332 · https://sacra.com/c/calm · https://businessofapps.com/?p=60411

**Cortisol trend**
- https://www.allarahealth.com/blog/stop-stressing-about-stress-the-role-of-cortisol-in-your-health · https://www.scopeweekly.com/2026/04/overwhelmed-stressed-burnout-cortisol-levels-what-google-searches-reveal-about-americans-in-2026 · https://www.risingtrends.co/blog/cortisol-meter-trend · https://www.yahoo.com/lifestyle/chronic-stress-rise-cortisol-mocktails-060000769.html · https://syncly.app/social-index/trends/cortisol-2026-09 · https://facevaluenewsletter.substack.com/p/tiktok-translator-moon-face-cortisol · https://en.wikipedia.org/wiki/Cortisol_cocktail · https://www.healthline.com/health-news/cortisol-face-tiktok · https://www.calm.com/blog/cortisol-face · https://www.strongerbyscience.com/?p=59978 · https://www.nutraingredients.com/Article/2025/05/05/top-supplement-trends-according-to-google-tiktok/

**Korea**
- Obesity/stress: https://www.newsis.com/view/NISX20250930_0003349661 · https://www.koreaherald.com/article/10586856 · https://www.koreajoongangdaily.com/korea/more-than-half-of-korean-men-in-their-30s-to-50s-are-obese-survey-finds/12899075 · https://www.kdca.go.kr/bbs/kdca/42/240811/download.do · https://medigatenews.com/news/47938752
- Diet apps: https://www.mt.co.kr/future/2026/02/16/2026021316172476103 · https://disquiet.io/articles/EosA9g · https://www.jobplanet.co.kr/companies/89218/landing/눔코리아 · https://apps.apple.com/KR/app/id634598719
- Wegovy: https://www.hankyung.com/article/2025082588007 · https://www.bizhankook.com/articles/32464.html · https://www.khan.co.kr/article/202410260900001
- 저속노화 / 저코르티솔: https://www.imaeil.com/page/view/2025052514414112584 · https://www.wkorea.com/?p=367342 · https://v.daum.net/v/20250511060111822?f=p
- Supplements / digital health: https://www.segye.com/newsView/20260527511692 · https://www.ceoscoredaily.com/page/view/2024021614310940082 · https://www.marketsandmarkets.com/Market-Reports/geography/digital-health-market/South-Korea · https://www.imarcgroup.com/report/en/south-korea-digital-health-market · https://www.koreatimes.co.kr/business/companies/20260806/korean-app-store-spending-topped-268-bil-in-2025-apple

**Competitor pricing / models**
- Noom: https://www.noom.com/plans · https://sacra.com/c/noom · https://healthrx.com/brands-noom/pricing-analysis · https://www.pharmaceuticalcommerce.com/view/noom-microdose-glp-1-program-reduce-side-effects-boost-affordability
- WHOOP: https://sacra.com/c/whoop/ · https://www.thepricer.org/how-much-does-whoop-advanced-labs-cost/ · https://androidauthority.com/whoop-drops-membership-for-advanced-labs-3699949 · https://www.emarketer.com/content/whoop-opens-lab-testing-non-members-creating-new-customer-funnel
- Oura: https://www.thepricer.org/how-much-does-the-oura-ring-cost/ · https://sacra.com/research/whoop
- Lumen: https://www.wareable.com/health-tech/lumen-review · https://www.garagegymreviews.com/equipment/lumen
- Zero: https://apps.apple.com/us/app/-/id1168348542 · https://www.apkmirror.com/?p=1244182
- Welltory: https://ionanalytics.com/insights/mergermarket/welltory-could-raise-up-to-usd-30m-this-year-for-ai-health-data-app-ceo/ · https://apps.apple.com/app/welltory-heart-rate-monitor/id1074367771
- Bevel: https://apps.apple.com/us/app/bevel-all-in-one-health-app/id6456176249 · https://askvora.com/blog/bevel-pricing-is-bevel-free-2026
- Blueprint: https://fortune.com/2024/01/10/bryan-johnson-blueprint-anti-aging-subscription · https://www.builtbyfoundry.io/blog/bryan-johnson-800m-exit-break-even-blueprint · https://en.wikipedia.org/wiki/Bryan_Johnson
- Eli Health: https://insider.fitt.co/press-release/eli-health-expands-saliva-based-hormone-platform-hormometer-with-real-time-tests-for-testosterone-and-progesterone/ · https://www.wareable.com/ces/eli-healths-hormometer-tracks-crucial-hormones-from-saliva
- Midlife care: https://sacra.com/c/midi-health/ · https://femtechinsider.com/midi-health-raises-100-million-series-d-surpasses-1-billion-valuation/

**Conversion / retention benchmarks**
- RevenueCat: https://www.revenuecat.com/state-of-subscription-apps · https://www.revenuecat.com/state-of-subscription-apps-2025 · https://www.revenuecat.com/blog/growth/average-subscription-renewal-rates-by-app-category · https://athletechnews.com/fitness-apps-monetizable-winner-take-all-or-most/ · https://subscriptioninsider.com/article-type/news/revenuecats-state-of-subscription-apps-2025-report-ais-dominance-retention-challenges-and-the-shift-away-from-pure-subscriptions · https://sahha.ai/blog/health-app-monetization-first-month/ · https://arpubrothers.com/blog/revenuecat-subscription-app-report-2026/ · https://www.rocketshiphq.com/?p=5592
- Adapty: https://adapty.io/blog/health-fitness-app-subscription-benchmarks/ · https://adapty.io/blog/freemium-to-premium-conversion-techniques · https://adapty.io/blog/state-of-in-app-subscriptions-2025-in-10-minutes/
- Pricing anchors / churn: https://ekavc.substack.com/p/taking-the-pulse-on-consumer-apps · https://techcrunch.com/2024/03/12/most-subscription-mobile-apps-dont-make-money-new-report-shows/ · https://appsops.store/blog/health-fitness-app-subscription-pricing-2026 · https://eightx.co/blog/dtc-subscription-churn-index-2026 · https://focus-digital.co/average-churn-rate-subscription-services
