# Run ARYLIDE on a phone

## Recommended: install the Android APK

For a one-tap app experience, download `arylide-holdings-universal.apk` to an Android phone, tap it in **Files / Downloads**, allow **Install unknown apps** for the selected file app if prompted, and install. Open the **ARYLIDE Holdings** icon. The universal APK includes the website, Python backend and private SQLite store—no Termux or browser is required.

The APK includes `armeabi-v7a`, `arm64-v8a`, `x86`, and `x86_64` native runtimes and declares Android 5.0 / API 21 or newer. On first use, scroll to **Admin panel** and create your own admin account and password (minimum 12 characters). There is no preset password. Local records persist across normal app restarts and compatible updates; export CSV before clearing app data or uninstalling. Android device backup is enabled for the local database but is subject to the device’s backup settings.

See `ANDROID-APK-INSTALL.md` for step-by-step Bengali instructions and scope notes.

## Alternative: run the source bundle with Android Termux

Use this only if you prefer to run the Python server from source instead of installing the APK.

1. Download `arylide-full-app.zip` and extract it to `Download/arylide-full-app/`.
2. Install **Termux** (F-Droid is recommended), open it, then run:

   ```sh
   termux-setup-storage
   pkg update
   pkg install python
   cd ~/storage/downloads/arylide-full-app
   python run.py --create-admin --email admin@arylideholdings.com
   ```

   Choose a private password of at least 12 characters when prompted. Do not reuse any password shown in screenshots or chat.

3. Start the local app:

   ```sh
   python run.py --host 127.0.0.1 --port 4173
   ```

4. In Chrome on the **same phone**, open `http://127.0.0.1:4173/`. Use `/admin` to sign in. New enquiries are saved in `data/arylide.sqlite3`.
5. To install the PWA shortcut, use Chrome’s menu → **Install app** / **Add to Home screen**. Keep Termux running while submitting forms or using Admin; stopping the Python server disables those features until it is restarted.

The local app stores data in its own database. Different APKs or downloads do **not** share enquiries, referral codes, or admin data. Shared customer use requires one central HTTPS server and database. The contact form does not send email automatically.

## Windows / macOS / Linux

Install Python 3.10 or newer; no third-party packages are required. In a terminal in the extracted app folder:

```sh
python run.py --create-admin
python run.py --host 127.0.0.1 --port 4173
```

Open `http://127.0.0.1:4173/`; the admin page is at `/admin`. For a phone to preview the same computer over Wi‑Fi, bind to `0.0.0.0` and use the computer’s LAN IP. Do not expose the local admin to the public internet.

## iPhone / iPad

Use a hosted HTTPS URL in Safari and choose **Share → Add to Home Screen**. The public page can cache for offline viewing, but the Python backend and database need a server; the standalone APK is Android-only.
