# 03 · Legal & Compliance: Ebb

*Prepared by the Legal & Compliance workstream, 27 October 2026.*

> **Not legal advice.** This is a research summary to help plan the work and brief a lawyer. It is not a legal opinion. Laws, guidance and platform rules change often, and several items below say "verify" because the official text could not be read directly during research. Before launch, have a licensed attorney in each market (US, EU and Korea) review the product, the claims and the contracts. Have a licensed clinician review the health content.

**Research note.** Some official sites (fda.gov, some Korean news and law-firm sites) could not be reached from the research environment. Where that happened, this document relies on law-firm or press summaries and says so. Those points are marked **(verify)**. Check them against the primary text.

---

## 0. Summary

**Where Ebb stands today.** Ebb is a local-only web app (PWA). It sells nothing, sends no data anywhere, and already includes a good disclaimer ("The Calm Score ... is not a cortisol test"). That puts it at low regulatory risk. Monetization raises the risk in four places at once:

| # | Top risk | Why it matters | Trigger |
|---|---|---|---|
| 1 | **Disease and drug wording plus doses**: Tier 3 doses for insulin resistance and PCOS, "GLP-1/metformin work far better", lab re-check schedules | Turns a wellness app into disease management. That raises medical-device and CDS questions under FDA, EU MDR and MFDS rules, and unlicensed-practice questions in Korea (의료법). | Now. Fix before any public launch. |
| 2 | **Supplement claims combined with affiliate links** ("lowers cortisol", "1–3 cm off the waist") | Once Ebb earns money from a product it recommends, every efficacy statement becomes advertising. That requires RCT-level substantiation (FTC), affiliate disclosure, and in Korea, food and 건강기능식품 ad rules. | Affiliate launch. |
| 3 | **Health data leaves the device** (accounts, AI coach, B2B, wearables) | Triggers the FTC Health Breach Notification Rule, Washington's MHMDA (private right of action), GDPR Art. 9 and PIPA Art. 23. Health data in ad SDKs is what drew the GoodRx and BetterHelp penalties. | Cloud sync or AI coach. |
| 4 | **The AI coach gives individualized medical-sounding advice or misses a crisis** | Raises device and practice-of-medicine risk and harm and liability risk. State AI mental-health laws (IL, NV, UT, CA) apply, as do the EU AI Act Art. 50 transparency duties, in force since 2 Aug 2026. | AI coach launch. |
| 5 | **Subscription dark patterns** | California's ARL (amended 1 July 2025), ROSCA, NY law, EU/German cancel-button rules, and Korea's 2025 전자상거래법 dark-pattern rules. Common source of class actions. | Paid launch. |

---

## 1. Is Ebb a medical device or SaMD?

### 1.1 United States (FDA)

- **The test.** Software is a device if it is *intended* to diagnose, cure, mitigate, treat or prevent disease, or to affect the structure or function of the body (FD&C Act §201(h)). The 21st Century Cures Act §3060 excludes software meant to maintain or encourage a healthy lifestyle, as long as it is unrelated to the diagnosis, cure, mitigation, prevention or treatment of a disease or condition. Intended use is judged from labeling, marketing, app-store text, ads and the AI coach's outputs.
- **General Wellness guidance.** FDA issued an updated final guidance, *General Wellness: Policy for Low Risk Devices*, on **6 January 2026**. It replaces the September 2019 version, which replaced the 2016 version. It keeps the two wellness categories:
  1. claims about maintaining or encouraging general health, such as weight management, physical fitness, relaxation or **stress management**, sleep, and mental acuity, with no reference to disease; and
  2. claims linking a healthy lifestyle to **reducing the risk of, or helping people live well with, a chronic disease or condition**, where it is well understood that a healthy lifestyle plays an important part. An example is "may help reduce the risk of type 2 diabetes".
  The products must also be low risk (non-invasive, not implanted, no novel risk to safety).
  **New in 2026:** some products that use *non-invasive sensing* to estimate physiologic parameters can stay in the wellness category under certain conditions. Disease-related claims still take a product out of it. **(verify** the exact conditions in the FDA text; summaries say the values must not be meant for clinical diagnosis or management.)
- **Clinical Decision Support guidance, also updated 6 Jan 2026.** The CDS exemption covers software for **health-care professionals** who can independently review the basis of a recommendation. An AI coach for **patients or consumers** does not qualify for that exemption. If it makes disease-specific recommendations, it falls back on device analysis. The coach therefore has to stay inside the wellness category.
- **Applied to Ebb:**

| Feature | Wellness or device? | Note |
|---|---|---|
| Calm Score (habit and self-report index) | Wellness | Keep the "not a cortisol test" language. Never present it as a physiologic estimate. |
| Logging waist, weight, HRV and stress; charts | Wellness | General fitness and stress management. |
| PSS-10 questionnaire | Wellness if framed as "track how stressed you feel" | Do not label results as anxiety or depression screening, or give diagnostic cut-offs. |
| Breathing exercises | Wellness (relaxation and stress management) | Avoid "treats anxiety" or "lowers blood pressure". |
| **"Estimated cortisol" from HRV or wearables** (do not build) | **Likely device**: estimates a hormone level that is used clinically | Even under the 2026 sensing policy, a cortisol estimate tied to Cushing's or adrenal conditions points toward diagnosis. |
| Supplement list with doses and a medication-exclusion screen | Mostly not a device issue (food and supplement information). The **risk** is practice of medicine and FTC claims. | Conservative exclusion ("hide if you take X") is safer than personalized dosing. |
| Tier 3 berberine for insulin resistance, myo-inositol for PCOS, GLP-1/metformin comparison | **Disease treatment content** | Remove doses and condition-specific advice. See §1.5. |
| Lab test list and "re-check ALT/TSH at weeks 6–8" | Gray area: monitoring advice | Reframe as "questions to ask your doctor". Do not interpret results. |
| "See a doctor if..." red flags | Fine and encouraged | Referral is not diagnosis. Phrase it as "can have medical causes; a doctor can check". |
| AI coach reading logs | Wellness **only if** constrained (see §4) | Disease triage, dose changes and lab interpretation would cross the line. |

