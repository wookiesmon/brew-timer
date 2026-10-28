# 06 — Health Sync: Apple Shortcuts bridge (and Android)

*Health Integrations team · researched 2026-10-28*

Ebb is an offline PWA with no backend. A web page cannot call HealthKit or Health Connect. The bridge is an Apple Shortcut the user builds once. It reads Apple Health, builds a small JSON text, copies it to the clipboard, and Ebb reads it with **Paste from Shortcut** (`applySync()` in `index.html`).

> **Research limits.** In this session, `support.apple.com` and `matthewcassinelli.com` could not be fetched directly. They are blocked by the sandbox network settings and would need to be allowed to re-check. Findings come from search-result summaries of those pages, Apple Developer Forums, Six Colors, iMagazine, Korean blogs and Apple Community KR, plus the team's working knowledge of the Shortcuts editor. Every action name marked ⚠ must be checked on a real iPhone before release.

---

## 1. The Shortcut, action by action

### 1.1 Actions and parameters (English UI, iOS 18 / iOS 26)

| # | Action | Parameters used | Confidence |
|---|---|---|---|
| 1 | **Date** | Current Date | High |
| 2 | **Adjust Date** | Operation **Get Start of Day** → rename `Today`; second copy **Subtract 1 days** → `Yesterday` | High (the Get Start of Day/Week/Month operations exist) |
| 3 | **Format Date** | Date Format **Custom**, format string `yyyy-MM-dd` (lower-case `yyyy`, `dd`; `DD` = day-of-year, `YYYY` = week-year), Time Format **None** | High |
| 4 | **Find Health Samples** | `Type` (Steps, Sleep Analysis, Heart Rate Variability, Resting Heart Rate, Weight, Waist Circumference); filters on `Start Date` / `End Date` / `Value` / `Duration` / `Source`; **Sort by**, **Order** (Latest First / Oldest First), **Limit**; optional **Group By** (Hour/Day/Week/…) | High for the action and its sort/limit/group options (Cassinelli action page: "allows for sorting, reordering, grouping by time periods, and limiting"). Medium for the exact filter labels. |
| 5 | **Calculate Statistics** | **Sum** (steps, sleep minutes), **Average** (HRV, RHR) | High |
| 6 | **Get Details of Health Sample** | Type, **Value**, **Unit**, **Start Date**, **End Date**, **Duration**, Source, Name | High (Cassinelli action page lists type, value, unit, dates, duration, source, name) |
| 7 | **Repeat with Each** / **End Repeat** | Over the sleep samples; output = Repeat Results | High |
| 8 | **Get Time Between Dates** | Start Date → End Date **in Minutes** | High |
| 9 | **Calculate** | ÷ 60 | High |
| 10 | **Round Number** | **Ones Place** (steps, HRV, RHR), **Tenths** (sleep) | Medium on the exact label wording |
| 11 | **Text** | The JSON template with variables | High |
| 12 | **Copy to Clipboard** | Input: Text (optional Local Only / Expire At) | High |
| 13 | **Show Notification** | `Copied for Ebb` | High |

Data-type names: in the Shortcuts type picker, HealthKit **Body Mass** shows as **Weight**, and **Step Count** shows as **Steps**. ⚠ Confirm the exact list labels on device.

### 1.2 Recipe per field

