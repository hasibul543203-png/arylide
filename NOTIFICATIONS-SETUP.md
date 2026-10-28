# Optional lead notifications

The app saves referrals, appointments, and enquiries to its local SQLite database first. It also mirrors the submitted records to browser localStorage under `aryl_refs`, `aryl_appointments`, and `aryl_enquiries`.

Telegram and N8N notifications are intentionally disabled in the distributed APK/EXE until configured on a trusted, company-controlled server. `config.js` contains the requested empty browser settings object only. **Never paste a Telegram bot token or private webhook URL into `config.js`, homepage JavaScript, a public repository, or a distributed APK/EXE**: users can inspect and extract those values.

To enable server-side notifications in a protected Python deployment, set these environment variables for the server process:

- `ARYLIDE_TELEGRAM_BOT_TOKEN`
- `ARYLIDE_TELEGRAM_CHAT_ID`
- `ARYLIDE_N8N_WEBHOOK_URL` (must be HTTPS)

When configured, the server sends Telegram `sendMessage` notices such as `🔥 New Lead: Buyer Name - 01XXXXXXXXX`, and posts the submitted record to N8N. Notifications are best-effort and do not block or undo a locally saved form if the external service is unavailable. Keep credentials in server environment secrets, restrict who can configure them, and use HTTPS for any hosted service.

For the packaged offline-first app, records stay on that device. No cloud sync or notification relay is active by default; configure a company-owned hosted relay before using shared customer traffic.
