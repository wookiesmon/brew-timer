# 04 — Competitive Landscape & Design System

*Product & Design department · researched 2026-10-27*

Scope: a mobile-first, single-file, offline web app (data in `localStorage`) that runs one user through a 12-week program to lower cortisol/stress and lose belly fat. Core loops: daily checklist (supplements, meals, steps, breathing, sleep), daily check-in (stress 1-10, energy, sleep hours, mood), weekly measurements (waist, weight, HRV, resting HR), progress charts, and a 12-week phase plan.

> Pricing caveat: most prices below come from third-party review/aggregator pages, and many of those pages disagree with each other. Treat them as ballpark figures as of 2025-2026, not verified list prices.

---

## 1. Competitive survey

### 1.1 Wearable / physiology platforms

| App | Stress / cortisol angle | Fat-loss angle | Price (approx.) | UX worth borrowing | Gaps for our use case |
|---|---|---|---|---|---|
| **WHOOP** | Stress Monitor (0-3 scale from HR/HRV) on the Peak tier and above; recovery score from HRV/RHR/sleep | Strain/calories only; no nutrition program | One $199/yr, Peak $239/yr (adds Stress Monitor), Life $359/yr | One hero number per day (Recovery %) on a coloured ring; journal that correlates behaviours with recovery ("When you log X, recovery is Y% higher") | Needs hardware; no structured program; no waist tracking; scores can turn into "number anxiety" |
| **Oura** | Daytime Stress graph, "Resilience" level; readiness score | Activity only | Ring ~$299+ plus membership ~$5.99/mo or $69.99/yr | Calm, low-saturation visuals; plain-language "Readiness" text under the number; long-term trends | Hardware lock-in; descriptive, not prescriptive; no protocol or checklist |
| **Welltory** | Camera-finger HRV "stress & energy" measurement; correlations dashboard | None | Free core; Pro roughly $79.99-$119.99/yr (sources conflict) | "Measure now" one-tap flow; combines several metrics into a stress/energy pair; correlation cards | Noisy UI with many paywalls; no fat-loss or program structure |
| **Bevel** | Free Stress score (HRV-based "daily load") alongside Recovery/Sleep/Strain | Food logging added later | Free tier; Pro reported at $5.99/mo-$49.99/yr (App Store) up to $14.99/mo-$99.99/yr (2026 review) | Clean Apple-native rings, everything on one Today screen, generous free tier | Apple Watch only; broad, so it's complex; no 12-week arc |
| **Athlytic** | HRV/RHR recovery and energy, a cheap WHOOP alternative | None | ~$30/yr | Uses data the user already has (Apple Health); simple gauge plus a target | Cardio-biased recovery; no habits/program |

### 1.2 Calm / breathing

| App | Stress angle | Price | UX worth borrowing | Gaps |
|---|---|---|---|---|
| **Calm** | Meditation, sleep stories, breathe bubble | ~$69.99/yr (monthly $14.99-$16.99) | Nature imagery; "Daily Calm" single daily session; soft gradient backgrounds | Content library, not a measurable program; no physiology or body metrics |
| **Headspace** | Guided meditation courses | ~$69.99/yr | Friendly illustration; courses split into days; gentle "run streak" | Same: no outcome tracking beyond minutes |
| **Breathwrk** (Peloton) | Short breathing "classes" by goal (calm, sleep, energy) | Pro ~$49/yr; free with Peloton | Expanding/contracting shape with haptics; goal-based picker ("I want to... calm down") | No link between breathing and stress outcome over weeks |
| **Open** | Breathwork + meditation + movement classes | Free download, subscription in-app | Premium dark aesthetic; streaks plus Apple Health mindful minutes | Class library; no body-composition goal |

### 1.3 Nutrition / fat loss / metabolism