- **date**: `Today` = **Adjust Date** (Get Start of Day) of Current Date; `Yesterday` = `Today` − 1 day; **Format Date** `yyyy-MM-dd` of `Yesterday`. **The date in the JSON is yesterday.** Steps are yesterday's full-day total. Sleep is the night that ended this morning. HRV/RHR are 7-day averages ending now.
- **steps**: Find Health Samples, Type Steps, Start Date is after `Yesterday` AND Start Date is before `Today` → Calculate Statistics Sum → Round Number. This gives a true calendar-day total. A "today" filter would give a near-zero count at 8:30 AM. Steps from multiple sources (Watch + iPhone) can be double-counted by a raw sum. The Health app de-duplicates, a raw sample sum does not. ⚠ Compare with the Health app on a device that has both a Watch and an iPhone. If it double-counts, add a filter **Source is** \<the Apple Watch\>.
- **sleep**: see §1.3.
- **hrv**: Type Heart Rate Variability, Start Date is in the last 7 days → Average → Round Number. The values are SDNN in ms.
- **rhr**: same, with Resting Heart Rate (count/min).
- **weight / weightUnit**: Type Weight, Sort by Start Date, Order Latest First, Limit 1 → Get Details → **Value**, and Get Details → **Unit** ("lb" or "kg", following the user's Health unit settings). Ebb converts lb with `startsWith("lb")`.
- **waist / waistUnit**: Type Waist Circumference, same pattern; unit "in" or "cm". Ebb converts with `startsWith("in")`.

### 1.3 Sleep Analysis: the approach chosen

Facts:
- A night is stored as **many short category samples**, not one value (iMagazine; Apple `HKCategoryValueSleepAnalysis` docs). The asleep stages (Core, Deep, REM, Asleep Unspecified) partition the night and don't overlap each other. **In Bed** samples overlap them. Summing everything double-counts.
- Since watchOS 11 / iOS 18, Apple Watch **no longer writes In Bed samples** (Apple DTS engineer, Developer Forums 766977). Third-party trackers and the iPhone still may.
- Summing the asleep-stage samples matches the Health app to within ~2 minutes. Apple's reply attributes the remaining difference to "sleep day" boundaries (6 pm–6 pm) and naps (Developer Forums 776851).

Chosen recipe:
1. Find Health Samples, Type **Sleep Analysis**, filters (match **All**): **End Date is in the last 12 hours**, **Value is not In Bed**, **Value is not Awake**. This keeps Core/Deep/REM/Asleep without listing each one. It also works with older "Asleep"-only data from non-Watch sources.
2. **Repeat with Each** sample: Get Details → Start Date, Get Details → End Date, **Get Time Between Dates** in **Minutes**.
3. After End Repeat: **Calculate Statistics → Sum** of Repeat Results, **Calculate ÷ 60**, **Round Number → Tenths**.

Why not *Get Details → Duration → Sum*? It needs fewer actions, but Duration comes back as a duration/measurement. Its unit and its text form inside a Text action ("7 hr 12 min" vs a number) could not be confirmed. Get Time Between Dates always returns a plain number in the unit you choose. A Six Colors 2019 sleep shortcut uses the same method. Cost: a long night with 40–80 samples loops 40–80 times, which takes about a second.

The 12-hour window assumes the Shortcut runs in the morning. At 8:30 AM it covers 8:30 PM onward. Running it in the evening would miss the previous night. Two sources recording sleep (e.g. Watch + AutoSleep/Oura) would double-count. ⚠ Test this case. The fix is a **Source is** filter.

### 1.4 Building the JSON, and missing data

Options considered:
- **Dictionary → (implicit JSON)**: valid JSON when copied, but a Number field fed by an empty variable behaves unpredictably (0 or empty).
- **Text with bare numbers** (`"hrv":[HRV]`): a missing sample gives `"hrv":,`, which is **invalid JSON**, and the whole paste fails.
- **If [variable] has any value / Otherwise**: correct, but adds 3 actions × 6 fields, which is too long for beginners.
- **Chosen: Text with every value in quotes** (`"hrv":"[HRV]"`). A missing value becomes `""`, so the JSON is always valid. Ebb's parser already does `+r.hrv` (→ 0 for `""`). `cleanHealth()` drops out-of-range values, and the weight/waist branch skips falsy values. **No Ebb code change is needed** for quoted numbers.

Ebb parser follow-ups (not in scope here; recommended):
1. Shortcuts may render large numbers with a grouping separator (`8,123`). Some locales also use a decimal comma (`7,2`). `+"8,123"` is `NaN`, so steps would be silently dropped. The fix is to normalise strings before `+`: remove spaces/thin spaces, and treat a lone comma followed by 1–2 digits as a decimal point. ⚠ Test with a German/French region setting.
2. The record is keyed to `date` = **yesterday**, but `syncResult()` builds its toast from today's `health` entry, so the toast shows a bare count. It should read the synced date. Also decide whether last night's sleep belongs to yesterday or today in Ebb's model. Today the whole record lands on yesterday.

### 1.5 Copy, notify, paste

**Copy to Clipboard** then **Show Notification** "Copied for Ebb". In Ebb, `navigator.clipboard.readText()` on iOS Safari/PWA shows a system **Paste** callout the user must tap. If it's denied, Ebb falls back to the manual text box. If Universal Clipboard is on, the text also appears on the user's Mac, which is harmless.

---

## 2. Korean (ko-KR) action names

Search for Korean UI strings was thin. Apple's ko-KR Shortcuts guide pages did not surface in search and support.apple.com could not be fetched.

| English | Korean | Status |
|---|---|---|
| Shortcuts (app) | 단축어 | ✅ App Store KR listing |
| Find Health Samples | 건강 샘플 찾기 | ✅ Apple Community KR thread 255835147 uses it |
| Automation tab / Personal Automation | 자동화 / 개인용 자동화 | ✅ extrememanual.net (iOS 26) |
| Time of Day | 특정 시간 | ✅ extrememanual.net |
| Daily | 매일 | ✅ extrememanual.net |
| Run After Confirmation → Run Immediately | 실행 후 확인 → 즉시 실행 | ✅ extrememanual.net (iOS 26) |
| Calculate Statistics | 통계 계산 | ⚠ unconfirmed (founder-supplied, plausible) |
| Copy to Clipboard | 클립보드에 복사 | ⚠ unconfirmed (founder-supplied, high prior) |
| Text | 텍스트 | ⚠ unconfirmed (high prior) |
| Format Date | 날짜 포맷 | ⚠ unconfirmed (founder-supplied) |
| Show Notification | 알림 보기 | ⚠ unconfirmed (founder-supplied) |
| Date / Adjust Date / Get Start of Day | 날짜 / 날짜 조정 / 하루의 시작 가져오기 | ⚠ unconfirmed |
| Get Details of Health Sample | 건강 샘플의 세부사항 가져오기 | ⚠ unconfirmed |
| Repeat with Each / End Repeat / Repeat Results | 각 항목 반복 / 반복 종료 / 반복 결과 | ⚠ unconfirmed |
| Get Time Between Dates | 날짜 사이의 시간 가져오기 | ⚠ unconfirmed |
| Calculate | 계산 | ⚠ unconfirmed (high prior) |
| Round Number (Ones Place / Tenths) | 숫자 반올림 (일의 자리 / 소수점 첫째 자리) | ⚠ unconfirmed |
| Sum / Average | 합계 / 평균 | ⚠ unconfirmed (high prior) |
| Custom (date format) | 사용자 설정 | ⚠ unconfirmed |
| Sort by / Order Latest First / Limit | 정렬 기준 / 최신 항목 먼저 / 제한 | ⚠ unconfirmed |
| Steps / Sleep Analysis / HRV / Resting HR / Weight / Waist Circumference | 걸음 / 수면 분석 / 심박 변이 / 안정 시 심박수 / 체중 / 허리둘레 | ⚠ unconfirmed. "안정 시 심박수" matches Ebb's own copy; the HRV label may be "심박변이도". |
| In Bed / Awake | 침대에 있음 / 깨어 있음 | ⚠ unconfirmed |
| Notify When Run | 실행 시 알림 | ⚠ unconfirmed |
| Turn On All / Allow | 모두 켜기 / 허용 | ⚠ unconfirmed |

Mitigation in `sync.ko.js`: step 1 tells users to search by the core word (건강, 날짜) if a name differs slightly. Before launch, have a Korean-locale iPhone screenshot each action and fix the table.

---

## 3. Daily Personal Automation

- **Path (iOS 17+/18/26)**: Shortcuts → **Automation** tab → **+** / **New Automation** → **Time of Day** → time (8:30 AM) + **Daily** → choose **Run Immediately** (default is **Run After Confirmation**) → **Next** → pick the shortcut. The **Notify When Run** toggle exists for some triggers. Cassinelli's iOS 17 beta write-up says automations now notify when they run, so the user sees a banner either way.
- In iOS 17, Apple replaced the old "Ask Before Running" switch with the Run Immediately / Run After Confirmation choice. Before iOS 17, Apple's guide said Time of Day was one of the triggers that could run without asking. Some actions in a shortcut may separately ask for confirmation.
- **First-run permissions**: the first time **Find Health Samples** runs for a type, iOS shows the Health access sheet ("Shortcuts would like to access…") listing each requested data type (Steps, Sleep, HRV, Resting HR, Weight, Waist), with **Turn On All** and **Allow**. In practice the sheet appears per data type as each action first runs, so a 6-type shortcut may show it several times on the first run. That's why the guide tells users to **run it manually once before automating**. A permission prompt can't be answered by an automation that runs while the phone is unattended. Permissions can be changed later in Settings → Health → Data Access & Devices → Shortcuts. Clipboard *writing* needs no prompt.
- **⚠ Locked-device caveat**: HealthKit data is encrypted while the iPhone is locked, and reads fail or return nothing. At 8:30 AM with the phone in a pocket, the automation may produce empty values. The quoted-value design means the JSON stays valid and Ebb reports "Nothing to import". Test it locked and unlocked. Picking a time when the phone is usually in use is the practical advice.
- **Clipboard lifetime**: the copied JSON stays until the user copies something else, so they must paste into Ebb before copying anything.

---

## 4. Sharing a ready-made iCloud link later

- **Allowed**: yes. Any user can share a shortcut as an `https://www.icloud.com/shortcuts/<id>` link (Share → Copy iCloud Link). Recipients see a description and the action list before tapping Add Shortcut. The owner can **Stop Sharing**. Requirements: iCloud sync for Shortcuts on the sharer's device. Apple does not review these links. Only the curated Gallery is Apple-reviewed.
- **Signed**: since iOS 15 / macOS 12, shared shortcuts and `.shortcut` files are **signed** (macOS has a `shortcuts sign` CLI with "anyone" / "people-who-know-me" modes). Signing identifies the sharer and lets the file be imported. It is not an App-Store-style review.
- **Untrusted-shortcuts setting**: Apple's older guide versions (Shortcuts 2.x–4.x, iOS 12–14) say non-Gallery shortcuts are "untrusted" and need **Settings → Shortcuts → Allow Untrusted Shortcuts**. From iOS 15, as far as we know, this toggle **no longer exists**, and signed iCloud links import directly after the user reviews the actions. ⚠ Could not confirm on a current Apple page this session. Check on iOS 26.
- **Privacy prompts still apply per user**: the importer still sees the Health permission sheet on first run, and may see a "Allow … to share data" prompt if the shortcut sent data out (ours doesn't).
- **Recommendation**: yes, publish an official iCloud link once the shortcut is tested. Keep the manual guide as a fallback and for transparency. Notes:
  - A shared link is tied to the publisher's Apple ID name, so use a company Apple ID.
  - Health types are referenced generically, so they import fine.
  - Unit settings (lb/kg) come from each user's own Health settings, not the sharer's.
  - Localised users see action names in their own language automatically, which removes the Korean-name risk for link users.
  - Keep the shortcut free of hard-coded personal data.
  - Version it (e.g. add `"v":1` later).

---

## 5. Android in 2026: honest summary

- **Health Connect is on-device only, with no web API.** A PWA cannot read it. Google's comparison guide splits integration into **Health Connect** (on-device Android) and the cloud **Google Health API** (web/server, OAuth). The cloud route needs a backend to hold tokens, which Ebb doesn't have.
- **Bridges that exist:**
  - **Tasker + TaskerHealthConnect** (community plugin, GitHub-only, author says it's unstable): it can read Health Connect records as JSON, and Tasker can then build Ebb's JSON and set the clipboard. This is a power-user path, too fiddly to document for mainstream users.
  - **Automate / MacroDroid**: no reliable first-party Health Connect blocks that we could find.
  - **Samsung Health**: personal data export (Settings → Download personal data) produces CSVs by hand. It isn't an automated bridge and the format changes.
  - **Garmin / Oura / WHOOP / Fitbit**: CSV exports from their web dashboards (manual), or cloud APIs that all require OAuth plus a server. Not viable for a no-backend app.
- **What to tell Android users today**: enter the numbers manually once a week (the weekly check-in already has the fields). Automatic sync comes with the native app.

---

## 6. Native apps later: recommendation

Wrap the existing PWA in **Capacitor** and add a health plugin:
- **@capgo/capacitor-health** (free, MPL-2.0, v8.6–8.7 on npm in 2026): HealthKit + Health Connect. It has `requestAuthorization`, `readSamples`, `queryAggregated` (sum/avg by day) and `queryWorkouts`. Health Connect needs Android 8.0+ (API 26).
- **@capawesome-team/capacitor-health** (announced 2026-08-26, Insiders/paid): about 20 data types, including sleep, with an `aggregate()` API bucketed by hour/day/week/month. On iOS, read permission status is never reported as granted (a HealthKit privacy design), so the app must treat "no data" as "maybe not allowed".

Notes:
- iOS needs `NSHealthShareUsageDescription` in Info.plist and App Review justification for health use.
- Google Play needs a Health Connect permissions declaration and a privacy policy.
- Both platforms allow on-device-only processing, which keeps Ebb's no-server promise.
- Keep the JSON shape (`{"ebb":1,…}`) as the internal contract, so the native plugin and the Shortcut both feed `applySync()`.

---

## Sources

- Matthew Cassinelli, *Find Health Samples* / *Get Details of Health Sample* action pages and *How far did I walk today?* — https://matthewcassinelli.com/shortcuts/how-far-did-i-walk-today/
- Matthew Cassinelli, *All Automations Now Run Immediately In Shortcuts (Notifications Required)* — https://matthewcassinelli.com/automations-run-immediately-shortcuts-notifications
- Apple, Shortcuts User Guide: enable/disable personal automation — https://support.apple.com/guide/shortcuts/apd602971e63/ios
- Apple, Shortcuts User Guide: share shortcuts (iCloud link, Stop Sharing) — https://support.apple.com/guide/shortcuts/apdf01f8c054/ios
- Apple, Shortcuts User Guide: enable shared/untrusted shortcuts (older versions) — https://support.apple.com/en-gb/guide/shortcuts/apdfeb05586f/3.5/ios
- How-To Geek, *Allow Untrusted Shortcuts greyed out* — https://www.howtogeek.com/699397/how-to-fix-allow-untrusted-shortcuts-grayed-out-on-iphone-or-ipad/
- Apple Developer Forums, *Sleep Samples sum off by 2 minutes* — https://developer.apple.com/forums/thread/776851
- Apple Developer Forums, *Sleep Analysis inBed sample not recorded on Apple Watch in iOS 18* — https://developer.apple.com/forums/thread/766977
- Apple, `HKCategoryValueSleepAnalysis` — https://developer.apple.com/documentation/healthkit/hkcategoryvaluesleepanalysis
- Six Colors, *Simple sleep tracking with Shortcuts* — https://sixcolors.com/post/2019/02/simple-sleep-tracking-with-shortcuts
- iMagazine, *Kurs Siri Shortcuts cz. 6 (sleep time)* — https://imagazine.pl/2018/10/05/kurs-siri-shortcuts-czesc-6-sprawdzanie-czasu-snu-przez-siri
- Leancrew, *A bug that isn't and an error that is* (custom date formats in Shortcuts) — https://leancrew.com/all-this/2020/09/a-bug-that-isnt-and-an-error-that-is/
- Apple Community KR, 단축어사용시 건강 데이터 추출방안 (건강 샘플 찾기) — https://discussionskorea.apple.com/thread/255835147
- extrememanual.net, 아이폰 특정 시간에 앱 실행하는 단축어 자동화 설정 방법 (개인용 자동화 / 특정 시간 / 즉시 실행, iOS 26) — https://extrememanual.net/60959
- Google, Health Connect vs Google Health API comparison guide — https://developer.android.com/health-and-fitness/health-connect/comparison-guide
- TaskerHealthConnect (GitHub) — https://github.com/RafhaanShah/TaskerHealthConnect
- Capgo, `@capgo/capacitor-health` docs — https://capgo.app/docs/plugins/health/ and README https://cdn.jsdelivr.net/npm/@capgo/capacitor-health@8.7.0/README.md
- Capawesome, *Announcing the Capacitor Health plugin* — https://capawesome.io/blog/announcing-the-capacitor-health-plugin/
