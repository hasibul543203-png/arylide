"""
Live end-to-end test: login then check the dashboard response.
Safe - read-only HTTP requests only.
"""
import urllib.request, urllib.parse, http.cookiejar, re, sys

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
opener.addheaders = [("User-Agent", "ArylideVerify/1.0")]

# 1. GET login page
resp = opener.open("http://127.0.0.1:4173/admin.html")
body = resp.read().decode("utf-8", errors="replace")
print(f"Login page status: {resp.status}  length: {len(body)}")

# Extract CSRF from hidden input
csrf_match = re.search(r'name=["\'](?:public_csrf|csrf)["\'] value=["\']([^"\']+)["\']', body)
if not csrf_match:
    csrf_match = re.search(r'value=["\']([A-Za-z0-9_-]{20,})["\'] name=["\'](?:public_csrf|csrf)["\']', body)
csrf = csrf_match.group(1) if csrf_match else ""
print(f"CSRF token found: {'YES (' + csrf[:10] + '...)' if csrf else 'NO'}")

# 2. POST login
login_data = urllib.parse.urlencode({
    "email": "admin@arylideholdings.com",
    "password": "Samir543203@",
    "csrf": csrf,
}).encode("utf-8")

req = urllib.request.Request(
    "http://127.0.0.1:4173/admin/login",
    data=login_data,
    headers={"Content-Type": "application/x-www-form-urlencoded",
             "Referer": "http://127.0.0.1:4173/admin.html"},
)
try:
    resp2 = opener.open(req)
    print(f"After login: {resp2.status}")
except urllib.error.HTTPError as e:
    loc = e.headers.get("Location", "")
    print(f"After login redirect: {e.code}  -> {loc}")

# 3. GET admin dashboard
resp3 = opener.open("http://127.0.0.1:4173/admin")
dash = resp3.read().decode("utf-8", errors="replace")
print(f"Dashboard status: {resp3.status}  length: {len(dash)}")
print()

# 4. Verify labels in live response
all_tabs = ["dashboard", "activity-logs", "cms", "projects", "media", "videos",
            "social", "meetings", "enquiries", "referrals", "appointments",
            "landowners", "calculator", "users", "security", "ai"]

checks = {
    "Sync pill says 'Local Application · SQLite'": "Local Application \u00b7 SQLite" in dash,
    "Prototype badge says 'Prototype · Not Yet Connected'": "Prototype \u00b7 Not Yet Connected" in dash,
    "Activity log says 'Demonstration Trail'": "Demonstration Trail" in dash,
    "'Live Synced' removed from live page": "Live Synced" not in dash,
    "'PROTOTYPE STAGING' removed from live page": "PROTOTYPE STAGING" not in dash,
    "All 16 navigation tabs present": all(f'data-tab="{t}"' in dash for t in all_tabs),
    "CMS form action intact": 'action="/admin/cms"' in dash,
    "Project save action intact": 'action="/admin/project/save"' in dash,
    "Logout action intact": 'action="/admin/logout"' in dash,
}

all_ok = True
for desc, result in checks.items():
    icon = "OK " if result else "FAIL"
    print(f"  [{icon}]  {desc}")
    if not result:
        all_ok = False

print()
if all_ok:
    print("LIVE TEST PASSED - All labels and navigation verified on running server.")
else:
    print("LIVE TEST HAS FAILURES - Check details above.")
