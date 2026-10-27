# Ebb backlog

The Living Bot takes items from the top of **Next** (see `LIVING_BOT.md`). The owner can reorder this list, add items, or mark a gated item `[approved]`.

## Next
1. **Spanish (es).** Add `i18n/es.js` with the same keys as `en.js` (Latin-American Spanish, wellness-only wording, Latin-friendly food examples), then add "es" to `LANGS` in `index.html` and to the service worker's `SHELL`.
2. **K-PSS-10 wording check.** Replace the Korean PSS-10 items with the validated K-PSS-10 text, and confirm PSS-10 licensing (Mapi Trust) before the paid launch.
3. **"I'm stressed right now" button** on Today. It opens Breathe with the 1-minute Quick reset already selected.
4. **Weekly recap card** on Progress, comparing this week with last week: average stress, sleep, habit %, and waist change.
5. **Phase-completion recap** on days 28, 56 and 84: before/after numbers plus the prompt "What helped most?", saved to a note.
6. **Edit and skip habits.** Hide habits that don't apply and add custom ones, stored as overrides in settings with a data migration.
7. **CSV export** of daily check-ins and weekly measurements.
8. **Pre/post breathing tension rating** (1–10), so each session shows its drop ("Tension 7 → 4").
9. **Gentle milestones:** 10 breathing sessions, 30 check-ins, first 1 cm off the waist. Celebrate quietly; never show a lost streak.
10. **Opt-in local reminders** using the Notification API, at most 3 a day and never after bedtime.

## Gated (owner must mark `[approved]` first)
- Anonymous privacy-friendly analytics (PostHog in anonymous mode or Plausible).
- Plus tier unlocked by a license key (Stripe/Lemon Squeezy/Toss payment links) — see `business/BUSINESS_PLAN.md`.
- Opt-in encrypted cloud backup (Supabase).
- AI weekly report (Claude API, aggregate data only, opt-in).
- Lab-test affiliate links at checkpoints, disclosed next to each link.

## Done
- v2: onboarding wizard (language, age/sex, units, schedule, lunch habit, existing activity and days, wearable, safety, personal summary); every habit timed from the user's day; training week built around the user's activity; English + Korean; lb/in support.
- v1: Today / Check-in / Breathe / Progress / Plan tabs, onboarding with a safety screen, tiered supplements, PSS-10, offline worker.