### 1.2 European Union (MDR 2017/745)

- **Definition** (MDR Art. 2(1)): software with a medical purpose (diagnosis, prevention, monitoring, prediction, prognosis, treatment or alleviation of disease) is a device. **MDR Recital 19** says software for **lifestyle and well-being purposes** is not a medical device.
- **MDCG 2019-11 Rev.1 (June 2025)** is the qualification and classification guidance. Qualification depends **only on the intended purpose** stated by the manufacturer. Under **Rule 11**, most medical-purpose software is Class IIa or higher. That means a notified body, a QMS (ISO 13485) and clinical evaluation, typically **€100k+ and 12–18 months**. For a startup, the wellness framing is not optional.
- **Words that cross the line in the EU:** "monitor your cortisol", "prevent metabolic syndrome", "manage PCOS", "reduce visceral fat to prevent diabetes" (prevention of a specific disease), and "detects burnout or depression".
- **Supplements in the EU** fall under the **Nutrition & Health Claims Regulation (EC) 1924/2006**. Only claims on the EU Register are allowed. For example, magnesium "contributes to a reduction of tiredness and fatigue" and "to normal psychological function" are authorised. Ashwagandha "reduces stress or cortisol" is **not** authorised. EU affiliate copy must use register wording only.

### 1.3 Korea (MFDS / 식약처, Ministry of Health and Welfare / 보건복지부)

- **「의료기기와 개인용 건강관리(웰니스)제품 판단기준」** has been in force since July 2015 and revised since. Classification depends on **intended use (사용목적)**, judged from the manufacturer's specs, instructions and marketing, and on **risk (위해도)**. Low-risk products for maintaining or improving health, including lifestyle guidance for people with chronic conditions that does not change treatment, are wellness products. Products that diagnose, treat or claim disease effects are medical devices. Press reports describe example cases such as personalized information for **stress relief**, **diet information for weight management**, and lifestyle recommendations for people with hypertension. **(verify** the latest revision on the MFDS site.)
- **디지털의료제품법** (Digital Medical Products Act) took effect on 24 Jan 2025. Its **second phase on 24 Jan 2026** started the **디지털의료·건강지원기기** (digital health-support device) scheme. It includes a scope designation, **voluntary self-declaration (자율신고) and information disclosure**, **voluntary performance certification (성능인증)**, and **control of false or exaggerated advertising**. The first designated products measure or analyse heart rate, SpO2, body composition and step count. **Exercise, diet and mental-health products are planned next.** Samsung Health was the first registration. If Ebb later integrates wearable HR/HRV in Korea, check whether it falls in a designated category. Certification is optional but can be a marketing asset.
- **의료법 Art. 27 (unlicensed medical practice)** and the **「비의료 건강관리서비스 가이드라인」** (MoHW, 2019, with later case books) are separate from device law. Under them, non-medical providers may do things like BMI calculation, body-composition analysis and exercise goal-setting. **Medical examination, prescription, or medical consultation and advice** is a 의료법 violation. A Korean AI coach must not judge disease, adjust medication or interpret labs.

### 1.4 Wording that crosses the line

| Crosses the line (avoid) | Why |
|---|---|
| "Lowers cortisol" / "reduces cortisol levels" / "cortisol-balancing" | Implies a measured hormonal effect. Hard to substantiate for an app, and reads as hormone therapy in KR/EU. |
| "Estimates your cortisol" / "cortisol score" | Physiologic estimate of a clinical biomarker. Device-like. |
| "Treats / cures / reverses" anything; "for insulin resistance / PCOS / Cushing's / anxiety / depression" | Disease claims. |
| "Berberine 500 mg 2–3× daily for insulin resistance"; "myo-inositol 2 g for PCOS" | Disease dosing. Practice of medicine plus a drug-like claim. |
| "GLP-1 drugs / metformin work far better" | Prescription-drug comparison. Becomes promotional if any telehealth or affiliate tie-in exists. |
| "Recheck ALT and TSH at weeks 6–8" | Clinical monitoring instruction. |
| "Burns belly fat" / "melts visceral fat" / guaranteed cm loss | Unsubstantiated weight-loss claim (FTC). Korea treats it as exaggerated advertising. |
| "Clinically proven" (for the app) | Requires trials of the app itself. |

### 1.5 Safe-language rewrites

| Current or likely wording | Safer rewrite |
|---|---|
| "12-Week Cortisol & Belly-Fat Plan" (PLAN.md title) | "12-week stress-reset and waistline habit plan" |
| meta: "A private, offline 12-week program to lower stress and shrink belly fat." | "A private, offline 12-week habit program for feeling calmer and working toward a healthier waistline." |
| "Fix the foundations that drive cortisol: sleep, light, walking, and food quality." | "Fix the foundations of stress recovery: sleep, light, walking, and food quality." |
| "Alcohol raises cortisol and wrecks sleep" | "Alcohol disrupts sleep quality, even in small amounts." |
| "Overtraining raises cortisol" | "Too much hard training without recovery can leave you more tired and stressed." |
| Supplement subs, e.g. "Ashwagandha 300 mg breakfast + 300 mg dinner · ALT/TSH check" | "Studied amount: 300 mg twice daily (KSM-66). Ask your doctor or pharmacist before starting, especially with thyroid, liver or autoimmune conditions." Frame doses as "amounts used in studies or on the label", not instructions. |
| Tier 3 block with doses | "Some people ask their doctor about berberine, myo-inositol, melatonin or prescription options. These are medical decisions; we don't give doses for them." |
| "Prescription GLP-1 drugs or metformin work far better..." | Delete. If needed: "If lifestyle changes aren't enough, a doctor can discuss medical options." |
| "Recheck liver tests (ALT) and TSH at weeks 6–8 if you started ashwagandha" | "If you take ashwagandha, ask your doctor whether liver or thyroid checks make sense for you." |
| "Blood tests: baseline and week 12" (list incl. AM cortisol) | "Tests you might discuss with your doctor". Keep the list, drop the instruction to draw them, and never interpret results in the app. |
| "These are possible signs of Cushing's syndrome." | "These can have medical causes, including hormone conditions. Please see a doctor." This is acceptable now; keep the referral. |
| "Supplements ... at best about 1–3 cm of waist" | Fine as a cautious educational statement with a citation. Remove it from any page that carries affiliate links unless counsel signs off on the substantiation. |
| Calm Score | Keep: "A habit-and-feeling index. Not a medical measurement and not a cortisol test." |
| AI coach persona | "Ebb Coach is an AI wellness assistant, not a doctor, and can make mistakes." |

