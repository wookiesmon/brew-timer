# 05 — "My supplements" catalog: sources and rationale

**Files:** `data/catalog.js` (structure), `i18n/catalog.en.js`, `i18n/catalog.ko.js` (names, notes, warnings)
**Date:** 2026-10-28 · **Builds on:** `02-supplements.md` (grades and skip list come from there where it covers the item)

## How to read this

- **UL** is the adult (19+) Tolerable Upper Intake Level from the US National Academies (NASEM) as published by NIH ODS. `null` = none established. Some ULs cover **supplements only** (magnesium, niacin, folic acid, vitamin E); the rest cover **total intake** (food + supplements). Calcium uses the **51+ value (2,000 mg)**; ages 19–50 are 2,500 mg.
- **Grade** is the evidence for the item's *most common marketed use* (A strong, B moderate, C weak/mixed, D none/null), following the key in `02-supplements.md`.
- **Dose** is only a pre-filled default from a typical label.
- Warnings are listed **once per pair**; the app must check both directions.
- Note: `ods.od.nih.gov` could not be fetched from the build sandbox. UL values are the published NASEM values, cross-checked against DRI tables ([NASEM UL table](https://www.nationalacademies.org/cdn/materials/9fb9faeb-1faf-41d1-b2f7-381c9b8bdbef), [PMC DRI table](https://pmc.ncbi.nlm.nih.gov/articles/PMC4940574/table/tab1)). Re-check against the ODS links before launch.

ODS fact-sheet pattern: `https://ods.od.nih.gov/factsheets/<Nutrient>-HealthProfessional/`

## Catalog table

| id | UL (unit) · source | Grade · basis · source | Key interactions (warn) · source |
|---|---|---|---|
| vit_d3 | 4000 IU · [ODS Vit D](https://ods.od.nih.gov/factsheets/VitaminD-HealthProfessional/) | B · corrects deficiency; general-population outcome trials (VITAL) mostly null · same | — |
| d3_k2 | 4000 IU (D part) · ODS Vit D | B · as D3; K2 add-on weak · same | w_dup with vit_d3, vit_k2. K2 vs warfarin · [ODS Vit K](https://ods.od.nih.gov/factsheets/VitaminK-HealthProfessional/) |
| mg_glycinate / mg_citrate / mg_threonate | 350 mg supplemental · [ODS Mg](https://ods.od.nih.gov/factsheets/Magnesium-HealthProfessional/) | C · anxiety/sleep "suggestive", low quality (Boyle 2017) · [WRRO](https://eprints.whiterose.ac.uk/115878/) | w_dup between forms |
| fish_oil / algal_oil | null (FDA: up to 5 g/day EPA+DHA OK) · [ODS Omega-3](https://ods.od.nih.gov/factsheets/Omega3FattyAcids-HealthProfessional/) | B · TG lowering strong; CV outcomes mixed; AF signal ≥1 g · same | w_bleed with ginkgo, vit_e |
| krill_oil | null · ODS Omega-3 | C · fewer trials, less EPA+DHA/capsule · same | w_dup fish_oil; w_bleed ginkgo |
| creatine | null | A · lean mass/strength with training (meta-analyses) · [Examine](https://examine.com/supplements/creatine/) | lab: raises serum creatinine |
| l_theanine | null | B · Hidese 2019 RCT · [PMC6836118](https://pmc.ncbi.nlm.nih.gov/articles/PMC6836118/) | — |
| psyllium | null | A · LDL/glucose (FDA heart claim), satiety · [PMC10389520](https://pmc.ncbi.nlm.nih.gov/articles/PMC10389520/) | w_absorb with iron |
| ashwagandha | null | B · stress meta-analyses · [PMC12242034](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12242034/); liver: [LiverTox](https://www.ncbi.nlm.nih.gov/books/NBK548536/) | w_liver (GTE, turmeric, garcinia, RYR), w_sedation (melatonin, lemon balm), w_thyroid (iodine) |
| probiotic | null | C · strain-specific · [PMC11510182](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11510182/) | — |
| saffron | null | B · mood meta-analysis · [Front Nutr 2020](https://www.frontiersin.org/articles/10.3389/fnut.2020.606124/full) | w_serotonin rhodiola, SJW, methylene blue |
| glycine | null | C · small Japanese sleep RCTs · Examine | — |
| multivitamin | null (per nutrient) | C · COSMOS/PHS II: no CVD or mortality benefit · [NCCIH](https://www.nccih.nih.gov/health/vitamins-and-minerals) | w_dup with single nutrients + s_d3 |
| vit_c | 2000 mg · [ODS Vit C](https://ods.od.nih.gov/factsheets/VitaminC-HealthProfessional/) | C · shortens colds slightly; no prevention (Cochrane) · same | lab: some glucose meters |
| b_complex | null as a product (B6 100 mg, niacin 35 mg supplemental, folic acid 1000 µg) · [ODS B6](https://ods.od.nih.gov/factsheets/VitaminB6-HealthProfessional/), [ODS Niacin](https://ods.od.nih.gov/factsheets/Niacin-HealthProfessional/) | C · helps when deficient · 02-supplements | w_dup b12/folate/biotin; lab (biotin) |
| vit_b12 | null · [ODS B12](https://ods.od.nih.gov/factsheets/VitaminB12-HealthProfessional/) | B · deficiency common 50+, metformin, PPIs · same | — |
| folate | 1000 µg folic acid · [ODS Folate](https://ods.od.nih.gov/factsheets/Folate-HealthProfessional/) | B · pregnancy/deficiency · same | masks B12 deficiency |
| biotin | null · [ODS Biotin](https://ods.od.nih.gov/factsheets/Biotin-HealthProfessional/) | D · hair/nails only if deficient · same | lab: troponin, TSH/T4 (FDA 2019 warning, cited in ODS) |
| vit_k2 | null · ODS Vit K | C · bone/arterial small trials · same | warfarin contraindicated |
| vit_e | 1000 mg supplemental α-tocopherol · [ODS Vit E](https://ods.od.nih.gov/factsheets/VitaminE-HealthProfessional/) | D · HOPE/PHS II null; SELECT ↑ prostate cancer · same | w_bleed with fish oil / s_o3 / ginkgo |
| vit_a | 3000 µg RAE preformed · [ODS Vit A](https://ods.od.nih.gov/factsheets/VitaminA-HealthProfessional/) | D · no benefit unless deficient; bone/liver risk · same | — |
| zinc | 40 mg · [ODS Zinc](https://ods.od.nih.gov/factsheets/Zinc-HealthProfessional/) | C · colds (lozenges) modest · same | w_copper (zinc-induced copper deficiency), w_absorb with calcium, iron |
| copper | 10 mg · [ODS Copper](https://ods.od.nih.gov/factsheets/Copper-HealthProfessional/) | C · only needed with high zinc · same | — |
| iron | 45 mg · [ODS Iron](https://ods.od.nih.gov/factsheets/Iron-HealthProfessional/) | B · iron-deficiency anemia; men rarely need · same | w_absorb with calcium, psyllium |
| calcium | 2000 mg (51+; 2500 mg 19–50) total · [ODS Calcium](https://ods.od.nih.gov/factsheets/Calcium-HealthProfessional/) | B · small fracture benefit with D; CV and stone concerns · same | w_absorb iron, zinc; levothyroxine spacing |
| selenium | 400 µg · [ODS Selenium](https://ods.od.nih.gov/factsheets/Selenium-HealthProfessional/) | D · SELECT null for cancer; T2D signal · same | — |
| iodine | 1100 µg · [ODS Iodine](https://ods.od.nih.gov/factsheets/Iodine-HealthProfessional/) | C · only if deficient (Korean diets often high) · same | w_thyroid with ashwagandha |
| electrolytes | null (potassium has no UL; AI only) · [ODS Potassium](https://ods.od.nih.gov/factsheets/Potassium-HealthProfessional/) | C · only when depleted · same | ACE-I/ARB/spironolactone, kidney disease |
| chromium **(skip)** | null · [ODS Chromium](https://ods.od.nih.gov/factsheets/Chromium-HealthProfessional/) | D · effect "clinically insignificant" · [ODS Weight Loss](https://ods.od.nih.gov/factsheets/WeightLoss-HealthProfessional/) | w_sugar with berberine |
| collagen | null | C · skin meta-analyses largely industry-funded · [Examine](https://examine.com/supplements/collagen/) | — |
| glucosamine | null | C · GAIT mixed · [NCCIH](https://www.nccih.nih.gov/health/glucosamine-and-chondroitin-for-osteoarthritis) | warfarin INR rise · same |
| coq10 | null | C · statin myalgia/energy mixed · [NCCIH CoQ10](https://www.nccih.nih.gov/health/coenzyme-q10) | warfarin · same |
| pqq | null | D · almost no human trials · Examine | — |
| nac | null | C · general wellness weak · Examine | nitroglycerin |
| glutathione | null | D · oral bioavailability poor · Examine | — |
| ala | null | C · neuropathy B in diabetes; weight small · [NCCIH ALA](https://www.nccih.nih.gov/health/alpha-lipoic-acid) | w_sugar with berberine |
| nmn, nr **(skip)** | null | D · no human body-composition benefit · 02-supplements | w_dup with each other |
| resveratrol **(skip)** | null | D · null human trials · 02-supplements | antiplatelet, CYP |
| quercetin | null | C · Examine | CYP effects |
| fisetin | null | D · human RCT results not published · Examine | — |
| spermidine | null | D · SmartAge memory RCT null (Schwarz 2022, JAMA Netw Open) | — |
| urolithin_a | null | C · small industry RCTs (Liu 2022, JAMA Netw Open) | — |
| astaxanthin | null | C · Examine | — |
| tmg | null | C · lowers homocysteine; raises LDL (meta-analysis, Zawieja 2019) · Examine | — |
| taurine | null (EFSA observed-safe 3 g) | C · 02-supplements | — |
| l_carnitine | null | C · ~1 kg weight meta-analysis (Pooyandjoo 2016) · Examine | thyroid; TMAO |
| berberine | null | B · weight/glucose meta-analyses · [PubMed 32690176](https://pubmed.ncbi.nlm.nih.gov/32690176/) | w_statin with RYR (CYP3A4 · [PubMed 21870106](https://pubmed.ncbi.nlm.nih.gov/21870106/)); w_sugar myo-inositol, ALA, chromium |
| myo_inositol | null | B · PCOS · [PubMed 35477841](https://pubmed.ncbi.nlm.nih.gov/35477841/) | w_sugar berberine |
| red_yeast_rice | null | B · LDL (monacolin K = lovastatin), variable content · [NCCIH RYR](https://www.nccih.nih.gov/health/red-yeast-rice); 2024 Kobayashi recall · [Wikipedia summary](https://en.wikipedia.org/wiki/Kobayashi_red_yeast_rice_scandal) | w_statin berberine; w_liver ashwagandha |
| melatonin | null | B · sleep onset/jet lag small effect; mislabeling · [NCCIH](https://www.nccih.nih.gov/health/melatonin-what-you-need-to-know). **Korea: prescription-only (전문의약품)** · [DailyPharm](https://dailypharm.com/user/news/86882) | w_sedation ashwagandha, lemon balm, apigenin |
| rhodiola | null | C · inconsistent SR · [PMC3541197](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3541197/) | w_serotonin saffron/SJW/MB; w_stim caffeine |
| holy_basil | null | C · one good RCT · [Lopresti 2022](https://www.frontiersin.org/articles/10.3389/fnut.2022.965130/full) | antiplatelet |
| apigenin | null | C · chamomile GAD trials; isolated apigenin almost none · 02-supplements | w_sedation melatonin |
| lemon_balm | null | C · small acute RCTs · 02-supplements | w_sedation ashwagandha, melatonin |
| lions_mane | null | C · tiny RCTs · Examine | — |
| alpha_gpc | null (choline UL 3.5 g; 600 mg α-GPC ≈ 240 mg choline) | C · weak · Examine. Stroke HR 1.46 in Korean NHIS cohort (Lee 2021) · [PMC8613599](https://pmc.ncbi.nlm.nih.gov/articles/PMC8613599/) | — |
| ginkgo | null | D · GEM trial: no prevention of decline · [NCCIH Ginkgo](https://www.nccih.nih.gov/health/ginkgo) | w_bleed fish/krill/algal oil, s_o3, turmeric, vit_e · same |
| methylene_blue **(skip)** | null | D · little human evidence for cognition · [FDA 2011 DSC](https://www.fda.gov/drugs/drug-safety-and-availability/fda-drug-safety-communication-serious-cns-reactions-possible-when-methylene-blue-given-patients) | w_serotonin (MAO-A inhibitor) saffron, SJW, rhodiola |
| turmeric | null | B · knee OA meta-analyses · [NCCIH Turmeric](https://www.nccih.nih.gov/health/turmeric); liver: [LiverTox (search "Turmeric")](https://www.ncbi.nlm.nih.gov/books/NBK547852/) | w_liver ashwagandha, GTE; w_bleed ginkgo |
| mct_oil | null | C · small weight effect (Mumme 2015) · Examine | — |
| caffeine | null (FDA: 400 mg/day generally safe) · [FDA](https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much) | A · alertness/performance · ISSN position | w_stim red ginseng, GTE, rhodiola |
| beetroot | null | B · endurance, small BP drop · Examine | w_bp citrulline |
| citrulline | null | C · mixed performance data · Examine | w_bp beetroot; PDE5 inhibitors |
| whey | null | A · muscle with training when protein short (Morton 2018 meta-analysis) | kidney disease |
| st_johns_wort **(skip)** | null | B · mild depression (Cochrane) but skipped for interactions · [NCCIH SJW](https://www.nccih.nih.gov/health/st-johns-wort) | strong CYP3A4/P-gp inducer; w_serotonin saffron, rhodiola, MB |
| saw_palmetto | null | D · Cochrane 2023 (27 RCTs): no LUTS benefit · [Cochrane CD001423](https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001423.pub4/pdf/CDSR/CD001423/CD001423_abstract.pdf), [AFP summary](https://www.aafp.org/pubs/afp/issues/2024/0500/cochrane-saw-palmetto-benign-prostatic-hyperplasia.html) | antiplatelet (theoretical) |
| lutein | null | B · AREDS2 for intermediate AMD · [NEI AREDS2](https://www.nei.nih.gov/research/clinical-trials/age-related-eye-disease-studies-aredsareds2) | — |
| red_ginseng (홍삼) | null | C · fatigue/immunity small trials · [NCCIH Asian ginseng](https://www.nccih.nih.gov/health/asian-ginseng) | warfarin INR, glucose; w_stim caffeine |
| milk_thistle (밀크씨슬) | null | C · NAFLD ALT modest; Cochrane null on mortality · [NCCIH Milk thistle](https://www.nccih.nih.gov/health/milk-thistle) | may lower glucose |
| propolis (프로폴리스) | null | C · small oral/throat trials · Examine | bee/pollen allergy; antiplatelet |
| green_tea_extract **(skip)** | null (EFSA: ALT rises ≥800 mg EGCG) | C · ~1 kg weight · [UK COT](https://cot.food.gov.uk/Statement%20on%20the%20Hepatotoxicity%20of%20Green%20Tea%20Catechins%20-%20COT%20Conclusions) | w_liver ashwagandha, turmeric; w_stim caffeine |
| cla **(skip)** | null | D · ~0.5 kg; t10c12 worsens insulin sensitivity (Risérus 2004) · ODS Weight Loss | — |
| acv **(skip)** | null | D · flagship RCT retracted 2025 · [BMJ](https://bmjgroup.com/bmj-group-retracts-trial-on-apple-cider-vinegar-and-weight-loss/) | potassium with diuretics/digoxin |
| garcinia **(skip)** | null | D · null weight trials · ODS Weight Loss; [LiverTox (search "Garcinia")](https://www.ncbi.nlm.nih.gov/books/NBK547852/) | w_liver ashwagandha; serotonergic case reports |
| dhea **(skip)** | null | C · hormonal; no clear benefit in men · [NCCIH DHEA](https://www.nccih.nih.gov/health/dhea) | lab: sex-hormone panels |

## Interaction keys used

| key | Meaning | Pairs |
|---|---|---|
| w_bleed | Additive antiplatelet/anticoagulant | ginkgo × omega-3s/vit E/turmeric; vit E × fish oil |
| w_serotonin | Serotonin syndrome risk | saffron/s_saf × rhodiola, SJW, methylene blue |
| w_sedation | Additive CNS depression | melatonin × ashwagandha/lemon balm/apigenin; lemon balm × ashwagandha |
| w_absorb | Competes for absorption; separate 2 h | iron × calcium/zinc/psyllium; calcium × zinc |
| w_copper | Zinc-induced copper deficiency | zinc × copper |
| w_bp | Additive BP lowering | beetroot × citrulline |
| w_sugar | Additive glucose lowering | berberine × myo-inositol/ALA/chromium |
| w_liver | Stacked hepatotoxicity signals | ashwagandha × GTE/turmeric/garcinia/RYR; GTE × turmeric |
| w_statin | Statin-like + CYP3A4 inhibitor | red yeast rice × berberine |
| w_stim | Stacked stimulants | caffeine × red ginseng/GTE/rhodiola |
| w_thyroid | Both shift thyroid hormones | iodine × ashwagandha |
| w_dup | Same nutrient twice (sum toward UL) | multivitamin × singles; D3+K2 × D3/K2; magnesium forms; krill/algal × fish oil; NMN × NR; B-complex × B12/folate/biotin |

## Open items

- Calcium UL is age-dependent; the catalog uses 2,000 mg (51+). If the app knows the user's age, use 2,500 mg for 19–50.
- `multivitamin` and `b_complex` have `dose: null` (no single number describes them). The UI should ask for nutrient amounts or skip the UL check.
- `ul` for caffeine is `null`; the FDA's 400 mg/day is guidance, not a UL. The note text mentions it.
- Vitamin E dose uses mg α-tocopherol (400 IU natural = 268 mg); bottles in IU need converting (×0.67 natural, ×0.45 synthetic).
