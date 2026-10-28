# Install ARYLIDE on Android

## বাংলা: সরাসরি APK ইনস্টল

1. `arylide-holdings-universal.apk` ফোনে ডাউনলোড করুন।
2. **Files / My Files → Downloads** থেকে APK-টি খুলুন। Android অনুমতি চাইলে ওই Files/Chrome অ্যাপের জন্য **Install unknown apps / Allow from this source** চালু করে ফিরে এসে **Install** চাপুন।
3. ইনস্টল হলে **ARYLIDE Holdings** আইকনে ট্যাপ করুন। APK-এর ভেতরেই ওয়েবসাইট, Python সার্ভার ও SQLite ডেটাবেস আছে—Termux বা আলাদা ব্রাউজার চালু করতে হবে না।
4. Admin ব্যবহার করতে সাইটের নিচের **Admin panel** লিংকে যান। প্রথমবার নিজের email এবং অন্তত ১২ অক্ষরের ব্যক্তিগত password দিয়ে admin account তৈরি করুন। কোনো default password নেই।
5. Enquiry, referral, appointment এবং admin data এই ফোনের app-private storage-এ থাকে। সাধারণ app restart-এ থাকে; uninstall বা **Clear data** করলে মুছে যেতে পারে। Admin থেকে নিয়মিত CSV export করুন। বর্তমান build-এ Android auto-backup বন্ধ আছে।
6. আগের APK-এর signing certificate আলাদা হলে Android সরাসরি update দেবে না। CSV export করে পুরোনো app uninstall করে নতুনটি ইনস্টল করুন—তবে uninstall করলে পুরোনো app-এর local data মুছে যাবে। এই build একই project-local debug key ধরে রাখে; অজানা পুরোনো builds যাচাই ছাড়া compatible ধরে নেবেন না।

## English

- `arylide-holdings-universal.apk` is version **1.3.0 (versionCode 5)**, one debug-signed APK containing native Python runtimes for `armeabi-v7a`, `arm64-v8a`, `x86_64`, and `x86`. It declares **minimum Android API 21 (Android 5.0)** and **target API 34**. This covers those Android versions and ABIs; it cannot guarantee compatibility with every unusual device or modified Android build.
- The app embeds the ARYLIDE site, Python service, and SQLite database. It works offline for local enquiry/admin tasks; no Termux or separate browser is required.
- First admin setup is inside the app. Create your own password (12+ characters); none is preset.
- Local SQLite records survive normal app restarts and compatible updates. Android automatic backup/device transfer is disabled by the current manifest; uninstalling, clearing app data, a factory reset, or device loss can erase records. Export CSV regularly; separate installs do not synchronize.
- The project-local debug signing key matches the prior universal APK present in this workspace (SHA-256 certificate fingerprint `27:96:93:A7:04:D0:30:AF:4B:EC:84:70:43:0C:18:BE:BA:CF:1C:1E:C4:4B:C0:78:DA:6C:CF:05:18:04:0D:DC`). It is a development/debug key, not a private Play Store release key. Future sideload builds need the same key to update in place. The earlier arm64-only APK had a different certificate; if an installed APK rejects the update, export its leads, uninstall it, and then install the universal build.

## Scope and security notes

- This is a **local-first, single-device** build. Each phone has its own SQLite database; separate installs do not share leads. Shared customer traffic requires a company-controlled central HTTPS service, database, and privacy/security rules.
- Optional Telegram/N8N notifications are off unless a trusted server relay is configured. Bot tokens and private webhook URLs are not included in this APK or its browser code.
- No email or referral payment is sent automatically. Referral amounts are tracked in the admin workflow only.
- This is a debug-signed sideload build, not a Google Play release. Android may show its standard prompt for apps installed outside Play Store.
- The supplied screenshot was used as design guidance only and is not embedded; it contained private account details and an older reward amount. ARYLIDE-supplied branding/assets remain in the app.
- APK signing, manifest SDK range, and packaged ABI directories are checked during build. No Android phone/emulator is attached for an on-device installation test.