---

## 2. Health and advertising claims

### 2.1 FTC (US)

- **Health Products Compliance Guidance (Dec 2022).** It replaced the 1998 supplement guide and covers **all** health claims, apps included. Claims need **competent and reliable scientific evidence**, generally **RCTs** that are statistically significant and clinically meaningful, on the same ingredient, dose and population. Qualifiers like "may help" do not cure weak evidence. Animal, in-vitro and observational data are usually not enough. Testimonials can't say what the advertiser couldn't.
- **Endorsement Guides (16 CFR 255, revised 2023).** Affiliate commissions are a **material connection**. The disclosure must be **clear and conspicuous**: near the link, unavoidable, and in plain words ("We earn a commission if you buy through these links"). A footer link to a policy page is not enough. Influencer and UGC campaigns need the same.
- **Consumer Reviews and Testimonials Rule (16 CFR 465, effective 21 Oct 2024).** It bans fake or AI-generated reviews, buying reviews, and suppressing negative reviews. Civil penalties exceed **$50k per violation** (inflation-adjusted yearly). Never seed app-store or landing-page reviews.
- **Weight-loss claims** are a long-time FTC priority. Results claims ("lost 8 cm") must be typical or clearly qualified with what users generally achieve.

### 2.2 Supplement structure/function claims (FDA, DSHEA)

- A supplement *seller* may make structure/function claims ("supports a normal stress response", "supports relaxation"). They must notify FDA within **30 days** (21 CFR 101.93) and carry the disclaimer: "*These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease.*" Disease claims ("reduces anxiety") make the product an unapproved drug.
- Ebb is a **publisher or affiliate**, not the seller. Its copy is still advertising when it earns commissions. **Policy:** use only structure/function language, never disease language, near affiliate links; add the FDA disclaimer; and link only to USP- or NSF-verified products (as the app already advises).

### 2.3 Korea

- **식품표시광고법 (Act on Labeling and Advertising of Foods), Art. 8:** food and 건강기능식품 ads may not claim to prevent or treat disease, imply medicine, claim to replace or boost medicines, imply doctor or pharmacist endorsement, or use groundless "best" claims. Allowed exceptions are approved **functional (기능성) claims** and approved disease-**risk-reduction** claims.
- **Art. 10 self-regulatory review (자율심의):** functional advertising for 건강기능식품 must be reviewed by the registered review body, the **Korea Health Supplements Association (한국건강기능식품협회)**, through ad.khff.or.kr. Media include the internet and video. If Ebb Korea runs affiliate copy that repeats functional claims, the advertiser (the brand) normally owns the review. **Ebb must use the brand's approved wording verbatim** and not add its own efficacy claims. **(verify** with Korean counsel whether affiliate publishers need separate review.)
- **Ingredient legality (verify):** check each Tier 1/2 ingredient (ashwagandha, saffron extract, specific probiotic strains, doses) against the MFDS 식품원료 list and 건강기능식품 고시. Some ingredients, or doses above the approved daily intake, may not be lawfully sold as food in Korea. Overseas direct-purchase products have been blocked for some ingredients. Korean users may need different supplement content.
- **표시광고법 (Act on Fair Labeling and Advertising) and the 「추천·보증 등에 관한 표시·광고 심사지침」 (KFTC)** require disclosure of economic interest, including commissions and paybacks, next to the endorsement, in Korean (e.g. "광고", "제휴 링크로 수수료를 받습니다"), in a size and colour that is easy to notice.

---

## 3. Privacy

### 3.1 Today: data on device only

There is no collection by the company, so most privacy laws are barely engaged. Still, publish a short privacy notice that says so and lists any analytics or CDN calls (GitHub Pages logs IPs). This also helps with app-store review.

### 3.2 United States

