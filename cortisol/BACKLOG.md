# Ebb backlog

The Living Bot takes items from the top of **Next** (see `LIVING_BOT.md`). The owner can reorder this list, add items, or mark a gated item `[approved]`.

## Next
1. **Korean language toggle.** Make the app bilingual EN/한국어 like the brew timer. Start with the Today and Check-in tabs.
2. **"I'm stressed right now" button** on Today. It opens Breathe with the 1-minute Quick reset already selected.
3. **Weekly recap card** on Progress, comparing this week with last week: average stress, sleep, habit %, and waist change.
4. **Phase-completion recap** on days 28, 56 and 84: before/after numbers plus the prompt "What helped most?", saved to a note.
5. **Edit and skip habits.** Hide habits that don't apply and add custom ones, stored as overrides in settings with a data migration.
6. **Unit toggle** for cm/in and kg/lb (store metric, convert for display).
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
- v1: Today / Check-in / Breathe / Progress / Plan tabs, onboarding with a safety screen, tiered supplements, PSS-10, offline worker.