| App | Angle | Price | UX worth borrowing | Gaps |
|---|---|---|---|---|
| **MyFitnessPal** | Calorie and macro logging | Premium ~$79.99/yr | Huge food DB; quick-add; daily remaining-calories bar | Logging fatigue; calorie focus can raise stress; ignores cortisol/sleep |
| **Cronometer** | Micronutrient-accurate logging | Gold ~$49.99/yr | Nutrient "targets" bars (great for magnesium, protein, fibre) | Data-dense, clinical UI |
| **Lifesum** | Diet plans (keto, high-protein, etc.), "Life Score" | Premium $44.99-$99.99/yr (regional) | Best-looking tracker; colourful food cards; plan-based onboarding | Free tier is thin; macro-focused |
| **Zero** | Fasting timer, streaks; Plus adds mood journal, protein score, correlated charts | Plus ~$69.99/yr | Big circular countdown timer; zone labels ("fat burning") along the ring; streaks | Long fasting can raise cortisol for some users, so it fits our goal poorly as a default |
| **Lumen** | CO2 breath test that tells you whether you're burning carbs or fat | $249-$349 per 6-18 months, then ~$19/mo | Morning one-action ritual followed by a daily plan | Expensive, accuracy debated, demands daily tests |
| **Levels** | CGM glucose response scoring | Sensors ~$199 per shipment; app membership | Meal "zone scores"; explaining *why* a spike happened | Hardware cost; glucose is only part of the stress/belly-fat picture |

### 1.4 Habits / protocol / gamification

| App | Angle | Price | UX worth borrowing | Gaps |
|---|---|---|---|---|
| **Habitify** | Habit tracker grouped by time of day | Free (3 habits); ~$35.99/yr or ~$65 lifetime | **Morning / Afternoon / Evening sections**; "do" and "avoid" habits; completion heat-map | Generic: no metrics, no program content |
| **Finch** | Self-care pet; tasks earn energy for a bird | Free + Plus | **No penalty for missed days**; tiny tasks count; warm, forgiving tone | Childlike aesthetic; no health metrics |
| **Blueprint Protocol** (unofficial, Bryan Johnson) | Lists the Blueprint routine; supplements filtered by time of day | Free | **Supplements grouped by time slot**; routine milestones (wake, last meal, bed) | Static reference; no tracking or outcomes |

### 1.5 "Cortisol" apps (new 2025-26 niche)

| App | What it does | Notes |
|---|---|---|
| **Lower Cortisol: Calmer** | Free; 8 daily habits (morning light, consistent bedtime...) produce a 0-100 "Calm Score"; on-device, no account | Closest to our concept, but there's no fat-loss, measurement, or phase structure, and no ratings yet |
| **CalmTide: Cortisol Tracker** | Reads Apple Health, estimates "cortisol load" and shows an HPA Balance Score ring | An estimate presented like a measurement; iOS 18.6+ only |
| **Cortisol+** | ~$2.99; Apple Watch HRV/sleep, "continuous cortisol insights" | Marketing overstates what it measures |
| **Cortisol Detox** | Weight-loss program: meal plans, workouts, meditation, onboarding quiz | Closest on fat loss, but it doesn't track stress or body metrics |
| **Eli Health** | At-home saliva cortisol test sticks plus app | The only one that actually measures cortisol; expensive per test |

### 1.6 Top competitor takeaways

