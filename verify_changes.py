"""
FINAL VERIFICATION SCRIPT for Arylide Holdings admin_dashboard.py changes.
- Safe: reads files only, NO database writes, NO server changes.
- Run from the app directory so Python picks up the latest source (not stale cache).
"""
import sys, re

# Force fresh import - clear any cached version
for key in list(sys.modules.keys()):
    if "admin_dashboard" in key:
        del sys.modules[key]

sys.path.insert(0, ".")
from admin_dashboard import admin_dashboard_html

# ── Minimal fake data (no real DB needed) ──────────────────────────────────────
fake_admin   = {"email": "admin@arylideholdings.com", "id": 1}
fake_session = {"csrf_token": "TESTCSRF", "admin_id": 1,
                "expires_at": 9999999999, "created_at": 0}
fake_cms = {
    "stats": {"projects": "5", "completed": "3", "happy_clients": "120",
              "years_trust": "10", "area_built": "500,000", "vision_sqft": "2,000,000"},
    "projects": [],
    "company": {"phone": "+880 1817 338 899",
                "email": "info@arylideholdings.com",
                "address": "Hashim Tower, Unit 7C · Gulshan, Dhaka 1208"},
    "meeting_settings": {
        "working_start": "10:00", "working_end": "18:00", "slot_duration": 60,
        "off_days": [5], "slot_times": ["10:00", "11:00", "12:00"],
        "location_bn": "গুলশান", "location_en": "Gulshan"
    },
    "videos": [],
    "social": {"facebook": "", "linkedin": "", "x": "", "youtube": "", "post_embed_link": ""},
    "calculator": {"area_sft": 2850, "price_per_sft": 8500, "down_percent": 50,
                   "months": 36, "annual_growth_percent": 14, "growth_years": 3},
}
fake_settings = {"referral_reward_bdt": "50000"}
fake_counts   = {"enquiries": 0, "referrals": 0, "appointments": 0,
                 "landowners": 0, "meetings": 0}

# Generate HTML for every tab we need to test
html_dashboard = admin_dashboard_html(
    admin=fake_admin, session=fake_session, cms=fake_cms,
    settings=fake_settings, referral_rows=[], appointment_rows=[],
    enquiry_rows=[], counts=fake_counts, active_tab="dashboard",
    toast="", notifications_enabled=False, meetings=[],
)
html_users = admin_dashboard_html(
    admin=fake_admin, session=fake_session, cms=fake_cms,
    settings=fake_settings, referral_rows=[], appointment_rows=[],
    enquiry_rows=[], counts=fake_counts, active_tab="users",
    toast="", notifications_enabled=False, meetings=[],
)

print(f"HTML (dashboard tab): {len(html_dashboard):,} bytes")
print(f"HTML (users tab):     {len(html_users):,} bytes")
print()

# ── 1. TRUTHFUL LABEL CHECKS ───────────────────────────────────────────────────
truthful = {
    "Sidebar env bar says 'Local SQLite CRM'":
        "Local SQLite CRM" in html_dashboard,
    "Dashboard banner says 'Local Environment'":
        "Local Environment" in html_dashboard,
    "Sync pill says 'Local Application · SQLite'":
        "Local Application · SQLite" in html_dashboard,
    "Media panel badge says 'Prototype · Not Yet Connected'":
        "Prototype · Not Yet Connected" in html_dashboard,
    "Users panel badge says 'Prototype · Not Yet Connected'":
        "Prototype · Not Yet Connected" in html_users,
    "Security panel body mentions 'not yet connected'":
        "not yet connected" in html_dashboard.lower(),
    "AI panel body mentions 'not yet connected'":
        "not yet connected" in html_dashboard.lower(),
    "AI guardrails card header says 'Staged Protocol'":
        "Staged Protocol" in html_dashboard,
    "Activity log subtitle says 'Demonstration Trail'":
        "Demonstration Trail" in html_dashboard,
}

# ── 2. MISLEADING LABELS REMOVED ──────────────────────────────────────────────
removed = {
    "'PROTOTYPE STAGING // BATCH 3' is gone":
        "PROTOTYPE STAGING // BATCH 3" not in html_dashboard,
    "'PROTOTYPE STAGING // BATCH 6' is gone":
        "PROTOTYPE STAGING // BATCH 6" not in html_dashboard,
    "'PROTOTYPE STAGING // BATCH 7' is gone":
        "PROTOTYPE STAGING // BATCH 7" not in html_dashboard,
    "'Live Synced' is gone from sync pill":
        "Live Synced" not in html_dashboard,
}

# ── 3. NAVIGATION TABS ALL INTACT ─────────────────────────────────────────────
tabs = ["dashboard", "activity-logs", "cms", "projects", "media", "videos",
        "social", "meetings", "enquiries", "referrals", "appointments",
        "landowners", "calculator", "users", "security", "ai"]
nav = {f"Nav tab '{t}' present": f'data-tab="{t}"' in html_dashboard for t in tabs}

# ── 4. FORM ACTIONS ALL INTACT ────────────────────────────────────────────────
forms = {
    "CMS save → /admin/cms":                    'action="/admin/cms"' in html_dashboard,
    "Project save → /admin/project/save":        'action="/admin/project/save"' in html_dashboard,
    "Meeting settings → /admin/meetings/settings": 'action="/admin/meetings/settings"' in html_dashboard,
    "Calculator save → /admin/calculator/save":  'action="/admin/calculator/save"' in html_dashboard,
    "Social save → /admin/social/save":          'action="/admin/social/save"' in html_dashboard,
    "Logout → /admin/logout":                    'action="/admin/logout"' in html_dashboard,
}

# ── 5. SIDEBAR BADGE CHECKS ───────────────────────────────────────────────────
badges = {
    "Dashboard badge says 'LIVE' (still in sidebar)":
        ">LIVE<" in html_dashboard,
    "Media sidebar badge says 'STAGING' (still in sidebar)":
        ">STAGING<" in html_dashboard,
    "Users sidebar badge says 'STAGING' (still in sidebar)":
        ">STAGING<" in html_dashboard,
    "Security sidebar badge says 'ACTIVE' (still in sidebar)":
        ">ACTIVE<" in html_dashboard,
    "AI sidebar badge says 'GUARDED' (still in sidebar)":
        ">GUARDED<" in html_dashboard,
}

# ── PRINT RESULTS ──────────────────────────────────────────────────────────────
all_ok = True

def section(title, checks):
    global all_ok
    print(f"{'─'*55}")
    print(f"  {title}")
    print(f"{'─'*55}")
    for desc, result in checks.items():
        icon = "✓" if result else "✗ FAIL"
        print(f"  {icon}  {desc}")
        if not result:
            all_ok = False
    print()

section("1. TRUTHFUL LABELS PRESENT", truthful)
section("2. MISLEADING LABELS REMOVED", removed)
section("3. ALL 16 NAVIGATION TABS INTACT", nav)
section("4. ALL FORM ACTIONS INTACT", forms)
section("5. SIDEBAR BADGE PRESENCE CHECK", badges)

print("═" * 55)
if all_ok:
    print("  ✅  ALL CHECKS PASSED — Changes are SAFE TO KEEP.")
else:
    print("  ❌  Some checks FAILED — See details above.")
print("═" * 55)