- **FTC Health Breach Notification Rule** (amended 26 Apr 2024, effective **29 Jul 2024**). It now expressly covers health and wellness apps that draw data from more than one source, such as user input plus a wearable API. A "breach" includes **unauthorized disclosure**, such as sharing with ad platforms without authorization, not only hacks. Required notice goes to users, the FTC and sometimes the media, within 60 days. Penalties exceed $50k per violation. It applies as soon as Ebb stores identifiable health data in the cloud **and** pulls from a wearable or other source.
- **FTC enforcement precedent:** GoodRx (~$1.5M, first HBNR case, 2023) and BetterHelp ($7.8M, 2023) were penalized for sending health data to Facebook, Google and others through pixels and SDKs. **Rule: no ad or marketing pixels on any screen that handles health data. No health data to ad networks, ever.**
- **Washington My Health My Data Act (RCW 19.373)**, in force since Mar 31 2024 (small businesses Jun 30 2024). It covers **any size** entity targeting WA consumers. It defines consumer health data broadly and includes inferences; stress, weight, HRV and supplement use all qualify. It requires **separate opt-in consent to collect** and **separate consent to share**, a **signed authorization to sell**, a standalone **Consumer Health Data Privacy Policy** linked from the homepage, deletion and access rights, and a ban on geofencing around health facilities. It carries a **private right of action** through the WA Consumer Protection Act. **Nevada (SB 370)** and **Connecticut** have similar consumer-health-data rules. **New York's NYHIPA** was vetoed in Dec 2025 and a revised bill was introduced in 2026; monitor it.
- **CCPA/CPRA (California).** It applies above thresholds (about $26.6M revenue, 100k consumers, or 50% of revenue from selling or sharing data). Health data is **sensitive personal information**, which brings a right to limit, notice at collection, and contracts with service providers. CPPA regulations on **risk assessments and automated decision-making** took effect in 2026 **(verify** dates). Other state comprehensive laws (CO, VA, TX, OR and others) generally require **opt-in consent** for health data even when CCPA thresholds aren't met.
- **HIPAA.** It does **not** apply to a direct-to-consumer app. It **does** apply when Ebb provides services **to or on behalf of a covered entity**: a health plan (including an employer's **group health plan**, for example a wellness program tied to premium discounts or HSA contributions), an insurer, or a provider. Ebb would then be a **business associate**, which means a BAA, Security Rule safeguards, breach notification and minimum-necessary access. A wellness perk paid by the employer outside the health plan is usually not HIPAA, but ADA/GINA wellness rules and HBNR/MHMDA still apply. **Never give employers individual-level data.** Report aggregates only, with a minimum cohort size of at least 10–20.

### 3.3 European Union (GDPR)

- Health data is **special-category data (Art. 9)**. The realistic lawful basis is **explicit consent (Art. 9(2)(a))**: granular, freely given, withdrawable, and separate for the AI coach and for research or analytics.
- **DPIA (Art. 35)** is required for large-scale health processing and for innovative AI. Also needed: Art. 30 records, **Art. 28 DPAs** with every processor (cloud, LLM vendor, analytics), **Art. 27 EU representative** if there's no EU establishment, and transfer mechanisms (EU-US Data Privacy Framework certification of the vendor, or SCCs plus a transfer impact assessment).
- **ePrivacy:** consent is needed for any non-essential SDK or cookie.
- **Art. 22:** avoid solely automated decisions with legal or similarly significant effects. B2B "risk scores" for employers would raise this.

### 3.4 Korea (PIPA / 개인정보보호법)

- **Art. 23 sensitive information (민감정보)** includes health data. Processing needs **separate consent (별도 동의)**, distinct from other consents, after notice of purpose, items, retention and the right to refuse. Since the 2023 amendment, users must also be told when a service might make sensitive data public, and how to keep it private.
- **Art. 22** requires itemized consent screens (required versus optional shown separately). **Art. 30** requires a published privacy policy (개인정보 처리방침). **Art. 31** requires a designated CPO. Children under 14 need guardian consent (block them).
- **Overseas transfer (Art. 28-8).** It is prohibited unless one of the exceptions applies: **separate consent**, or outsourcing or storage necessary for the contract with **disclosure in the privacy policy**, or certification or adequacy. A US cloud or LLM vendor counts as overseas transfer; disclose the country, recipient, items, timing and method.
- **Art. 31-2 domestic agent** applies to foreign businesses above revenue or user thresholds. Likely not at first, but recheck at scale.
- **PIPC 「생성형 AI 개발·활용을 위한 개인정보 처리 안내서」 (Aug 2025)** sets lifecycle safeguards for generative AI: purpose limitation, minimization, DPIA-style review, and preventing training on user data without a lawful basis. Follow it for the Korean AI coach.
- **Korea AI Basic Act (인공지능 기본법)**, effective **22 Jan 2026** **(verify** enforcement decrees): advance notice that a service uses generative AI, and labeling of AI outputs.

### 3.5 What changes when data moves off the device

| Moving to... | New obligations |
|---|---|
| **Cloud sync and accounts** | HBNR (with a second data source), MHMDA consent and policy, CCPA/state opt-in, GDPR Art. 9 consent plus DPIA, PIPA Art. 23 plus 28-8. Security program (encryption at rest and in transit, access logs, MFA, deletion), breach-response plan, data retention schedule, DSAR workflow. |
| **AI/LLM provider** | Processor DPA, **zero-data-retention / no-training** terms, region selection (EU/KR), a sub-processor list in the privacy policy, prompt minimization (send derived summaries, not raw logs or identifiers), and a BAA if HIPAA applies. Disclose the AI provider by name. |
| **Wearables (HealthKit, Health Connect, Oura, etc.)** | Apple 5.1.3 and Google Health Connect limits (no ads or marketing use), HBNR "multiple sources" coverage, per-data-type consent, and Korean 건강지원기기 scope check. |
| **Analytics and marketing** | No health events in ad pixels. Use privacy-preserving, self-hosted analytics. Keep marketing email lists separate from health data. |
| **B2B / employer** | Aggregate-only reporting, employee-facing notice that the employer can't see individual data, HIPAA/BAA if part of a health plan, a DPA with the employer, and SOC 2 expectations. |

---

## 4. AI coach

### 4.1 Risks
- **Device or CDS drift:** individualized disease advice, lab interpretation, dose titration, or "you may have Cushing's".
- **Harm:** unsafe supplement advice combined with medications, eating-disorder reinforcement (aggressive deficits, fasting), missed suicidality or self-harm (stress apps attract distressed users), overtraining with cardiac symptoms.
- **Hallucinated citations and invented evidence**, which also creates FTC substantiation exposure.
- **Commercial conflict:** a coach that recommends affiliate products looks like a deceptive endorsement. Utah HB 452 explicitly restricts advertising inside mental-health chatbots.
- **Privacy:** prompts holding health data go to a third party (see §3.5).

### 4.2 State AI mental-health laws (US)
- **Illinois Public Act 104-0054 (signed 4 Aug 2025):** AI may not provide therapy or psychotherapy, or make therapeutic decisions, without a licensed professional.
- **Nevada AB 406 (2025):** bans AI systems offering, or being marketed as, mental or behavioral health care. Up to $15k per violation.
- **Utah HB 452 (2025):** mental-health chatbots must disclose they are AI, may not sell or share user health input, and must label ads.
- **California:** SB 243 (companion chatbots: disclosure and suicide-prevention protocols) and AB 489 (AI may not imply it is a licensed health professional), both effective 2026 **(verify** applicability).
- **Practical rule:** market the coach as **habit and wellness coaching**, never "therapy", "counseling" or "mental health treatment". Consider geo-limiting coach features in IL and NV until counsel signs off.

### 4.3 Guardrails (build list)
1. **Scope system prompt plus classifier:** sleep, movement, food habits, breathing, and adherence to the plan. Refuse diagnosis, lab interpretation, medication changes, disease-specific dosing, pregnancy dosing, and minors.
2. **Red-flag escalation (deterministic, runs before the LLM):** suicidal ideation or self-harm → show **988 (US)**, **109 or 1577-0199 (KR)**, and local emergency numbers, then stop coaching. Chest pain, fainting, palpitations during training, signs of Cushing's, rapid unexplained weight loss, disordered-eating signals (very low intake, purging, BMI < 18.5), pregnancy, and new high BP or glucose readings → "please see a doctor"; no plan advice.
3. **Supplement answers only from a vetted, versioned content library** (retrieval only, no free generation of doses), respecting the in-app medication and condition flags.
4. **No affiliate links inside coach responses**, or if there are any, clear "ad" labeling and a commercial-neutral ranking policy.
5. **Disclosure:** a persistent "AI, not a doctor" label (EU AI Act Art. 50(1), Utah, CA, Korea AI Basic Act). Make the first-run consent screen specific to the coach.
6. **Logging and evaluation:** a red-team set of 300+ adversarial prompts in EN and KR, pre-release evaluation gates, monthly sampling reviewed by the medical advisor, an incident log, and a user "report this answer" button.
7. **Data minimization:** send summarized trends, not raw logs or identity. Choose a zero-retention, no-training enterprise tier.

### 4.4 EU AI Act category
- A wellness coach that is **not** a medical device is **not high-risk**. It falls under **Art. 50 transparency obligations** (inform users they are interacting with AI), which apply from **2 Aug 2026**. The 2026 AI Omnibus (Reg. (EU) 2026/1744) did not delay them. **Art. 4 AI literacy** duties have applied since Feb 2025.
- If the coach became an **MDR medical device** (Class IIa+), it would be **high-risk under Art. 6(1)/Annex I**. Under the Omnibus, obligations for AI embedded in regulated products moved to **Aug 2028** (verify). That is one more reason to stay wellness-only.

---

## 5. App stores and subscriptions

### 5.1 Apple App Store Review Guidelines
- **1.4.1:** medical apps get more scrutiny. **Health measurement accuracy claims must be validated**, and sensor-only blood pressure, glucose or SpO2 is not permitted. Apps should remind users to check with a doctor. → No "cortisol estimate"; keep the doctor reminder.
- **5.1.1(ix):** apps in **healthcare** or needing sensitive data **should be submitted by a legal entity, not an individual developer.** → Form the company before native submission.
- **5.1.3:** HealthKit, Motion and similar data may **not** be used for advertising, marketing or data mining; no false data written to HealthKit; **no personal health information stored in iCloud**; disclose the specific health data collected.
- **3.1.1 / 3.1.2:** digital subscriptions (coach, premium) must use **In-App Purchase** outside the US storefront. Auto-renewing subscriptions need ongoing value, a minimum 7-day period, and a clear description before purchase. Physical-goods affiliate links (supplements, lab kits) are outside IAP.
- **Privacy:** App Privacy "nutrition label", privacy manifest, account deletion in-app.

### 5.2 Google Play
- Complete the **Health apps declaration** in Play Console. A privacy policy covering personal and sensitive data is required. **Medical functionality needs regulatory proof or a disclaimer.** Fill in the Data Safety section. Health Connect access must be declared per data type with justification, and the Health Connect privacy policy must match. No misleading medical functionality.
- Subscriptions policy: clear terms, easy cancellation, and Play Billing for digital goods.

### 5.3 Auto-renewal and subscription law
- **US federal:** the FTC "click-to-cancel" rule was **vacated by the 8th Circuit on 8 Jul 2025**. **ROSCA** and FTC Act §5 still require clear terms, express informed consent and a simple cancellation method.
- **California ARL (amended by AB 2863, effective 1 Jul 2025):** clear and conspicuous terms before purchase, affirmative consent to the renewal terms, an acknowledgment email, **online cancellation** for online sign-ups (click to cancel), notice before free-trial conversion and price changes, and **annual reminders**. **(verify** the details.) New York and other states have similar laws.
- **EU:** 14-day withdrawal right for digital services unless the user expressly waives it on immediate start. **Germany §312k BGB "Kündigungsbutton"** (cancellation button). Unfair-terms rules.
- **Korea 전자상거래법 (effective 14 Feb 2025):** 6 dark-pattern types are banned, including **숨은갱신** (silent free-to-paid conversion or price increase without new consent and notice), drip pricing, preselected options, misleading hierarchy, **obstructed cancellation**, and repeated nagging. Before any price increase or trial conversion, get separate consent. Also 통신판매업 신고 (mail-order business registration).
- **Build once to the strictest standard:** a trial-end reminder 3–7 days before, one-tap cancel in-app and on the web, an annual reminder, and price-increase opt-in.

---

## 6. Business setup

| Item | Recommendation |
|---|---|
| **Entity** | US Delaware C-corp (if raising capital) or LLC. Needed for Apple 5.1.1(ix), insurance, contracts and liability shielding. For Korea: a 한국 법인 or branch when revenue starts, or at least **사업자등록 + 통신판매업 신고** for direct sales. |
| **Terms of Service** | Wellness-only purpose; **no medical advice, no doctor–patient relationship**; 18+ only; assumption of risk for exercise, sauna, cold and fasting; AI output disclaimer; subscription terms in line with the ARL; limitation of liability; arbitration and class-waiver (US, where enforceable); governing law; Korean-language terms for KR (약관규제법 fairness review). |
| **Privacy Policy** | General policy, plus a **WA Consumer Health Data Privacy Policy**, GDPR Art. 13 notice, PIPA 처리방침 (in Korean), and a sub-processor list with AI vendor and transfer countries. |
| **Medical disclaimer** | On onboarding (already present), the supplement screens, the coach, the labs and the store listings. Example: "Ebb is a wellness program. It does not diagnose, treat, cure or prevent any disease. Talk to your doctor before starting supplements or changing diet or exercise, especially if you are pregnant, take medication or have a medical condition. In an emergency call 911 / 119." |
| **Insurance** | **Tech E&O + cyber** (covers data breach and AI errors). **General liability** with **products and completed operations** coverage. If selling own-brand supplements later, **product liability** and a vendor's endorsement from the manufacturer. Ask the broker about AI exclusions. |
| **Medical and content governance** | Contract a **physician (endocrinology or internal medicine) plus a registered dietitian** to review all health content, supplement tiers, red-flag lists and coach evaluations. Version the content and keep a **substantiation file** (citations per claim) for FTC defence. Re-review every 6–12 months and on each feature launch. For Korea, a Korean-licensed 의사/약사 reviewer. |
| **Regulatory memo** | One-time FDA/MDR/MFDS "wellness positioning" memo from counsel, recording intended use. Useful for app review, B2B due diligence and investors. |

---

## 7. Compliance checklist by launch phase

Effort: **S** = under 1 day, **M** = 1–5 days, **L** = 1–4 weeks, **XL** = more than a month. Costs are rough 2026 US-market ranges for a small startup (external fees only, excluding staff time). Get real quotes.

### Phase A: Pre-monetization (now, free PWA)
| ☐ | Item | Effort | Est. cost |
|---|---|---|---|
| ☐ | Apply the wording changes in §8 (disease doses, GLP-1 line, cortisol phrasing, lab instructions) | S | $0 |
| ☐ | Add a medical disclaimer to the supplement, lab and plan screens and to PLAN.md (onboarding already has one) | S | $0 |
| ☐ | Add an 18+ age gate; keep the pregnancy, medication and condition screen | S | $0 |
| ☐ | Publish a simple privacy notice ("data stays on your device"; list hosting and CDN logs) | S | $0–200 (template) |
| ☐ | Medical advisor (MD + RD) review of current content, supplement tiers and red flags | M | $1.5k–5k |
| ☐ | Start a substantiation file: a citation for every health or efficacy statement | M | $0 |
| ☐ | Check trademarks for "Ebb" and "Calm Score" (USPTO/KIPRIS knock-out search). The word "Calm" may conflict with existing marks. | S–M | $0–1.5k |

### Phase B: Paid launch (subscriptions, accounts, affiliates)
| ☐ | Item | Effort | Est. cost |
|---|---|---|---|
| ☐ | Form the entity, open a bank account, get an EIN; register as a legal entity in the Apple and Google developer programs | M | $500–2k plus about $300/yr agent |
| ☐ | ToS, Privacy Policy, WA Consumer Health Data Privacy Policy, cookie/SDK policy (lawyer-drafted) | L | $3k–10k |
| ☐ | Wellness-positioning regulatory memo (FDA/MDR) | M | $3k–10k |
| ☐ | Consent UX: separate opt-ins for health data collection and sharing (MHMDA / state laws / GDPR Art. 9) | M | $0 (build) |
| ☐ | Security baseline: encryption, MFA for admins, logging, backups, deletion and export (DSAR) flows, retention schedule | L | $0–5k tooling |
| ☐ | Incident response plus HBNR/MHMDA/GDPR breach playbook (60-day FTC, 72-hour GDPR) | M | $0–3k |
| ☐ | No ad pixels on health screens; privacy-first analytics; review vendor DPAs | S–M | $0–1k/yr |
| ☐ | Subscription flow to the CA ARL / ROSCA / EU standard: pre-purchase terms, express consent, confirmation email, trial reminder, one-click cancel, annual reminder | M | $0 |
| ☐ | Affiliate program: disclosure next to every link; structure/function language only; FDA disclaimer; USP/NSF-only product policy; no fake or incentivized reviews | M | $0 |
| ☐ | Store compliance: Apple 1.4.1 / 5.1.3 / 3.1.2, privacy labels and manifest; Google Health apps declaration and Data Safety | M | $0 |
| ☐ | Insurance: tech E&O + cyber + general liability | S | $1.5k–5k/yr |
| ☐ | DPIA (if EU users) plus EU Art. 27 representative | M | $1k–5k + $1k–3k/yr rep |

### Phase C: AI coach
| ☐ | Item | Effort | Est. cost |
|---|---|---|---|
| ☐ | LLM vendor enterprise terms: zero retention, no training, DPA, regional hosting; disclose in the privacy policy | M | Vendor pricing; legal review $1k–3k |
| ☐ | Coach scope spec plus refusal policy; deterministic red-flag pre-filter (self-harm, cardiac, ED, pregnancy, Cushing's signs) with 988 / 109 / 119 routing | L | $0 (build) |
| ☐ | Vetted supplement content library (retrieval only); coach never generates doses | M | Advisor $1k–3k |
| ☐ | Red-team and evaluation suite (EN + KR, 300+ cases), medical-advisor sign-off, monthly sampling | L | $3k–15k (advisor + contractor) |
| ☐ | AI disclosure (EU AI Act Art. 50, Utah, CA, KR AI Basic Act); separate coach consent | S | $0 |
| ☐ | State AI mental-health law review (IL, NV, UT, CA); geo-gate if needed; no "therapy" wording | M | $2k–5k counsel |
| ☐ | Update the DPIA for AI; add an AI rider to E&O insurance | S–M | $0–2k |

### Phase D: B2B / corporate wellness and wearables
| ☐ | Item | Effort | Est. cost |
|---|---|---|---|
| ☐ | Decide whether each deal is inside a **group health plan** (HIPAA BAA) or outside it (perk). Template MSA, DPA and BAA. | L | $5k–15k counsel |
| ☐ | HIPAA program if any covered-entity deal: risk analysis, policies, training, BAA-capable vendors | XL | $10k–40k first year |
| ☐ | Aggregate-only employer dashboards (min cohort ≥ 10–20); employee notice; no individual data to the employer; ADA/GINA incentive review | M | $0–3k |
| ☐ | SOC 2 Type I, then Type II (expected by enterprise buyers) | XL | $20k–60k first year |
| ☐ | Wearable APIs: HealthKit and Health Connect declarations; HBNR coverage confirmed; per-type consent | M | $0 |
| ☐ | Raise cyber coverage limits ($2–5M) for enterprise contracts | S | $3k–10k/yr |

### Phase E: Korea launch
| ☐ | Item | Effort | Est. cost |
|---|---|---|---|
| ☐ | Korean counsel review: 의료법 / 비의료 건강관리서비스 가이드라인 positioning, MFDS wellness classification, 건강지원기기 scope check | L | ₩5M–20M ($4k–15k) |
| ☐ | PIPA: Korean 처리방침, separate 민감정보 consent, itemized consents, overseas-transfer disclosure or consent, CPO designation, under-14 block | L | ₩3M–10M |
| ☐ | Follow the PIPC generative-AI guidance; KR AI Basic Act generative-AI notices | M | included above |
| ☐ | Korean-specific supplement content: check each ingredient and dose against 식품원료 and 건강기능식품 고시; use brand-approved (KHFF-reviewed) functional wording only | M | ₩1M–5M advisor |
| ☐ | KFTC endorsement disclosure ("광고 / 제휴 수수료") on all affiliate placements | S | ₩0 |
| ☐ | 전자상거래법: 통신판매업 신고, subscription consent for price increases and trial conversion, no 6 dark patterns | M | ₩0–1M |
| ☐ | Entity or branch, 사업자등록, Korean ToS (약관규제법), Korean-language support channel | L | ₩2M–5M |
| ☐ | Optional: MFDS 성능인증 if wearable HR features fall in a designated category | XL | Varies (test fees) |

---

## 8. Wording to change in the current app (specific locations)

| Location | Current | Action |
|---|---|---|
| `index.html` line 7 (meta description) | "...program to lower stress and shrink belly fat." | → "...habit program for feeling calmer and working toward a healthier waistline." |
| `index.html` line 370 (Phase 1 goal) | "Fix the foundations that drive cortisol..." | → "Fix the foundations of stress recovery..." |
| `index.html` line 375 (Phase 2 "new") | "Recheck liver tests (ALT) and TSH at weeks 6–8 if you started ashwagandha." | → "If you started ashwagandha, ask your doctor whether liver or thyroid checks make sense." |
| `index.html` line 406 (ashwagandha sub) | "... · ALT/TSH check" | → "Studied amount ... · ask your doctor first" |
| `index.html` line 434 (no-alcohol habit) | "Alcohol raises cortisol and wrecks sleep" | → "Alcohol disrupts sleep, even in small amounts" |
| `index.html` line 662 (**Tier 3**) | Berberine 500 mg 2–3× for insulin resistance; myo-inositol 2 g for PCOS; melatonin dose; "GLP-1 drugs or metformin work far better..." | **Remove all doses and condition indications.** → "Some people discuss berberine, myo-inositol, melatonin or prescription options with their doctor. These are medical decisions." |
| `index.html` line 674 (training) | "Overtraining raises cortisol." | → "Too much hard training without recovery can backfire." |
| `index.html` line 694 (labs) | "Blood tests: baseline and week 12. Fasting, 07:00–09:00..." | → Title "Tests to discuss with your doctor". Keep the list; note "your doctor decides what's appropriate". |
| `index.html` line 697 (See a doctor) | "...possible signs of Cushing's syndrome." | Acceptable. Optionally → "...can have medical causes, including hormone conditions. See a doctor." |
| `PLAN.md` title | "12-Week Cortisol & Belly-Fat Plan" | → "12-Week Stress-Reset & Waistline Plan" |
| `PLAN.md` Phase 2 / Tier 2 / Tier 3 | ALT/TSH recheck; doses for Tier 3 | Same changes as in the app |
| Store listings, ads and landing pages (future) | — | Never use "lowers cortisol", "cortisol test/score", "burn belly fat", "treats", "clinically proven" |

---

## Sources

**FDA / US medical device**
- FDA guidance page, *General Wellness: Policy for Low Risk Devices* (Jan 2026; docket FDA-2014-N-1039): https://www.fda.gov/MedicalDevices/DeviceRegulationandGuidance/GuidanceDocuments/UCM429674
- Faegre Drinker, "Key updates in FDA's 2026 General Wellness and CDS guidance": https://faegredrinker.com/en/insights/publications/2026/1/key-updates-in-fdas-2026-general-wellness-and-clinical-decision-support-software-guidance
- Foley, "FDA relaxes restrictions over wearables and AI decision-making tools in two new 2026 guidances": https://www.foley.com/insights/publications/2026/01/digital-health-policy-fda-relaxes-restrictions-over-wearables-and-ai-decision-ma/
- Loeb & Loeb, "FDA updates its general wellness device framework": https://www.loeb.com/en/insights/passle/2026/01/fda-updates-its-general-wellness-device-frameworkwhat-companies-need-to-know
- FDA, Structure/function claim notification for dietary supplements: https://www.fda.gov/food/information-industry/structurefunction-claim-notification-dietary-supplements

**EU**
- MDCG 2019-11 Rev.1 (June 2025) summaries: https://openregulatory.com/mdcg/mdcg-2019-11 ; https://mdrregulator.com/news/revised-mdcg-2019-11-guidance-updated-approach-to-qualification-and-classification-of-medical-software
- EU AI Act Art. 50 timing and AI Omnibus: https://www.goodwinlaw.com/en/insights/publications/2026/08/alerts-technology-dpc-eu-ai-act-transparency-obligations-now-in-force ; https://www.houthoff.com/insights/news/ai-act-transparency-obligations-and-the-ai-omnibus-regulation/
- Regulation (EU) 2017/745 (MDR), Recital 19 and Annex VIII Rule 11; Regulation (EC) 1924/2006 and the EU Register of health claims (EUR-Lex / European Commission)

**Korea**
- MFDS wellness 판단기준 background: https://kidd.co.kr/news/183571 ; https://www.khan.co.kr/article/201507101034082/amp
- 디지털의료·건강지원기기 제도 시행 (2026): https://medicaltimes.com/Main/News/NewsView.html?ID=1167006 ; Samsung Health first registration: https://www.smarttoday.co.kr/ko-kr/articles/102494
- 디지털의료제품법 시행: https://shinkim.com/kor/media/newsletter/2704
- 비의료 건강관리서비스 가이드라인: https://medigatenews.com/news/1336227781 ; https://www.kukinews.com/article/view/kuk202211090176
- 건강기능식품 금지 표현 (시행규칙 별표): https://www.dailypharm.com/user/news/251562 ; 자율심의: https://khff.or.kr/user/intro/IntroUser4.do
- 추천·보증 심사지침: https://www.shinkim.com/kor/media/newsletter/2613 ; https://www.lawtalk.co.kr/posts/163377
- 전자상거래법 다크패턴 (2025.2.14 시행): https://news.seoul.go.kr/economy/archives/566114 ; https://www.shinkim.com/kor/media/newsletter/3545
- PIPA Art. 23: https://itwiki.kr/w/개인정보 보호법 제23조 ; PIPC 국외이전: https://pipc.go.kr/np/default/page.do?mCode=D060040000 ; PIPC 생성형 AI 안내서 (Aug 2025): https://newsseoul.co.kr/news/view/1065602418218996

**FTC / US advertising and privacy**
- FTC Health Products Compliance Guidance (Dec 2022) summaries: https://www.cov.com/en/news-and-insights/insights/2023/01/ftc-issues-new-guidance-on-health-related-claims-to-replace-the-dietary-supplements-advertising-guide ; https://m.jonesday.com/en/insights/2023/01/ftc-overhauls-and-expands-25yearold-health-products-advertising-compliance-guide
- Endorsement Guides and Consumer Review Rule: https://www.beneschlaw.com/insight/endorsement-enforcement-ftc-updates-endorsement-guides-and-proposes-rule-that-would-impose-penalties-up-to-50k-per-violation
- Health Breach Notification Rule (2024): https://www.mofo.com/resources/insights/240514-ftc-issues-final-rule-to-expand ; https://jonesday.com/en/insights/2024/07/ftc-issues-final-health-breach-notification-rule
- GoodRx / BetterHelp: https://privacylaw.proskauer.com/2023/03/articles/data-privacy-laws/ftcs-one-two-punch-on-data-tracking-and-health-privacy/ ; https://epic.org/ftc-fines-online-therapy-company-betterhelp-7-8-million-for-sharing-health-data
- Washington MHMDA: https://www.aoshearman.com/en/insights/my-health-my-data-act-targets-entities-not-subject-to-hipaa-and-provides-a-private-right-of-action ; https://iapp.org/news/a/washington-on-track-to-pass-health-data-privacy-law
- NYHIPA veto / 2026 bill: https://www.insideprivacy.com/health-privacy/new-york-governor-vetoes-restrictive-health-privacy-law/ ; https://www.mofo.com/resources/insights/260316-nyhipa-returns-in-2026-revised-bill
- HIPAA and wellness programs: https://www.welcoa.org/?p=10943
- Click-to-cancel vacatur and California ARL: https://www.fenwick.com/insights/publications/eighth-circuit-vacates-ftcs-click-to-cancel-rule ; https://www.jdsupra.com/legalnews/ftc-click-to-cancel-rule-on-hold-but-2056488
- State AI mental-health laws: https://healthjournalism.org/blog/2025/08/states-crack-down-on-ai-for-behavioral-health-care ; https://casrai.org/compare/ai-therapy-laws-illinois-nevada-utah-compared

**App stores**
- Apple App Store Review Guidelines (1.4.1, 3.1.1, 3.1.2, 5.1.1(ix), 5.1.3): https://developer.apple.com/app-store/review/guidelines/
- Google Play health apps and Health Connect: https://developer.android.com/health-and-fitness/health-connect/publish ; https://support.google.com/googleplay/android-developer/answer/16679511

*Again: this is not legal advice. Confirm every point marked "verify" against the primary text, and get qualified counsel in each launch market before monetizing.*