1. **One hero score, explained in words** (WHOOP Recovery, Oura Readiness, Calmer's Calm Score). Users want a single daily number with a one-line meaning. We compute a transparent **Calm Score** from the checklist and check-in. It is never called a cortisol reading.
2. **Group habits by time of day** (Habitify, Blueprint). Supplements, meals, light, and breathing are time-bound, so Morning / Midday / Evening / Night sections beat a flat list.
3. **Forgiving gamification** (Finch, Headspace). No penalty for missed days, and small actions count. Streak loss is a known stressor, which matters even more for a stress-reduction app.
4. **Correlation insights build motivation** (WHOOP Journal, Welltory, Zero Plus). For example: "On days you hit 8k steps your next-day stress averaged 1.4 lower." We can compute this offline from local data.
5. **Ritual over library** (Calm's Daily Calm, Lumen's morning test, Breathwrk's goal picker). Give one obvious next action, such as "Do your 4-min evening downshift", instead of a content catalogue.

Also notable: every physiology player needs **hardware and a subscription** ($70-$360/yr). A free, private, offline app that accepts manually typed HRV/RHR from any device (or none) avoids that barrier.

### 1.7 Market gap

No product joins **stress physiology + belly-fat outcomes + a time-boxed program**:
- Wearables (WHOOP/Oura/Bevel) *measure* stress but don't *prescribe* a plan, and they ignore waist size.
- Calm apps (Calm/Headspace/Breathwrk) prescribe relaxation but measure nothing physical.
- Fat-loss apps (MFP/Lifesum/Zero/Lumen) focus on calories or fuel and can *increase* stress through restriction and logging fatigue.
- The new "cortisol" apps are either thin habit trackers (Calmer) or overclaim estimated cortisol (CalmTide, Cortisol+).

**Our position:** a *calm, 12-week, phase-based protocol* that connects daily stress behaviours (sleep, light, breathing, steps, protein-forward meals, supplements) to the outcome people care about: **waist circumference trending down while stress and RHR trend down and HRV trends up**. It is private (no account, offline), hardware-optional, and honest that the score is a behaviour index, not a lab value.

---

## 2. Design system

### 2.1 Product name ideas

| Name | Rationale |
|---|---|
| **Ebb** (favourite) | Cortisol should *ebb*: high in the morning, low at night. It's a tide metaphor, short, calm, and premium. Tagline: *"Ebb — twelve weeks to a calmer core."* |
| Stillwater | Evokes a still mind; slightly longer, more lifestyle-brand |
| Kalm Core | Says both outcomes at once (calm + core/belly), but sounds more like a fitness brand |
| Grove | Forest/sage palette tie-in, growth over 12 weeks |
| Downshift | Describes the parasympathetic "downshift"; good verb for the breathing feature |

**Favourite: Ebb.** It works as an app icon (lowercase "ebb" or a single wave line) and fits a sage/sand palette, and "Ebb Score" reads naturally.

### 2.2 Design principles

1. **Calm is the feature.** Every screen should lower arousal: soft contrast backgrounds, no red badges, no countdown pressure, slow easing (250-400 ms, `ease-out`), and generous whitespace.
2. **One next step.** Today always shows the single most relevant action for the time of day.
3. **Progress over perfection.** Partial days count. The UI celebrates *trend*, never punishes a miss.
4. **Honest numbers.** Label the Calm Score as a habit and feeling index. Show units, and show raw data alongside derived scores.
5. **Thumb-first and offline-first.** Primary actions sit in the bottom 40% of the screen. Logging takes under 30 seconds a day, with no network dependency.
6. **Private by default.** Show a "Your data stays on this device" note, plus export/import JSON in settings.

### 2.3 Colour rationale (colour psychology for stress)

- **Sage and forest green (primary):** green and nature cues are linked to restoration and lower stress in environmental-psychology research. A 2021 lab study found nature *content* matters more than green hue alone. So we pair green with organic shapes (wave, leaf) rather than relying on hue only. Desaturated greens read as calm and natural, not clinical like hospital teal.
- **Warm sand (neutral and accent):** warm off-whites feel softer and less clinical than pure #FFF and reduce glare. Sand also gives a premium, spa-like tone.
- **Soft amber (warning):** signals "pay attention" without the alarm of red. Use it for elevated-stress days, missed measurements, or a high RHR.
- **Muted terracotta (danger):** reserved for destructive actions (reset or delete data) only, never for "you failed a habit".
- **Dusk blue (info):** used for sleep and night items, associated with evening wind-down.
- **Dark mode:** a deep forest-charcoal background (not pure black) for evening use, to cut light exposure before bed, which also fits the program's sleep goals.

### 2.4 Palette: light mode

| Token | Hex | Use |
|---|---|---|
| `--bg` | `#F7F4EE` | App background (warm sand paper) |
| `--surface` | `#FFFDF9` | Cards |
| `--surface-2` | `#EFEAE0` | Inset areas, slider tracks, segmented control bg |
| `--border` | `#E2DBCD` | Hairlines, card borders |
| `--text` | `#1F2A24` | Primary text (forest ink) |
| `--text-muted` | `#5C6B62` | Secondary text, labels |
| `--primary` | `#3F6B52` | Forest sage: buttons, active tab, ring fill |
| `--primary-strong` | `#2F5640` | Pressed state, headings accent |
| `--primary-soft` | `#DCE8DF` | Chip bg, ring track, checked-row tint |
| `--accent` | `#8A6A3E` | Deep sand (text-safe accent, e.g. phase labels) |
| `--accent-soft` | `#F1E6D3` | Sand highlight bg (phase card, milestone) |
| `--success` | `#3A7151` | Completed, improving trend |
| `--success-soft` | `#DDEDE2` | Success bg |
| `--warning` | `#9A5B13` | Amber text/icon: elevated stress, overdue measurement |
| `--warning-soft` | `#FBEBD0` | Amber bg |
| `--danger` | `#A8452F` | Destructive actions only |
| `--danger-soft` | `#F6DFD7` | Destructive bg |
| `--info` | `#3F6582` | Dusk blue: sleep, night, tips |
| `--info-soft` | `#DDE7EF` | Info bg |
| `--on-primary` | `#FFFFFF` | Text on primary buttons |

### 2.5 Palette: dark mode

| Token | Hex | Use |
|---|---|---|
| `--bg` | `#121915` | Deep forest-charcoal |
| `--surface` | `#1A231E` | Cards |
| `--surface-2` | `#223029` | Insets, tracks |
| `--border` | `#2E3D35` | Hairlines |
| `--text` | `#ECE7DD` | Primary text (warm off-white) |
| `--text-muted` | `#A3B0A7` | Secondary text |
| `--primary` | `#8DBA9C` | Sage (lightened) |
| `--primary-strong` | `#A8CFB4` | Pressed/hover |
| `--primary-soft` | `#23382B` | Chip bg, ring track |
| `--accent` | `#D9BE94` | Sand |
| `--accent-soft` | `#2E2A22` | Sand bg |
| `--success` | `#7FC096` | Completed |
| `--success-soft` | `#1F3527` | Success bg |
| `--warning` | `#E3A857` | Amber |
| `--warning-soft` | `#3A2E1A` | Amber bg |
| `--danger` | `#E58C74` | Destructive |
| `--danger-soft` | `#3B241E` | Destructive bg |
| `--info` | `#8DB3CF` | Dusk blue |
| `--info-soft` | `#1E2C37` | Info bg |
| `--on-primary` | `#121915` | Text on primary buttons |

**Measured contrast (WCAG 2.x formula, computed for this report):**
- Light, on `--bg` / `--surface`: text 13.5 / 14.6; muted 5.1 / 5.5; primary 5.6 / 6.0; accent 4.5 / 4.9; warning 4.9 / 5.3; danger 5.4 / 5.8; info 5.6 / 6.1; success 5.2 / 5.7. White on primary: 6.1.
- Dark, on `--bg` / `--surface`: text 14.5 / 13.1; muted 7.9 / 7.2; primary 8.2 / 7.4; accent 10.0 / 9.0; warning 8.5 / 7.7; danger 7.1 / 6.4; info 8.1 / 7.3; success 8.4 / 7.6. `--on-primary` on primary: 8.2.
- Every text/foreground pairing passes **AA (≥4.5:1)**.
- Soft tints (`*-soft`) are backgrounds only. Ring tracks are decorative (1.2:1), so the ring always carries a numeric label.

**Data-viz series (charts):** stress `#9A5B13`/`#E3A857` (amber; down is good), energy `#3F6B52`/`#8DBA9C`, sleep `#3F6582`/`#8DB3CF`, waist `#8A6A3E`/`#D9BE94`, HRV `#3A7151`/`#7FC096`, RHR `#A8452F`/`#E58C74`. Charts show at most two series at once, and every line has a direct end label, so meaning never depends on colour alone.

### 2.6 Typography (Google Fonts)

- **Display: Fraunces** (soft variable serif; use `opsz` 72-144, weight 500-600, `SOFT` 50-100). Used for the hero score number, screen titles, and phase names. It's warm and premium, not clinical.
- **UI/body: Inter** (weights 400/500/600; `font-feature-settings: "tnum"` for numbers in tables and charts). Highly legible at small sizes, with excellent tabular figures.
- Offline: the app is a single file, so embed subsets as base64 `@font-face`, or fall back gracefully to `ui-serif, Georgia` / `system-ui, -apple-system, Segoe UI, Roboto`. The design must still look right on the fallback.

Type scale (rem; base 16px; line-height in parentheses):
| Token | Size | Font | Use |
|---|---|---|---|
| `display` | 3.5 (1.0) | Fraunces 600 | Calm Score in ring |
| `h1` | 1.75 (1.2) | Fraunces 600 | Screen title |
| `h2` | 1.25 (1.3) | Fraunces 500 | Card titles |
| `body` | 1.0 (1.5) | Inter 400 | Body |
| `label` | 0.875 (1.4) | Inter 500 | Row labels, chips |
| `caption` | 0.75 (1.4) | Inter 500, +0.02em tracking, uppercase only for section eyebrows | Units, eyebrows |

Support Dynamic Type: use `rem` everywhere and test at 200% zoom.

### 2.7 Spacing, radius, elevation, motion

- **Spacing (4-pt base):** 4, 8, 12, 16, 20, 24, 32, 40, 56. Page gutter is 16 px (20 px at ≥400 px width), card padding is 16-20 px, and the gap between cards is 12 px.
- **Radius:** chip/pill 999px; control 12px; card 20px; sheet 28px top corners; checkbox 8px (a soft square, not a harsh box).
- **Elevation:** light mode uses a 1px border `--border` plus a shadow `0 1px 2px rgba(31,42,36,.06), 0 4px 16px rgba(31,42,36,.05)`. Dark mode uses no shadows; separate cards with `--surface` vs `--bg` and a 1px border.
- **Motion:** 200 ms for UI state changes and 400 ms ease-out for ring fill. The breathing pacer follows the real breath timing. Respect `prefers-reduced-motion`: the ring snaps, and the pacer becomes a text count plus a slow opacity fade.
- **Max content width:** 520 px, centred on desktop.

### 2.8 Component list

| Component | Spec |
|---|---|
| **Score ring** | 180-200 px SVG ring. Track `--primary-soft`, fill `--primary`, stroke 14 px with round caps. Centre shows the Fraunces score (0-100) and a caption ("Calm Score · steady"). A thin sand tick marks yesterday's value. Tap opens a breakdown sheet (habits 60% / check-in 40%, each item listed). |
| **Mini rings ×3** | 44 px rings for Sleep / Move / Calm categories, under the hero ring (WHOOP/Bevel pattern) |
| **Habit check row** | Min height 56 px; left 28 px soft-square checkbox; label + sublabel (dose/time, e.g. "Magnesium glycinate · 300 mg"); right-side optional "info" icon button (44×44). Checked state: `--primary-soft` row tint, check animates in, and the label keeps full contrast (no strikethrough, so completed items stay readable). Long-press or swipe to "Skip today (that's okay)". |
| **Time-of-day section header** | Eyebrow ("MORNING · 3 of 5") + small progress bar; collapsible; current section auto-expanded |
| **Stepper / counter row** | For steps or water: −/+ buttons at 44 px + numeric input; optional progress bar to target |
| **Stress slider (1-10)** | Custom range input, track 8 px, thumb 32 px. Track gradient runs from sage (1) to sand (5) to amber (10), never red. Large live value above the thumb, and anchor words at both ends ("At ease" / "Overwhelmed"). Keyboard and screen-reader accessible (`aria-valuetext="4, mild"`). |
| **Energy / mood segmented picker** | 5 options with icon + word (e.g. Drained, Low, OK, Good, Bright). Equal-width 48 px tall pills. |
| **Number input card** | Waist/weight/HRV/RHR: big numeric field (`inputmode="decimal"`), unit toggle (cm/in, kg/lb), last value shown as placeholder hint, delta chip after save |
| **Sparkline card** | Title + latest value + 7-day or 12-week sparkline (SVG polyline, 2 px stroke, last point dot, no axes) + trend chip ("▼ 2.1 cm since start"). Trend colour reflects *desired direction*: waist down = success, stress up = warning. |
| **Line chart (full)** | Progress tab: weekly points, light gridlines `--border`, direct labels, phase bands shaded in alternating `--surface-2`, tap or drag for a tooltip |
| **Phase timeline** | Vertical list of 12 weeks grouped into phases. Current week has a filled sage node, past weeks are hollow with a check, future weeks are muted. Each phase card has a sand eyebrow ("PHASE 2 · WEEKS 4-6"), a name in Fraunces, and 3 focus bullets. A horizontal 12-segment mini bar sits at the top of Today. |
| **Breathing pacer** | Full-screen calm view: an expanding circle or wave, with cues for inhale / hold / exhale. Presets: physiological sigh, 4-7-8, box 4-4-4-4, resonant 5.5 bpm. Timer selector 1/3/5/10 min. Completion auto-checks the "Breathing" habit. |
| **Insight card** | Sand-soft bg, lightbulb icon. One sentence plus "Why this matters" disclosure. Used for correlations and phase tips. |
| **Bottom sheet** | For check-in and measurements; drag handle, 28 px top radius, primary CTA pinned at the bottom |
| **Toast** | Gentle confirmation, auto-dismiss 3 s; text such as "Saved. Nice work showing up." |
| **Empty state** | Line illustration (wave/leaf) + one sentence + one button |
| **Bottom tab bar** | 5 tabs, 64 px + safe-area inset, icon 24 px + label 11-12 px. Active tab has a pill highlight in `--primary-soft`. |

### 2.9 Information architecture: bottom tabs

1. **Today** (home): hero Calm Score ring, week/phase strip, the "next up" card, time-of-day habit checklist, and a check-in prompt card.
2. **Check-in**: daily check-in (stress, energy, mood, sleep hours, optional note) plus weekly measurements (unlocked on the measurement day, available anytime).
3. **Breathe**: breathing pacer and presets; a quick "I'm stressed right now" button.
4. **Progress**: charts, correlation insights, before/after summary.
5. **Plan**: 12-week phase timeline, current phase guidance, habit editor. Settings (theme, units, reminders, export/import, reset) sit behind a gear icon in the Plan header.

Why Breathe gets a tab: it's the one *acute* stress intervention, and it must be reachable in one tap at a stressful moment.

### 2.10 Key screens in detail

**A. Onboarding (first launch, 4 short steps, skippable)**
1. Welcome: "Ebb is a 12-week plan to calm your stress system and shrink your waist. Everything stays on this device."
2. Start date (default today) and measurement day (default Sunday).
3. Baseline: waist, weight, optional HRV/RHR, plus a stress 1-10 slider. Units toggle.
4. Choose habits: a preloaded program list grouped by time of day. Toggle off what doesn't apply; supplements are editable.
5. Disclaimer: "Not medical advice. The Calm Score reflects habits and how you feel; it is not a cortisol test."

**B. Today**
- Header: "Tuesday · Week 3 of 12", a phase chip ("Phase 1 · Reset"), and the 12-segment progress bar.
- Hero: Calm Score ring with 3 mini rings (Sleep, Move, Calm) and a one-line interpretation ("Steady. Evening downshift will lift it most.").
- **Next up** card: the single most relevant pending item for the current time (e.g. 21:30, "4-min downshift breathing", with a Start button).
- Check-in card (if not done): "How are you, really? 30 seconds." The button opens a bottom sheet. Once done, it collapses to a summary chip row (Stress 4 · Energy Good · Slept 7.2h).
- Checklist: Morning (light exposure, protein breakfast, supplements AM), Midday (walk / steps counter, lunch), Afternoon (caffeine cutoff reminder, snack), Evening (dinner, magnesium, screens down), Night (lights out by target, sleep). The current section is expanded and the others are collapsed with "3/5" counts.
- Measurement banner (on measurement day): sand card "Weekly check: waist, weight, HRV, RHR — 1 min".

**C. Check-in (tab)**
- Segmented control: **Daily** | **Weekly**.
- Daily: stress slider; energy picker; mood picker; sleep hours stepper (0.25 h increments, with an optional bedtime/wake time to auto-calculate); optional "What drove today's stress?" tag chips (work, sleep, family, caffeine, alcohol, illness) and a note. Save → toast plus Calm Score update.
- Weekly: waist (cm/in; how-to tip, "at the navel, relaxed exhale"), weight, HRV (ms, optional, with source text "any device"), RHR (bpm, optional). Show the previous value and delta after save. History list below with edit/delete.

**D. Breathe**
- Big preset cards: *Quick reset — physiological sigh (1 min)*; *Downshift — resonant 5.5/min (5 min)*; *Sleep — 4-7-8 (4 cycles)*; *Focus — box breathing*.
- Session view: dark-leaning full screen, a pacer circle grows during inhale and shrinks during exhale, with the phase word and remaining time. Optional vibration via `navigator.vibrate` on Android. Optional pre/post "How tense do you feel? 1-10", stored to show the per-session drop ("Tension 7 → 4").
- History: minutes this week, gentle count.

**E. Progress**
- Range toggle: 2W | 12W | All.
- Headline cards (2×2 grid of sparkline cards): Waist (Δ since start), Stress avg (7-day), HRV, RHR. Weight sits below waist on purpose: belly fat is the target, so waist leads.
- Full charts: stress + sleep (daily), waist + weight (weekly), HRV + RHR (weekly), with phase bands.
- Habit heat-map: 12 columns × 7 rows of rounded squares (opacity = % of habits done). No empty-square shaming; misses show as neutral `--surface-2`.
- Insights: offline correlations ("Stress was 1.6 lower on days after 7+ hours of sleep (n=18)"), shown only when n ≥ 7, with the sample size displayed.
- Milestones: "First 2 cm off your waist", "21 evening downshifts".

**F. Plan**
- Current phase card (expanded): name, weeks, goal, 3-5 focus behaviours, and what's new this phase (e.g. adding a step target, adjusting meals).
- Vertical 12-week timeline with weekly focus lines; tapping a week shows that week's targets and a recap (avg stress, habits %, waist).
- "Edit my habits": add, remove, or reorder; set time-of-day slot and dose.
- Gear → Settings: theme (System/Light/Dark), units, measurement day, reminder times (Notification API when available), export JSON / import JSON / CSV export, reset program (danger, with a confirm dialog).

### 2.11 Gamification that doesn't add stress

- **Consistency, not streaks:** show "Showed up 5 of the last 7 days" (rolling window) instead of a fragile consecutive streak. If a streak is shown, use **"best run"** and an automatic **grace day** each week; never display "streak lost".
- **Partial credit:** any check-in counts as "showing up". The day ring fills proportionally, and 60% is labelled "solid day".
- **Gentle milestones:** non-competitive badges (leaf/stone/wave motifs) for cumulative actions, e.g. 10 breathing sessions, 30 check-ins, first 1 cm, Phase 1 complete. Celebrate quietly with a soft ring bloom and a short line, no confetti explosions.
- **Phase completion ritual:** at the end of each phase, a recap card shows before/after numbers with a reflective prompt ("What helped most?").
- **Growing visual:** an optional small plant or tide illustration on Today that grows with *cumulative* actions. Like Finch, it never wilts or regresses.
- **Copy rules:** never "failed", "missed", "broke" or "behind". Prefer "skipped", "rest day", "pick up where you left off". When stress ≥ 8, the app responds with care ("Rough day. Want a 1-minute reset?") rather than a warning.
- **No push guilt:** reminders are opt-in, max 3/day, and never sent after the user's set bedtime.

---

## 3. Accessibility notes

- **Contrast:** all text tokens meet WCAG AA 4.5:1 in both themes (see §2.5). Large score numerals exceed 7:1. Non-text UI (checkbox borders, slider thumbs, focus rings) must reach ≥3:1 (SC 1.4.11). Use `--primary` / `--text-muted` for borders of interactive controls, never `--border`.
- **Target size:** WCAG 2.2 SC 2.5.8 (AA) requires ≥24×24 CSS px; we adopt the **44×44 px** AAA / Apple HIG standard for every tap target (rows 56 px, slider thumb 32 px with 44 px hit area, tab items ≥64 px wide). Keep ≥8 px between adjacent targets.
- **Not colour-only:** trends use arrows and words ("▼ 1.2 cm"), and chart lines have direct labels. Stress severity always shows a number and a word.
- **Semantics:** native `<button>`, `<input type="checkbox">`, `<input type="range">` with `aria-valuetext`; `role="tablist"` for bottom nav with `aria-current="page"`; `aria-live="polite"` for score updates and toasts; SVG rings get `role="img"` + `aria-label="Calm Score 72 of 100"`.
- **Focus:** visible 2-3 px focus ring in `--primary` with 2 px offset; logical order; Escape closes sheets; focus is trapped in open sheets and returned on close.
- **Motion:** honour `prefers-reduced-motion` (no ring sweep, pacer becomes text + fade). No auto-playing animation except the pacer the user starts.
- **Text scaling:** rem units, layout survives 200% zoom and 320 px width without horizontal scroll; no text in images.
- **Theme:** follow `prefers-color-scheme` with a manual override; dark mode default suggested after the user's wind-down time.
- **Forms:** visible labels (not placeholder-only); `inputmode="decimal"`; clear unit labels; inline validation in plain language ("Waist looks unusually high — check units?").
- **Cognitive load:** one primary action per screen, short sentences, and plain words (avoid jargon like "HPA axis" in UI; put it in "Learn more").
- **Health safety copy:** persistent "Not medical advice" in settings and onboarding; if stress ≥ 9 for 3+ days, show a gentle "Consider talking to a professional" card with no alarmist colour.

---

## 4. Sources

Competitors
- WHOOP pricing tiers: https://trackervs.com/pricing/whoop-pricing/ · https://lifestack.ai/blog/how-much-is-whoop-membership · https://www.whoop.com/je/en/membership
- Oura pricing: https://www.thepricer.org/how-much-does-the-oura-ring-cost/ · https://bestbuy.ca/en-ca/product/oura-ring-gen3-horizon-size-11-gold/17277758
- Welltory: https://adapty.io/paywall-library/welltory/ · https://mobihealthnews.com/node/143218 · https://www.bluestacks.com/campaign/com.welltory.client.android/en
- Bevel: https://lifestack.ai/blog/bevel-app-review · https://apps.apple.com/us/app/-/id6456176249 · https://lifestack.ai/blog/bevel-vs-athlytic
- Athlytic: https://apps.apple.com/us/app/athlytic-ai-fitness-coach/id1543571755 · https://ibikerun.substack.com/p/athlytic-app-review-iosapple-watch
- Calm / Headspace: https://lifestack.ai/blog/calm-pricing · https://www.choosingtherapy.com/headspace-vs-calm/ · https://carepaths.com/calm-app-vs-headspace/
- Breathwrk: https://www.choosingtherapy.com/breathwrk-app-review/ · https://apps.apple.com/us/app/-/id1481804500 · https://adapty.io/paywall-library/breathwrk/
- Open: https://apps.appfollow.io/ios/open-breathwork-meditation/1482725254?country=de
- Zero: https://apps.apple.com/app/zero-fasting-tracker/id1168348542 · https://www.garagegymreviews.com/equipment/zero
- MyFitnessPal / Cronometer: https://nutrola.app/en/blog/is-cronometer-gold-worth-the-money-2026 · https://nutrola.app/en/blog/calorie-tracker-pricing-guide-free-vs-premium-comparison-2026
- Lifesum: https://nutrola.app/en/blog/lifesum-review-2026 · https://recurdash.com/subscription-pricing/lifesum · https://apps.apple.com/us/app/lifesum-diet-macro-tracker/id286906691
- Lumen: https://www.tomsguide.com/reviews/lumen · https://www.wareable.com/health-tech/lumen-review · https://outliyr.com/lumen-metabolism-tracker-review
- Levels: https://levels.com/blog/how-much-does-levels-cost · https://support.levelshealth.com/article/355-139-how-much-does-levels-cost · https://bodysciencereview.com/blog/levels-cgm-continuous-glucose-monitor-review/
- Habitify: https://habitify.me/blog/free-habit-tracker-app · https://toolradar.com/tools/habitify/pricing · https://habi.app/insights/habitify-alternatives/
- Finch: https://makeheadway.com/blog/finch-app-review/ · https://www.internetmatters.org/advice/apps-and-platforms/wellbeing/finch/ · https://www.yogajournal.com/lifestyle/finch-self-care-app/
- Blueprint: https://apps.apple.com/us/app/-/id6467042093 · https://toolfinder.com/stacks/bryan-johnson · https://agetechworld.co.uk/news/blueprint-raises-us60m-for-longevity-platform/
- Cortisol apps: https://apps.apple.com/app/id6781436171 (Lower Cortisol: Calmer) · https://appshunter.io/ios/app/calmtide-cortisol-tracker/id6776101012 · https://www.capterra.co.uk/software/1099057/Cortisol · https://www.santelog.com/actualites-sante-nasdaq/cortisol-detox-app-supports-healthy-fat-loss-meal-plans-and-mindfulness · https://www.bustle.com/wellness/cortisol-level-test-eli-health-app-review

Design and accessibility
- Green nature vs green colour, stress study: https://agris.fao.org/search/en/records/65df48b263b8185d9cac0cd3
- WCAG 2.2 SC 2.5.8 target size: https://www.disabilityworld.org/toolkit/standards/wcag/2-5-8-target-size-minimum/ · https://dequeuniversity.com/rules/axe/4.8/target-size · https://www.disabilityworld.org/toolkit/standards/wcag/2-5-5-target-size-enhanced/
- W3C Understanding 2.5.8 (primary reference): https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- Fonts: https://fonts.google.com/specimen/Fraunces · https://fonts.google.com/specimen/Inter
