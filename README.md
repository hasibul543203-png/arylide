# ARYLIDE Holdings Limited — mobile-first app, website, and local CRM

A Bangla-default/English-toggle ARYLIDE app experience served by the local Python/SQLite backend. It includes project details and galleries, map links, sector filtering, a bilingual investment calculator, a video/social manager, meeting booking and customer meeting management, Firebase-ready accounts, and an expanded admin dashboard. ARYLIDE branding remains distinct from Jolshiri Abashon authority matters.

## Current deliverables

- **Android:** `arylide-holdings-universal.apk`, version 1.3.0 (versionCode 5), one debug-signed universal APK for `armeabi-v7a`, `arm64-v8a`, `x86_64`, and `x86`; min SDK 21, target SDK 34. It bundles the current app/site, Python 3.11 service, and SQLite. The project-local debug certificate matches earlier compatible sideload builds; this is not a Play Store signing key. APK signing, package metadata, and all four ABI libraries were verified. No physical Android device/emulator was available for installation testing.
- **Windows:** `desktop-app/` contains the Electron source and the current website/server files in `desktop-app/site/`. A regenerated `ARYLIDE-Setup.exe` is **not present in this workspace**.

First admin setup asks the owner to create a private email/password (12+ characters); no shared or hard-coded password is embedded. Local data persists across ordinary app restarts. Uninstalling, clearing app data, a factory reset, or device loss can erase it; export CSV regularly. Separate SQLite installs do not synchronize.

## Local build/run

Requires Python 3.10+ for the standalone server; no third-party Python packages are required.

```sh
python run.py --create-admin
python run.py --host 127.0.0.1 --port 4173
```

Open `http://127.0.0.1:4173/`; the admin panel is at `/admin.html` (`/admin` remains compatible). To reset an admin password, stop the server and run:

```sh
python run.py --reset-admin --email admin@arylideholdings.com
```

The database is `data/arylide.sqlite3`. Keep it private and back it up with the server stopped.

## Product features

- Bangla is the default; the English toggle is stored in `i18n.js` and remembered by the app.
- `/project/[id]` details with an image gallery, general-area map, editable price/area/amenities, and booking action; sector filtering shows only projects assigned to that sector.
- Company figures are kept as supplied: **3+ projects**, **3 completed**, **30+ clients**, **2 years of trust**, **51,000 sft built**, and **27,394,800 sft vision**.
- Calculator defaults are editable in Admin. Verified example: 2,850 sft × ৳8,500 = ৳24,225,000; 50% down = ৳12,112,500; 36 monthly installments ≈ ৳336,458.33; 14% compound growth over 3 years ≈ ৳35,890,403.40 future value and ৳11,665,403.40 profit.
- Two-step mobile meeting calendar: past days, Fridays by default, other off-days, and booked slots are unavailable. It collects attendee/project details and saves to local SQLite; CSV export, status actions, contact links, monthly agenda, and working-hours/slot settings are in Admin. `/my-meetings` supports cancel/reschedule using the local record's management token.
- Expanded admin tabs: project CMS, referrals, appointments, all enquiries, landowner enquiries, meetings/calendar, bilingual video library, social links/approved post embeds, and calculator assumptions.
- Firebase is optional and currently unconfigured. To enable it, fill the **public identifiers only** in `config.js`, enable the desired Auth providers and authorized domains in Firebase, and set restrictive Firestore rules. Once all required Firebase identifiers are present, the Python service verifies Firebase ID tokens with Identity Toolkit before allowing booking/cancellation/rescheduling. Firestore user/meeting writes require project rules and connectivity. Without Firebase configuration, local-first booking remains available without account login. Firebase/Auth/Firestore flows have not been tested against a supplied live project.
- Telegram/N8N notification relay remains server-side only; no bot token or private webhook secret is shipped in browser JavaScript. Optional SMS delivery is not configured.
- Homepage post embeds allow Facebook and YouTube frames through the server's CSP. Project/social URLs are editable; unverified company URLs or project facts should remain blank until supplied.
- Referral payment amounts are tracked only; no automatic payment or email/SMS is sent.

## Hosting and data scope

Each local app/website deployment has its own SQLite database. Separate installs do not share leads, admin accounts, or live slot availability. Firebase client writes do not turn local SQLite/admin availability into a shared backend. For shared customer traffic, deploy one company-controlled HTTPS service with persistent storage, backups, restrictive authorization rules, and a privacy/retention policy. The local server defaults to `127.0.0.1`; do not expose it publicly without a secure deployment plan. For a trusted HTTPS reverse proxy, set `ARYLIDE_COOKIE_SECURE=1`.

The app shell can be cached for offline viewing. Form submissions, meetings, Auth, and Admin require the local server; Firebase and external map/social embeds additionally need internet. No automatic payments are enabled.

## Source and build notes

- `arylide-full-app.zip` — current local website/server source, assets, and setup notes.
- `arylide-android-source.zip` — Android Studio/Gradle source and development-only debug key; do not use that key for a public release.
- `android-app/` — Android Studio/Gradle project; see its README for JDK/SDK and the universal APK build.
- `desktop-app/` — Electron source; the `site/` folder is staged, but a Windows Python runtime/installer build is not included here.
- `SOURCES.md` — external references and data provenance.
- `ANDROID-APK-INSTALL.md` — Android installation instructions (English and Bengali).
- `NOTIFICATIONS-SETUP.md` — secure optional relay configuration.
- `PHONE-SETUP.md` — Termux/PWA and iOS notes.
- `ODOO-UPDATE-PACK.md` — separate, paste-ready Odoo website update material; no live Odoo edits were made.
