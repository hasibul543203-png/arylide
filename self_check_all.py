import os
import sys
import json
import hashlib
import re

app_dir = r"C:\Users\Administrator\Desktop\aryland\app\arylide-full-app (5)"
frontend_dir = os.path.join(app_dir, "frontend")

def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def check_json(path):
    with open(path, "r", encoding="utf-8") as f:
        json.load(f)
    return True

print("=== STARTING FULL ZERO-DATA-LOSS SELF-CHECK ===")

# 1. SQLite Zero Data Loss Check
data_db = os.path.join(app_dir, "data", "arylide.sqlite3")
backend_db = os.path.join(app_dir, "backend", "data", "arylide.sqlite3")
expected_data_hash = "9bc1f4854184a015aa269a10e44fff3342583ceb1a61ce3ce8412585201b19b9"
expected_backend_hash = "d96d8d14e02aac7a75343b0afd7d0f20beaac6b9d224e72cc925601954d368ad"

curr_data_hash = sha256_file(data_db)
curr_backend_hash = sha256_file(backend_db)

assert curr_data_hash == expected_data_hash, f"data/arylide.sqlite3 changed! {curr_data_hash}"
assert curr_backend_hash == expected_backend_hash, f"backend/data/arylide.sqlite3 changed! {curr_backend_hash}"
print("✓ SQLite hashes 100% matched - 0 bytes altered!")

# 2. JSON files validation
json_files = [
    os.path.join(app_dir, "firebase.json"),
    os.path.join(app_dir, "config", "firebase.json"),
    os.path.join(app_dir, "vercel.json"),
    os.path.join(app_dir, "config", "vercel.json"),
    os.path.join(app_dir, ".firebaserc"),
    os.path.join(frontend_dir, "manifest.webmanifest"),
    os.path.join(app_dir, "backups", "sqlite-full-snapshot.json")
]

for jf in json_files:
    assert check_json(jf), f"Invalid JSON: {jf}"
    print(f"✓ Valid JSON: {os.path.basename(jf)}")

# 3. APP_SHELL Files Existence Check
with open(os.path.join(frontend_dir, "service-worker.js"), "r", encoding="utf-8") as f:
    sw_code = f.read()

assert "'arylide-pwa-v6.0.0'" in sw_code, "Service worker cache version must be v6.0.0"
assert "This private feature needs the ARYLIDE server" not in sw_code, "Old 503 error text still in service worker!"
print("✓ Service Worker v6.0.0 clean - 0 private server error text")

# Find APP_SHELL array
m = re.search(r"const APP_SHELL = \[(.*?)\];", sw_code, re.DOTALL)
assert m, "APP_SHELL not found"
shell_items = [item.strip().strip("'\"").split("?")[0] for item in m.group(1).split(",") if item.strip()]

for item in shell_items:
    if item in ["./", "./index.html", "./admin.html"]:
        continue
    clean_path = item.replace("./", "")
    full_path = os.path.join(frontend_dir, clean_path)
    assert os.path.exists(full_path), f"Missing APP_SHELL file: {clean_path}"

print(f"✓ All {len(shell_items)} APP_SHELL assets physically exist in frontend/")

# 4. 16 Admin Tabs & Panels in admin.html
with open(os.path.join(frontend_dir, "admin.html"), "r", encoding="utf-8") as f:
    admin_html = f.read()

tabs = ["dashboard", "activity-logs", "cms", "projects", "media", "videos",
        "social", "meetings", "enquiries", "referrals", "appointments",
        "landowners", "calculator", "users", "security", "ai"]

for t in tabs:
    assert f'data-tab="{t}"' in admin_html, f"Missing nav tab: {t}"
    assert f'id="panel-{t}"' in admin_html, f"Missing panel: panel-{t}"

print(f"✓ All {len(tabs)} tabs & panels intact in admin.html")

# 5. Check DOM Elements targeted in admin-cloud.js exist in admin.html
required_ids = [
    "adminAuthOverlay", "signInForm", "setupForm", "authEmail", "authPassword",
    "btnSignIn", "btnGoogleSignIn", "btnForgotPass", "btnToSetup", "setupName",
    "setupEmail", "setupPassword", "btnActivate", "btnGoogleSetup", "btnToSignIn",
    "authErrorMsg", "authSetupNotice", "adminHeaderEmail", "adminHeaderRole",
    "makeAdminCard", "addAdminForm", "newAdminEmail", "newAdminName", "newAdminRole",
    "adminsTableBody", "approvalsList", "projectCatalogList", "videoList",
    "socialForm", "calculatorForm", "meetingSettingsForm", "cmsForm"
]

for el_id in required_ids:
    assert f'id="{el_id}"' in admin_html, f"admin.html missing required element ID: {el_id}"

print(f"✓ All {len(required_ids)} interactive DOM elements verified in admin.html")

# 6. Check firestore.rules
with open(os.path.join(app_dir, "firestore.rules"), "r", encoding="utf-8") as f:
    rules = f.read()

assert "match /settings/admins" in rules, "Missing settings/admins rule"
assert "match /cms/public" in rules, "Missing cms/public rule"
assert "match /booked_slots/{slotId}" in rules, "Missing booked_slots rule"
assert "match /referral_codes/{code}" in rules, "Missing referral_codes rule"
assert "isOwnerOrSuperAdmin()" in rules, "Missing isOwnerOrSuperAdmin rule"
print("✓ firestore.rules verified with Multi-Admin ACL & public read")

print("=== ALL SELF CHECKS PASSED 100%! ===")
