#!/usr/bin/env python3
"""Local ARYLIDE website + lead/referral CRM. Python standard library only."""
from __future__ import annotations

import argparse
import csv
import hashlib
import hmac
import html
import io
import json
import mimetypes
import os
import re
import secrets
import sqlite3
import sys
import threading
import time
from collections import defaultdict, deque
from datetime import date, datetime, timezone
from email import policy
from email.parser import BytesParser
from uuid import uuid4
from email.utils import formatdate
from admin_dashboard import admin_dashboard_html
from getpass import getpass
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlencode, urlsplit
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

_script_dir = Path(__file__).resolve().parent
if (_script_dir / "frontend").is_dir():
    ROOT = Path(os.environ.get("ARYLIDE_ROOT", _script_dir)).expanduser().resolve()
elif (_script_dir.parent / "frontend").is_dir():
    ROOT = Path(os.environ.get("ARYLIDE_ROOT", _script_dir.parent)).expanduser().resolve()
else:
    ROOT = Path(os.environ.get("ARYLIDE_ROOT", _script_dir)).expanduser().resolve()

FRONTEND_DIR = ROOT / "frontend" if (ROOT / "frontend").is_dir() else ROOT
BACKEND_DIR = ROOT / "backend" if (ROOT / "backend").is_dir() else ROOT
CONFIG_DIR = ROOT / "config" if (ROOT / "config").is_dir() else ROOT

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

_db_env = os.environ.get("ARYLIDE_DB_PATH")
if _db_env:
    DB_PATH = Path(_db_env).expanduser()
elif (BACKEND_DIR / "data" / "arylide.sqlite3").is_file():
    DB_PATH = BACKEND_DIR / "data" / "arylide.sqlite3"
else:
    DB_PATH = ROOT / "data" / "arylide.sqlite3"
DEFAULT_ADMIN_EMAIL = "admin@arylideholdings.com"
APK_FILENAME = "arylide-holdings-universal.apk"
WINDOWS_INSTALLER_FILENAME = "ARYLIDE-Setup.exe"
ALLOW_WEB_ADMIN_SETUP = os.environ.get("ARYLIDE_ALLOW_WEB_ADMIN_SETUP", "1") == "1"
EMBEDDED_SERVER = None
EMBEDDED_SERVER_LOCK = threading.Lock()
DEFAULT_STATS = {
    "projects": "3+",
    "completed": "3",
    "happy_clients": "30+",
    "years_trust": "2",
    "area_built": "51,000",
    "vision_sqft": "27,394,800",
}
DEFAULT_COMPANY = {
    "phone": "+880 1817 338 899",
    "email": "info@arylideholdings.com",
    "address": "Hashim Tower, Unit 7C · Gulshan, Dhaka 1208",
}
DEFAULT_PROJECTS = [
    {"id":"arylide-purbasha","name":"Arylide Purbasha","name_bn":"আরাইলাইড পূর্বাশা","location":"Green Model Town · Dhaka","location_bn":"গ্রিন মডেল টাউন · ঢাকা","sector":"","status":"completed","type":"residential","images":["/assets/purbasha-building.jpg","/assets/purbasha-campaign.jpg"],"description_en":"A completed project featured in ARYLIDE's published campaign.","description_bn":"ARYLIDE-এর প্রকাশিত ক্যাম্পেইনে দেখানো সম্পন্ন প্রজেক্ট।","amenities_en":"Contact us for verified details.","amenities_bn":"যাচাইকৃত তথ্য জানতে যোগাযোগ করুন।","price_per_sft":"","area_sft":"","featured":True,"position":1,"map_query":"Green Model Town Dhaka"},
    {"id":"sky-high-living","name":"Sky High Living","name_bn":"স্কাই হাই লিভিং","location":"ARYLIDE Residences","location_bn":"ARYLIDE Residences","sector":"","status":"details","type":"residential","images":["/assets/sky-high-tower.jpg","/assets/sky-high-living-campaign.jpg"],"description_en":"Residential project featured in the ‘Reach New Heights of Comfort’ campaign.","description_bn":"‘Reach New Heights of Comfort’ ক্যাম্পেইনে দেখানো আবাসিক প্রজেক্ট।","amenities_en":"Contact us for verified amenities.","amenities_bn":"যাচাইকৃত সুবিধার তথ্য জানতে যোগাযোগ করুন।","price_per_sft":"","area_sft":"","featured":True,"position":2,"map_query":"Dhaka Bangladesh"},
    {"id":"uttara-signature-address","name":"Uttara Signature Address","name_bn":"উত্তরা সিগনেচার অ্যাড্রেস","location":"Uttara · Dhaka","location_bn":"উত্তরা · ঢাকা","sector":"","status":"coming_soon","type":"residential","images":["/assets/uttara-coming-soon.jpg"],"description_en":"The supplied teaser says ‘Coming Soon.’","description_bn":"প্রদত্ত টিজারে ‘Coming Soon’ উল্লেখ আছে।","amenities_en":"Details will be published when available.","amenities_bn":"তথ্য প্রকাশিত হলে এখানে দেখানো হবে।","price_per_sft":"","area_sft":"","featured":False,"position":3,"map_query":"Uttara Dhaka"},
    {"id":"arylide-breezy","name":"Arylide Breezy","name_bn":"আরাইলাইড ব্রিজি","location":"Bashundhara R/A","location_bn":"বসুন্ধরা R/A","sector":"","status":"details","type":"residential","images":["/assets/green-walkway.jpg"],"description_en":"Listed as a featured project on ARYLIDE's website.","description_bn":"ARYLIDE-এর ওয়েবসাইটে ফিচার্ড প্রজেক্ট হিসেবে তালিকাভুক্ত।","amenities_en":"Contact us for verified details.","amenities_bn":"যাচাইকৃত তথ্য জানতে যোগাযোগ করুন।","price_per_sft":"","area_sft":"","featured":False,"position":4,"map_query":"Bashundhara R/A Dhaka"},
    {"id":"nisorgo","name":"Nisorgo","name_bn":"নিসর্গ","location":"Bashundhara R/A","location_bn":"বসুন্ধরা R/A","sector":"","status":"details","type":"residential","images":["/assets/jolshiri-hero.jpg"],"description_en":"Listed as a featured project on ARYLIDE's website.","description_bn":"ARYLIDE-এর ওয়েবসাইটে ফিচার্ড প্রজেক্ট হিসেবে তালিকাভুক্ত।","amenities_en":"Contact us for verified details.","amenities_bn":"যাচাইকৃত তথ্য জানতে যোগাযোগ করুন।","price_per_sft":"","area_sft":"","featured":False,"position":5,"map_query":"Bashundhara R/A Dhaka"},
    {"id":"jolshiri-land","name":"Jolshiri Abashon Land Partnership","name_bn":"জলশিরি আবাসন জমি অংশীদারত্ব","location":"Jolshiri Abashon","location_bn":"জলশিরি আবাসন","sector":"","status":"land","type":"opportunity","images":["/assets/jolshiri-land-wanted.jpg"],"description_en":"ARYLIDE campaign for landowner partnerships at Jolshiri Abashon.","description_bn":"জলশিরি আবাসনে জমির মালিকদের সঙ্গে অংশীদারত্বের জন্য ARYLIDE-এর ক্যাম্পেইন।","amenities_en":"Contact us to discuss a land opportunity.","amenities_bn":"জমির সুযোগ নিয়ে কথা বলতে যোগাযোগ করুন।","price_per_sft":"","area_sft":"","featured":False,"position":6,"map_query":"Jolshiri Abashon Bangladesh"},
    {"id":"ashiyana","name":"Ashiyana","name_bn":"আশিয়ানা","location":"Sector 14 · Jolshiri Abashon","location_bn":"সেক্টর ১৪ · জলশিরি আবাসন","sector":"14","status":"details","type":"residential","images":["/assets/jolshiri-hero.jpg","/assets/residence-interior.jpg"],"description_en":"Adjacent to the lake and bridge; corner plot, near a school and mosque.","description_bn":"লেকভিউ ও ব্রিজ সংলগ্ন, কর্নার প্লট, স্কুল ও মসজিদ সন্নিকটে।","amenities_en":"Nearby: lake, bridge, school and mosque.","amenities_bn":"নিকটবর্তী: লেক, ব্রিজ, স্কুল ও মসজিদ।","price_per_sft":"8500","area_sft":"2850","featured":True,"position":7,"map_query":"23.81119,90.50089"},
    {"id":"bashundhara-tower","name":"Bashundhara Tower","name_bn":"বসুন্ধরা টাওয়ার","location":"Bashundhara R/A · Dhaka","location_bn":"বসুন্ধরা R/A · ঢাকা","sector":"","status":"details","type":"commercial","images":["/assets/sky-high-tower.jpg"],"description_en":"Listed as a commercial project in the client-provided brief.","description_bn":"ক্লায়েন্ট-প্রদত্ত ব্রিফে বাণিজ্যিক প্রজেক্ট হিসেবে তালিকাভুক্ত।","amenities_en":"Contact us for verified details.","amenities_bn":"যাচাইকৃত তথ্য জানতে যোগাযোগ করুন।","price_per_sft":"","area_sft":"","featured":False,"position":8,"map_query":"Bashundhara R/A Dhaka"},
    {"id":"uttara-heights","name":"Uttara Heights","name_bn":"উত্তরা হাইটস","location":"Uttara · Dhaka","location_bn":"উত্তরা · ঢাকা","sector":"","status":"details","type":"residential commercial","images":["/assets/green-walkway.jpg"],"description_en":"Listed as a mixed-use project in the client-provided brief.","description_bn":"ক্লায়েন্ট-প্রদত্ত ব্রিফে মিশ্র-ব্যবহার প্রজেক্ট হিসেবে তালিকাভুক্ত।","amenities_en":"Contact us for verified details.","amenities_bn":"যাচাইকৃত তথ্য জানতে যোগাযোগ করুন।","price_per_sft":"","area_sft":"","featured":False,"position":9,"map_query":"Uttara Dhaka"},
]
DEFAULT_MEETING_SETTINGS = {
    "working_start":"10:00", "working_end":"18:00", "slot_duration":60,
    "off_days":[5], "slot_times":["10:00","11:00","12:00","14:00","15:00","16:00","17:00"],
    "location_bn":"আমাদের গুলশান অফিস / অনলাইন Zoom", "location_en":"Our Gulshan office / online Zoom"
}
DEFAULT_MEETING_CONFIRMATION = {
    "en": "Thank you for booking a meeting with ARYLIDE Holdings. Our team will review your request and contact you shortly.",
    "bn": "ARYLIDE Holdings-এর সাথে মিটিং বুক করার জন্য ধন্যবাদ। আমাদের টিম আপনার অনুরোধটি পর্যালোচনা করে দ্রুত আপনার সাথে যোগাযোগ করবে।",
}
DEFAULT_CALCULATOR = {"area_sft":2850,"price_per_sft":8500,"down_percent":50,"months":36,"annual_growth_percent":14,"growth_years":3}
DEFAULT_SOCIAL = {"facebook":"","linkedin":"","x":"","youtube":"","post_embed_link":""}
DEFAULT_SETTINGS = {
    "referral_reward_bdt": "200000",
    "stats_json": json.dumps(DEFAULT_STATS, ensure_ascii=False, separators=(",", ":")),
    "projects_json": "[]",
    "company_info_json": json.dumps(DEFAULT_COMPANY, ensure_ascii=False, separators=(",", ":")),
    "meeting_settings_json": json.dumps(DEFAULT_MEETING_SETTINGS, ensure_ascii=False, separators=(",", ":")),
    "meeting_message_en": DEFAULT_MEETING_CONFIRMATION["en"],
    "meeting_message_bn": DEFAULT_MEETING_CONFIRMATION["bn"],
    "meeting_attachments_json": "[]",
    "calculator_json": json.dumps(DEFAULT_CALCULATOR, ensure_ascii=False, separators=(",", ":")),
    "social_links_json": json.dumps(DEFAULT_SOCIAL, ensure_ascii=False, separators=(",", ":")),
    "videos_json": "[]",
}
VALID_INTERESTS = {
    "Residential Development",
    "Commercial Projects",
    "Landowner Partnership",
    "Project / Site Visit",
    "Referral Programme",
    "Other",
}
VALID_STATUSES = {"pending", "contacted", "converted", "closed"}
REFERRAL_STATUSES = {"pending", "contacted", "sold"}
PASSWORD_ITERATIONS = 310_000
SESSION_SECONDS = 12 * 60 * 60
MAX_BODY_BYTES = 42 * 1024 * 1024
RATE_LOCK = threading.Lock()
RATE_BUCKETS: dict[tuple[str, str], deque[float]] = defaultdict(deque)


def configure_paths(root: str, db_path: str, allow_web_admin_setup: bool = False) -> None:
    """Point the server at writable app-private files (used by the Android wrapper)."""
    global ROOT, DB_PATH, ALLOW_WEB_ADMIN_SETUP
    ROOT = Path(root).expanduser().resolve()
    DB_PATH = Path(db_path).expanduser().resolve()
    ALLOW_WEB_ADMIN_SETUP = bool(allow_web_admin_setup)


def start_embedded_server(host: str = "127.0.0.1", port: int = 4173) -> bool:
    """Start the local HTTP server in a daemon thread for a native mobile shell."""
    global EMBEDDED_SERVER
    with EMBEDDED_SERVER_LOCK:
        if EMBEDDED_SERVER is not None:
            return True
        init_db()
        server = ThreadingHTTPServer((host, int(port)), AppHandler)
        server.daemon_threads = True
        thread = threading.Thread(target=server.serve_forever, daemon=True, name="arylide-local-http")
        thread.start()
        EMBEDDED_SERVER = server
    return True


def connect_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH), timeout=20)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("PRAGMA busy_timeout = 20000")
    return db


def init_db() -> None:
    with connect_db() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referral_code TEXT NOT NULL UNIQUE,
                referral_code_used TEXT NOT NULL DEFAULT '',
                referred_by_id INTEGER REFERENCES leads(id) ON DELETE SET NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                interest TEXT NOT NULL,
                message TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'pending',
                reward_amount_bdt INTEGER NOT NULL DEFAULT 0,
                reward_paid INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_leads_referrer ON leads(referred_by_id);
            CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                admin_id INTEGER NOT NULL REFERENCES admins(id) ON DELETE CASCADE,
                csrf_token TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                created_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS referral_leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT NOT NULL UNIQUE,
                your_name TEXT NOT NULL,
                your_mobile TEXT NOT NULL,
                buyer_name TEXT NOT NULL,
                buyer_mobile TEXT NOT NULL,
                project TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_referral_leads_created ON referral_leads(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_referral_leads_status ON referral_leads(status);
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                service TEXT NOT NULL,
                message TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_appointments_created ON appointments(created_at DESC);
            CREATE TABLE IF NOT EXISTS meetings (
                id TEXT PRIMARY KEY,
                serial_number TEXT NOT NULL UNIQUE,
                confirmation_message_en TEXT NOT NULL DEFAULT '',
                confirmation_message_bn TEXT NOT NULL DEFAULT '',
                confirmation_attachments_json TEXT NOT NULL DEFAULT '[]',
                name TEXT NOT NULL,
                mobile TEXT NOT NULL,
                email TEXT NOT NULL DEFAULT '',
                project TEXT NOT NULL,
                meeting_date TEXT NOT NULL,
                meeting_time TEXT NOT NULL,
                message TEXT NOT NULL DEFAULT '',
                user_id TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Pending',
                manage_token_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings(meeting_date, meeting_time);
            CREATE INDEX IF NOT EXISTS idx_meetings_status ON meetings(status);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_meetings_active_slot ON meetings(meeting_date, meeting_time) WHERE status IN ('Pending','Confirmed','Rescheduled');
            """
        )
        meeting_columns = {row["name"] for row in db.execute("PRAGMA table_info(meetings)").fetchall()}
        if "serial_number" not in meeting_columns:
            db.execute("ALTER TABLE meetings ADD COLUMN serial_number TEXT NOT NULL DEFAULT ''")
        if "confirmation_message_en" not in meeting_columns:
            db.execute("ALTER TABLE meetings ADD COLUMN confirmation_message_en TEXT NOT NULL DEFAULT ''")
        if "confirmation_message_bn" not in meeting_columns:
            db.execute("ALTER TABLE meetings ADD COLUMN confirmation_message_bn TEXT NOT NULL DEFAULT ''")
        if "confirmation_attachments_json" not in meeting_columns:
            db.execute("ALTER TABLE meetings ADD COLUMN confirmation_attachments_json TEXT NOT NULL DEFAULT '[]'")
        existing_meetings = db.execute(
            "SELECT id,created_at,serial_number FROM meetings ORDER BY created_at,id"
        ).fetchall()
        counters: dict[str, int] = {}
        for row in existing_meetings:
            serial = str(row["serial_number"] or "")
            if re.fullmatch(r"ARY-\d{4}-\d{6}", serial):
                year = serial[4:8]
                counters[year] = max(counters.get(year, 0), int(serial[9:]))
        for row in existing_meetings:
            if row["serial_number"]:
                continue
            year_match = re.match(r"(\d{4})", str(row["created_at"] or ""))
            year = year_match.group(1) if year_match else str(datetime.now(timezone.utc).year)
            counters[year] = counters.get(year, 0) + 1
            serial = f"ARY-{year}-{counters[year]:06d}"
            db.execute("UPDATE meetings SET serial_number=? WHERE id=?", (serial, row["id"]))
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_meetings_serial ON meetings(serial_number)")
        db.execute("DROP INDEX IF EXISTS idx_meetings_active_slot")
        db.execute("CREATE UNIQUE INDEX idx_meetings_active_slot ON meetings(meeting_date,meeting_time) WHERE status IN ('Pending','Confirmed','Rescheduled')")
        for key, value in DEFAULT_SETTINGS.items():
            db.execute("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)", (key, value))
        seeded = db.execute("SELECT value FROM settings WHERE key='project_catalog_seeded'").fetchone()
        if not seeded:
            current_projects = db.execute("SELECT value FROM settings WHERE key='projects_json'").fetchone()
            if not current_projects or current_projects["value"] in {"", "[]"}:
                db.execute("UPDATE settings SET value=? WHERE key='projects_json'", (json.dumps(DEFAULT_PROJECTS, ensure_ascii=False, separators=(",", ":")),))
            db.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('project_catalog_seeded','1')")
        # Remove the old, incorrect profile figures from existing local databases.
        db.execute("DELETE FROM settings WHERE key IN ('project_count','experience_years')")
        db.execute("DELETE FROM sessions WHERE expires_at < ?", (int(time.time()),))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_settings() -> dict[str, str]:
    with connect_db() as db:
        rows = db.execute("SELECT key,value FROM settings").fetchall()
    values = dict(DEFAULT_SETTINGS)
    values.update({row["key"]: row["value"] for row in rows})
    return values


def set_setting(key: str, value: str) -> None:
    with connect_db() as db:
        db.execute(
            "INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )


def firebase_client_config() -> dict[str, str]:
    """Read only the public Firebase identifiers from the shared config.js file."""
    keys = ("FIREBASE_API_KEY", "FIREBASE_AUTH_DOMAIN", "FIREBASE_PROJECT_ID", "FIREBASE_APP_ID")
    cfg_file = CONFIG_DIR / "config.js" if (CONFIG_DIR / "config.js").is_file() else (FRONTEND_DIR / "config.js" if (FRONTEND_DIR / "config.js").is_file() else ROOT / "config.js")
    try:
        source = cfg_file.read_text(encoding="utf-8")
    except OSError:
        source = ""
    values: dict[str, str] = {}
    for key in keys:
        match = re.search(r"\b" + re.escape(key) + r"\s*:\s*['\"]([^'\"]*)['\"]", source)
        values[key] = match.group(1).strip() if match else ""
    return values


def firebase_auth_configured() -> bool:
    config = firebase_client_config()
    return all(config.get(key) for key in ("FIREBASE_API_KEY", "FIREBASE_AUTH_DOMAIN", "FIREBASE_PROJECT_ID", "FIREBASE_APP_ID"))


def verify_firebase_id_token(id_token: str) -> dict[str, str] | None:
    """Verify a Firebase ID token through Identity Toolkit over HTTPS.

    The Firebase web API key is public configuration, not a private credential. The
    remote lookup validates token signature, expiry, project and disabled-account state.
    """
    config = firebase_client_config()
    api_key = config.get("FIREBASE_API_KEY", "")
    if not api_key or not id_token or len(id_token) > 8192:
        return None
    url = "https://identitytoolkit.googleapis.com/v1/accounts:lookup?" + urlencode({"key": api_key})
    body = json.dumps({"idToken": id_token}).encode("utf-8")
    request = Request(url, data=body, headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=7) as response:
            payload = json.loads(response.read(256 * 1024).decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    users = payload.get("users", []) if isinstance(payload, dict) else []
    if not isinstance(users, list) or not users or not isinstance(users[0], dict):
        return None
    user = users[0]
    uid = str(user.get("localId", "")).strip()
    if not uid or len(uid) > 128 or user.get("disabled") is True:
        return None
    return {"uid": uid, "email": str(user.get("email", "")).strip().lower(), "phone": str(user.get("phoneNumber", "")).strip()}


def get_cms_data() -> dict[str, object]:
    settings = get_settings()
    try:
        stats = json.loads(settings.get("stats_json", "{}"))
        if not isinstance(stats, dict):
            stats = {}
    except (json.JSONDecodeError, TypeError):
        stats = {}
    stats = {**DEFAULT_STATS, **{key: str(stats.get(key, DEFAULT_STATS[key])) for key in DEFAULT_STATS}}
    try:
        projects = json.loads(settings.get("projects_json", "[]"))
        if not isinstance(projects, list):
            projects = []
    except (json.JSONDecodeError, TypeError):
        projects = []
    projects = [item for item in projects if isinstance(item, dict)][:200]
    try:
        company = json.loads(settings.get("company_info_json", "{}"))
        if not isinstance(company, dict):
            company = {}
    except (json.JSONDecodeError, TypeError):
        company = {}
    company = {**DEFAULT_COMPANY, **{key: str(company.get(key, DEFAULT_COMPANY[key])) for key in DEFAULT_COMPANY}}
    def parse_setting(key: str, fallback: object, expected: type) -> object:
        try:
            value = json.loads(settings.get(key, ""))
            return value if isinstance(value, expected) else fallback
        except (json.JSONDecodeError, TypeError):
            return fallback
    meeting = parse_setting("meeting_settings_json", DEFAULT_MEETING_SETTINGS, dict)
    meeting = {**DEFAULT_MEETING_SETTINGS, **meeting}
    meeting_message_en = str(settings.get("meeting_message_en", DEFAULT_MEETING_CONFIRMATION["en"])).strip() or DEFAULT_MEETING_CONFIRMATION["en"]
    meeting_message_bn = str(settings.get("meeting_message_bn", DEFAULT_MEETING_CONFIRMATION["bn"])).strip() or DEFAULT_MEETING_CONFIRMATION["bn"]
    meeting_attachments = parse_setting("meeting_attachments_json", [], list)
    if not isinstance(meeting_attachments, list):
        meeting_attachments = []
    meeting_attachments = [item for item in meeting_attachments if isinstance(item, dict)][:50]
    videos = parse_setting("videos_json", [], list)
    videos = [item for item in videos if isinstance(item, dict)][:200]
    social = parse_setting("social_links_json", DEFAULT_SOCIAL, dict)
    social = {**DEFAULT_SOCIAL, **{key: str(social.get(key, "")) for key in DEFAULT_SOCIAL}}
    calculator = parse_setting("calculator_json", DEFAULT_CALCULATOR, dict)
    calculator = {**DEFAULT_CALCULATOR, **calculator}
    return {"stats": stats, "projects": projects, "company": company, "meeting_settings": meeting, "meeting_message_en": meeting_message_en, "meeting_message_bn": meeting_message_bn, "meeting_attachments": meeting_attachments, "videos": videos, "social": social, "calculator": calculator}


def get_public_cms_data() -> dict[str, object]:
    data = get_cms_data()
    data.pop("meeting_attachments", None)
    return data


def safe_json_for_script(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")


def valid_phone(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9+() .-]{8,24}", value or ""))


ALLOWED_MEETING_ATTACHMENT_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov", ".webm", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt"}


def generate_meeting_serial(db: sqlite3.Connection, year: int | None = None) -> str:
    serial_year = year or datetime.now(timezone.utc).year
    row = db.execute(
        "SELECT MAX(CAST(substr(serial_number,10) AS INTEGER)) "
        "FROM meetings WHERE serial_number LIKE ?",
        (f"ARY-{serial_year}-%",),
    ).fetchone()
    sequence = int(row[0] or 0) + 1
    return f"ARY-{serial_year}-{sequence:06d}"


def sanitize_attachment_filename(filename: str) -> str:
    safe = Path(filename or "attachment").name
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", safe).strip(".-") or "attachment"
    suffix = Path(safe).suffix.lower()
    if suffix not in ALLOWED_MEETING_ATTACHMENT_EXTENSIONS:
        suffix = ".bin"
    return f"{uuid4().hex}{suffix}"


def validate_meeting_attachment(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_MEETING_ATTACHMENT_EXTENSIONS:
        raise ValueError("File type not supported.")
    signatures = {
        ".pdf": content.startswith(b"%PDF-"),
        ".jpg": content.startswith(b"\xff\xd8\xff"),
        ".jpeg": content.startswith(b"\xff\xd8\xff"),
        ".png": content.startswith(b"\x89PNG\r\n\x1a\n"),
        ".webp": len(content) >= 12 and content.startswith(b"RIFF") and content[8:12] == b"WEBP",
        ".mp4": len(content) >= 12 and content[4:8] == b"ftyp",
        ".mov": len(content) >= 12 and content[4:8] == b"ftyp",
        ".webm": content.startswith(b"\x1a\x45\xdf\xa3"),
        ".doc": content.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"),
        ".xls": content.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"),
        ".ppt": content.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"),
        ".docx": content.startswith(b"PK\x03\x04"),
        ".xlsx": content.startswith(b"PK\x03\x04"),
        ".pptx": content.startswith(b"PK\x03\x04"),
        ".txt": b"\x00" not in content,
    }
    if not signatures.get(suffix, False):
        raise ValueError(f"The file content does not match its {suffix or 'unknown'} extension.")
    mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    return mime_type


def persist_uploaded_attachments(payload: object) -> list[dict[str, object]]:
    if not isinstance(payload, (list, tuple)):
        payload = [payload]
    uploads = [item for item in payload if isinstance(item, dict) and item.get("filename")]
    if len(uploads) > 10:
        raise ValueError("Upload no more than 10 files at a time.")
    total_size = 0
    validated: list[tuple[str, bytes, str]] = []
    for item in uploads:
        filename = Path(str(item.get("filename") or "")).name
        content = item.get("content")
        if not filename or not isinstance(content, (bytes, bytearray)):
            raise ValueError("Could not read one of the selected files.")
        data = bytes(content)
        if not data or len(data) > 12 * 1024 * 1024:
            raise ValueError(f"{filename} is empty or exceeds the 12 MB per-file limit.")
        total_size += len(data)
        if total_size > 40 * 1024 * 1024:
            raise ValueError("The combined upload must not exceed 40 MB.")
        validated.append((filename, data, validate_meeting_attachment(filename, data)))
    attachments: list[dict[str, object]] = []
    root = (BACKEND_DIR / "data" / "meeting_attachments").resolve() if (BACKEND_DIR / "data").is_dir() else (ROOT / "data" / "meeting_attachments").resolve()
    root.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    try:
        for filename, data, mime_type in validated:
            safe_name = sanitize_attachment_filename(filename)
            file_path = root / safe_name
            file_path.write_bytes(data)
            written.append(file_path)
            attachments.append({
                "id": uuid4().hex,
                "name": filename,
                "type": mime_type,
                "size": len(data),
                "path": safe_name,
            })
    except OSError as error:
        for file_path in written:
            file_path.unlink(missing_ok=True)
        raise ValueError("An attachment could not be saved. No attachments were added.") from error
    return attachments


def send_outgoing_notifications(kind: str, data: dict[str, object]) -> None:
    """Optional server-side notifications; credentials are never shipped to browser code."""
    token = os.environ.get("ARYLIDE_TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("ARYLIDE_TELEGRAM_CHAT_ID", "").strip()
    webhook = os.environ.get("ARYLIDE_N8N_WEBHOOK_URL", "").strip()
    buyer_name = str(data.get("buyer_name") or data.get("name") or data.get("your_name") or "New enquiry")
    buyer_mobile = str(data.get("buyer_mobile") or data.get("mobile") or data.get("phone") or data.get("your_mobile") or "")
    if kind == "meeting":
        telegram_text = f"📅 NEW MEETING BOOKED: {buyer_name} - {buyer_mobile} Date: {data.get('meeting_date', '')} Time: {data.get('meeting_time', '')} Project: {data.get('project', '')}"
    else:
        telegram_text = f"🔥 New Lead: {buyer_name} - {buyer_mobile}"
    payload = {"event": kind, "message": telegram_text, **data}

    if token and chat_id:
        try:
            telegram_url = f"https://api.telegram.org/bot{token}/sendMessage"
            encoded = urlencode({"chat_id": chat_id, "text": telegram_text}).encode("utf-8")
            request = Request(telegram_url, data=encoded, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
            with urlopen(request, timeout=5) as response:
                response.read(1024)
        except Exception as error:
            print(f"Telegram notification failed ({type(error).__name__}); local submission was saved.")

    if webhook:
        parts = urlsplit(webhook)
        if parts.scheme == "https" and parts.netloc:
            try:
                body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                request = Request(webhook, data=body, headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
                with urlopen(request, timeout=5) as response:
                    response.read(1024)
            except Exception as error:
                print(f"N8N webhook notification failed ({type(error).__name__}); local submission was saved.")


def queue_notifications(kind: str, data: dict[str, object]) -> None:
    if not (os.environ.get("ARYLIDE_TELEGRAM_BOT_TOKEN") and os.environ.get("ARYLIDE_TELEGRAM_CHAT_ID") or os.environ.get("ARYLIDE_N8N_WEBHOOK_URL")):
        return
    safe_data = {key: str(value)[:2000] for key, value in data.items() if key in {
        "your_name", "your_mobile", "buyer_name", "buyer_mobile", "project", "name", "mobile", "phone", "email", "service", "appointment_date", "meeting_date", "meeting_time", "message", "interest", "referral_code"
    }}
    threading.Thread(target=send_outgoing_notifications, args=(kind, safe_data), daemon=True, name="arylide-notifications").start()


def format_bdt(amount: int | str) -> str:
    number = max(0, int(amount))
    digits = str(number)
    if len(digits) <= 3:
        return digits
    last_three = digits[-3:]
    leading = digits[:-3]
    groups = []
    while leading:
        groups.insert(0, leading[-2:])
        leading = leading[:-2]
    return ",".join(groups + [last_three])


def escape(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def make_password_hash(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds, salt_hex, digest_hex = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(rounds))
        if hmac.compare_digest(digest.hex(), digest_hex):
            return True
        if password.strip() != password:
            stripped = hashlib.pbkdf2_hmac("sha256", password.strip().encode("utf-8"), bytes.fromhex(salt_hex), int(rounds))
            if hmac.compare_digest(stripped.hex(), digest_hex):
                return True
        return False
    except (ValueError, TypeError):
        return False


def create_or_reset_admin(email: str, reset: bool = False) -> None:
    init_db()
    email = email.strip().lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise SystemExit("Please enter a valid admin email address.")
    with connect_db() as db:
        row = db.execute("SELECT id FROM admins WHERE email=?", (email,)).fetchone()
        count = db.execute("SELECT COUNT(*) AS n FROM admins").fetchone()["n"]
    if row and not reset:
        raise SystemExit("That admin already exists. Use --reset-admin to change its password.")
    if not row and reset:
        raise SystemExit("No admin with that email exists; use --create-admin first.")
    if count and not row and not reset:
        raise SystemExit("An admin already exists. Use --reset-admin --email <address> to reset it.")

    password = getpass("Choose a new admin password (12+ characters): ")
    confirmation = getpass("Confirm password: ")
    if len(password) < 12:
        raise SystemExit("Password must be at least 12 characters.")
    if password != confirmation:
        raise SystemExit("The passwords did not match.")
    if password.lower() in {"password123456", "changeme123456"}:
        raise SystemExit("Choose a private password; do not use a common demo credential.")
    digest = make_password_hash(password)
    with connect_db() as db:
        if row:
            db.execute("UPDATE admins SET password_hash=? WHERE email=?", (digest, email))
            db.execute("DELETE FROM sessions WHERE admin_id=(SELECT id FROM admins WHERE email=?)", (email,))
            message = f"Admin password reset for {email}."
        else:
            db.execute("INSERT INTO admins(email,password_hash,created_at) VALUES(?,?,?)", (email, digest, utc_now()))
            message = f"Admin account created for {email}."
    print(message)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def valid_token(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_-]{30,100}", value or ""))


def allow_rate(bucket: str, identity: str, limit: int, seconds: int) -> bool:
    now = time.time()
    key = (bucket, identity)
    with RATE_LOCK:
        events = RATE_BUCKETS[key]
        while events and events[0] < now - seconds:
            events.popleft()
        if len(events) >= limit:
            return False
        events.append(now)
        return True


def generate_referral_code(db: sqlite3.Connection) -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    for _ in range(100):
        code = "ARY-" + "".join(secrets.choice(alphabet) for _ in range(8))
        if not db.execute("SELECT 1 FROM leads WHERE referral_code=?", (code,)).fetchone():
            return code
    raise RuntimeError("Unable to allocate a unique referral code")


ADMIN_STYLE = r"""
:root{--bg:#0c1513;--panel:#13241e;--panel2:#192e25;--gold:#d8bd68;--mint:#bfd0a9;--text:#eef1e8;--muted:#a0ada3;--line:rgba(255,255,255,.12);--red:#f3a3a0;--green:#a9d8ad}
*{box-sizing:border-box}body{margin:0;background:linear-gradient(140deg,#0a100e,#102019 55%,#17261e);color:var(--text);font:14px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}a{color:var(--mint);text-decoration:none}a:hover{color:#fff}button,input,select{font:inherit}button{cursor:pointer}.shell{width:min(1200px,calc(100% - 32px));margin:0 auto}.bar{position:sticky;top:0;z-index:3;border-bottom:1px solid var(--line);background:rgba(10,18,15,.94);backdrop-filter:blur(16px)}.barin{display:flex;align-items:center;justify-content:space-between;gap:18px;min-height:66px}.brand{color:var(--gold);font-weight:850;letter-spacing:.1em;font-size:14px}.barlinks{display:flex;align-items:center;gap:12px}.barlinks form{margin:0}.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:10px 14px;border:1px solid var(--line);border-radius:5px;color:var(--text);background:rgba(255,255,255,.04);font-weight:700;font-size:12px}.btn:hover{border-color:var(--gold);color:#fff}.btn.gold{color:#10130e;background:var(--gold);border-color:var(--gold)}.btn.danger{color:#ffc7c2}.wrap{padding:25px 0 46px}.welcome{display:flex;justify-content:space-between;gap:20px;align-items:end;margin:10px 0 20px}.kicker{color:var(--gold);font-size:10px;letter-spacing:.18em;text-transform:uppercase;font-weight:800}.welcome h1{margin:6px 0 0;font-family:Georgia,serif;font-weight:500;font-size:clamp(30px,5vw,47px);line-height:1.08}.welcome p{margin:8px 0 0;color:var(--muted);font-size:12px}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:21px 0}.metric{min-height:110px;padding:17px;border:1px solid var(--line);border-radius:8px;background:linear-gradient(145deg,rgba(255,255,255,.055),rgba(255,255,255,.015))}.metric span{display:block;color:var(--muted);font-size:9px;letter-spacing:.12em;text-transform:uppercase;font-weight:800}.metric strong{display:block;margin-top:10px;color:var(--gold);font-size:clamp(24px,3vw,34px);font-weight:700;letter-spacing:-.05em}.metric small{display:block;margin-top:4px;color:var(--muted);font-size:9px}.panel{margin-top:14px;padding:18px;border:1px solid var(--line);border-radius:8px;background:rgba(18,35,28,.88)}.panel h2{margin:0 0 12px;font-family:Georgia,serif;font-size:23px;font-weight:500}.toolbar{display:flex;flex-wrap:wrap;align-items:end;gap:9px;margin:12px 0 15px}.field{display:flex;flex-direction:column;gap:5px;min-width:150px}.field label{color:var(--muted);font-size:9px;font-weight:750;text-transform:uppercase;letter-spacing:.09em}.field input,.field select{min-height:38px;padding:8px 10px;border:1px solid var(--line);border-radius:4px;color:var(--text);background:#0d1914}.field select option{color:#101814;background:#fff}.tablewrap{overflow:auto;border:1px solid var(--line);border-radius:6px}.table{width:100%;min-width:1040px;border-collapse:collapse;font-size:11px}.table th,.table td{padding:11px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}.table th{color:var(--gold);font-size:8px;letter-spacing:.1em;text-transform:uppercase;background:rgba(255,255,255,.035)}.table tr:last-child td{border-bottom:0}.table td small{display:block;margin-top:4px;color:var(--muted);font-size:9px}.table .muted{color:var(--muted)}.rowform{display:flex;align-items:center;gap:6px;margin:0}.rowform select{min-height:33px;max-width:116px;padding:6px;border:1px solid var(--line);border-radius:4px;color:var(--text);background:#0d1914;font-size:10px}.rowform input[type=checkbox]{accent-color:#d8bd68}.rowform button{padding:7px 9px;border:1px solid var(--line);border-radius:4px;color:#fff;background:rgba(255,255,255,.06);font-size:9px}.tag{display:inline-block;padding:4px 7px;border-radius:20px;background:rgba(215,227,107,.09);color:var(--mint);font-size:8px;font-weight:800;text-transform:uppercase;letter-spacing:.06em}.tag.pending{color:#f2d995}.tag.contacted{color:#a8d1e6}.tag.converted{color:var(--green)}.tag.closed{color:#d8a6a4}.empty{padding:26px!important;text-align:center!important;color:var(--muted)}.settings{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;align-items:end}.notice{margin:11px 0 0;color:var(--muted);font-size:10px;line-height:1.7}.login{width:min(430px,calc(100% - 28px));margin:10vh auto;padding:25px;border:1px solid var(--line);border-radius:9px;background:rgba(17,34,27,.94);box-shadow:0 25px 70px rgba(0,0,0,.3)}.login h1{margin:8px 0 8px;font-family:Georgia,serif;font-size:31px;font-weight:500}.login p{color:var(--muted);font-size:11px;line-height:1.7}.login .field{margin:14px 0}.login input{width:100%}.msg{padding:10px 12px;border:1px solid rgba(243,163,160,.3);border-radius:5px;color:#ffd4d1;background:rgba(140,30,25,.13);font-size:11px}.msg.ok{color:var(--green);border-color:rgba(169,216,173,.25);background:rgba(40,120,55,.1)}.setup{padding:12px;border:1px solid rgba(216,189,104,.28);border-radius:5px;color:#e6dcbd;background:rgba(216,189,104,.06);font-size:11px;line-height:1.7}.setup code{color:#fff;font-family:ui-monospace,monospace}.foot{margin:18px 0;color:var(--muted);font-size:9px;line-height:1.6}
@media(max-width:860px){.metrics{grid-template-columns:repeat(2,1fr)}.settings{grid-template-columns:1fr 1fr}.welcome{align-items:flex-start;flex-direction:column}.table{min-width:970px}}
@media(max-width:560px){.shell{width:calc(100% - 22px)}.barin{min-height:58px}.barlinks{gap:6px}.barlinks .btn{padding:8px 9px;font-size:10px}.metrics{gap:7px}.metric{min-height:96px;padding:13px}.metric strong{font-size:25px}.panel{padding:12px}.settings{grid-template-columns:1fr}.welcome h1{font-size:34px}.login{margin:6vh auto;padding:20px}}
"""


def admin_page_start(title: str, description: str = "") -> str:
    return f"""<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><meta name=\"theme-color\" content=\"#0c1513\"><title>{escape(title)} · ARYLIDE Admin</title><style>{ADMIN_STYLE}</style></head><body>{description}"""


def admin_login_html(csrf: str, message: str = "", setup_required: bool = False) -> str:
    msg = f'<div class="msg">{escape(message)}</div>' if message else ""
    if setup_required:
        form = (
            '<div class="setup"><strong>Admin setup is required.</strong><br>'
            'In Termux or a terminal, stop the app and run:<br>'
            '<code>python run.py --create-admin</code><br>'
            'Choose a private password of at least 12 characters, then start the app again.'
            '</div>'
        )
    else:
        form = f"""<form method=\"post\" action=\"/admin/login\">
          <input type=\"hidden\" name=\"csrf\" value=\"{escape(csrf)}\">
          <div class=\"field\"><label for=\"email\">Admin email</label><input id=\"email\" name=\"email\" type=\"email\" required autocomplete=\"username\" value=\"{DEFAULT_ADMIN_EMAIL}\"></div>
          <div class=\"field\"><label for=\"password\">Password</label><input id=\"password\" name=\"password\" type=\"password\" required autocomplete=\"current-password\"></div>
          <button class=\"btn gold\" type=\"submit\" style=\"width:100%;margin-top:6px\">Sign in to Admin</button>
        </form>"""
    return admin_page_start("Admin sign in") + f"""
      <main class=\"login\"><div class=\"brand\">ARYLIDE HOLDINGS LIMITED</div><div class=\"kicker\" style=\"margin-top:17px\">SECURE LOCAL CRM</div>
      <h1>Admin sign in</h1><p>Manage enquiries, referral codes, conversion status and the reward settings for this app’s local database.</p>{msg}{form}
      <p class=\"foot\">For security, the shared demo password from the brief is not built into this app. Use a unique admin password. Local data is stored in <code>data/arylide.sqlite3</code>.</p>
      <a href=\"/\">← Back to ARYLIDE</a></main></body></html>"""


def admin_setup_html(csrf: str, message: str = "") -> str:
    msg = f'<div class="msg">{escape(message)}</div>' if message else ""
    body = f"""<main class=\"login\"><div class=\"brand\">ARYLIDE HOLDINGS LIMITED</div><div class=\"kicker\" style=\"margin-top:17px\">FIRST-RUN ADMIN SETUP</div>
      <h1>Create your admin</h1><p>This creates the only administrator for this device. Choose a private password of at least 12 characters; only a salted password hash is stored.</p>{msg}
      <form method=\"post\" action=\"/admin/setup\"><input type=\"hidden\" name=\"csrf\" value=\"{escape(csrf)}\">
      <div class=\"field\"><label for=\"setupEmail\">Admin email</label><input id=\"setupEmail\" name=\"email\" type=\"email\" required maxlength=\"180\" autocomplete=\"email\" value=\"{DEFAULT_ADMIN_EMAIL}\"></div>
      <div class=\"field\"><label for=\"setupPassword\">New password · 12 characters minimum</label><input id=\"setupPassword\" name=\"password\" type=\"password\" minlength=\"12\" maxlength=\"200\" required autocomplete=\"new-password\"></div>
      <div class=\"field\"><label for=\"setupConfirm\">Confirm password</label><input id=\"setupConfirm\" name=\"confirmation\" type=\"password\" minlength=\"12\" maxlength=\"200\" required autocomplete=\"new-password\"></div>
      <button class=\"btn gold\" type=\"submit\" style=\"width:100%;margin-top:6px\">Create admin account</button></form>
      <p class=\"foot\">Admin setup is available only until the first admin is created. Keep your phone private and never share your admin password.</p><a href=\"/\">← Back to ARYLIDE</a></main>"""
    return admin_page_start("Admin setup") + body + "</body></html>"


class AppHandler(BaseHTTPRequestHandler):
    server_version = "ARYLIDE-Local-App/1.0"
    sys_version = ""

    def log_message(self, fmt: str, *args: object) -> None:
        # Strip query parameters so dashboard search terms and personal values never reach logs.
        safe_args = list(args)
        if safe_args and isinstance(safe_args[0], str):
            parts = safe_args[0].split()
            if len(parts) >= 2 and parts[0] in {"GET", "POST", "HEAD"}:
                safe_args[0] = f"{parts[0]} {urlsplit(parts[1]).path} {parts[2] if len(parts) > 2 else ''}".strip()
        super().log_message(fmt, *safe_args)

    def add_security_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header("Content-Security-Policy", "default-src 'self' https: data:; img-src 'self' https: data: blob:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; script-src 'self' 'unsafe-inline' https://www.gstatic.com https://www.google.com/recaptcha/ https://www.gstatic.com/recaptcha/; connect-src 'self' https://identitytoolkit.googleapis.com https://securetoken.googleapis.com https://firestore.googleapis.com https://www.googleapis.com https://*.googleapis.com https://*.firebaseio.com; frame-src 'self' https://www.google.com https://www.recaptcha.net https://*.firebaseapp.com https://accounts.google.com https://facebook.com https://*.facebook.com https://www.youtube.com https://*.youtube.com https://youtube-nocookie.com https://*.youtube-nocookie.com; form-action 'self'; frame-ancestors 'none'; object-src 'none'")

    def send_body(self, status: int, body: bytes, content_type: str, headers: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.add_security_headers()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        cache_control = headers.get("Cache-Control", "no-store") if headers else "no-store"
        self.send_header("Cache-Control", cache_control)
        if headers:
            for key, value in headers.items():
                if key.lower() != "cache-control":
                    self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def send_file(self, file_path: Path, content_type: str, headers: dict[str, str] | None = None) -> None:
        """Stream a downloadable file without loading the entire artifact into memory."""
        size = file_path.stat().st_size
        self.send_response(200)
        self.add_security_headers()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(size))
        self.send_header("Accept-Ranges", "none")
        cache_control = headers.get("Cache-Control", "no-store") if headers else "no-store"
        self.send_header("Cache-Control", cache_control)
        if headers:
            for key, value in headers.items():
                if key.lower() != "cache-control":
                    self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            try:
                with file_path.open("rb") as source:
                    while chunk := source.read(1024 * 1024):
                        self.wfile.write(chunk)
            except (BrokenPipeError, ConnectionResetError):
                return

    def send_html(self, status: int, body: str, set_cookie: str | None = None) -> None:
        headers = {"Set-Cookie": set_cookie} if set_cookie else None
        self.send_body(status, body.encode("utf-8"), "text/html; charset=utf-8", headers)

    def send_json(self, status: int, data: dict[str, object]) -> None:
        self.send_body(status, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def redirect(self, location: str, set_cookie: str | None = None) -> None:
        headers = {"Location": location}
        if set_cookie:
            headers["Set-Cookie"] = set_cookie
        self.send_response(303)
        self.add_security_headers()
        for key, value in headers.items():
            self.send_header(key, value)
        self.send_header("Content-Length", "0")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def cookie(self, name: str) -> str:
        jar = SimpleCookie()
        try:
            jar.load(self.headers.get("Cookie", ""))
            return jar[name].value if name in jar else ""
        except Exception:
            return ""

    def cookie_header(self, name: str, value: str, max_age: int) -> str:
        parts = [f"{name}={value}", "Path=/", "HttpOnly", "SameSite=Lax", f"Max-Age={max_age}"]
        if os.environ.get("ARYLIDE_COOKIE_SECURE", "0") == "1":
            parts.append("Secure")
        return "; ".join(parts)

    def public_csrf(self) -> tuple[str, str | None]:
        token = self.cookie("ARYLIDE_CSRF")
        if valid_token(token):
            return token, None
        token = secrets.token_urlsafe(32)
        return token, self.cookie_header("ARYLIDE_CSRF", token, 24 * 60 * 60)

    def check_public_csrf(self, form: dict[str, object]) -> bool:
        cookie_token = self.cookie("ARYLIDE_CSRF")
        submitted = str(form.get("csrf", ""))
        return valid_token(cookie_token) and hmac.compare_digest(cookie_token, submitted)

    def parse_body(self) -> tuple[dict[str, object] | None, str | None]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return None, "Invalid request size."
        if length <= 0 or length > MAX_BODY_BYTES:
            return None, "Request is empty or too large."
        raw = self.rfile.read(length)
        content_type_header = self.headers.get("Content-Type", "")
        content_type = content_type_header.split(";", 1)[0].strip().lower()
        try:
            if content_type == "application/json":
                value = json.loads(raw.decode("utf-8"))
                if not isinstance(value, dict):
                    return None, "Invalid JSON body."
                return value, None
            if content_type == "application/x-www-form-urlencoded":
                parsed = parse_qs(raw.decode("utf-8"), keep_blank_values=True, max_num_fields=50)
                return {key: values[-1] for key, values in parsed.items()}, None
            if content_type == "multipart/form-data":
                boundary = ""
                for part in content_type_header.split(";"):
                    candidate = part.strip()
                    if candidate.lower().startswith("boundary="):
                        boundary = candidate.split("=", 1)[1].strip().strip('"')
                        break
                if not boundary:
                    return None, "Missing multipart boundary."
                message = BytesParser(policy=policy.default).parsebytes(
                    f"Content-Type: {content_type_header}\r\n\r\n".encode("utf-8") + raw
                )
                form: dict[str, object] = {}
                for part in message.iter_parts():
                    name = part.get_param("name", header="content-disposition")
                    if not name:
                        continue
                    filename = part.get_filename()
                    if filename:
                        item = {
                            "filename": filename,
                            "content": part.get_payload(decode=True) or b"",
                            "content_type": part.get_content_type() or "application/octet-stream",
                        }
                        existing = form.get(name)
                        if existing is None:
                            form[name] = item
                        elif isinstance(existing, list):
                            existing.append(item)
                        else:
                            form[name] = [existing, item]
                    else:
                        value = (part.get_payload(decode=True) or b"").decode("utf-8", "replace")
                        existing = form.get(name)
                        if existing is None:
                            form[name] = value
                        elif isinstance(existing, list):
                            existing.append(value)
                        else:
                            form[name] = [existing, value]
                return form, None
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError):
            return None, "Could not read the submitted form."
        return None, "Unsupported form type."

    def current_admin(self) -> tuple[sqlite3.Row | None, sqlite3.Row | None]:
        token = self.cookie("ARYLIDE_SESSION")
        if not valid_token(token):
            return None, None
        hashed = token_hash(token)
        with connect_db() as db:
            row = db.execute(
                "SELECT s.token_hash,s.admin_id,s.csrf_token,s.expires_at,a.email "
                "FROM sessions s JOIN admins a ON a.id=s.admin_id WHERE s.token_hash=?",
                (hashed,),
            ).fetchone()
        if not row or row["expires_at"] < int(time.time()):
            if row:
                with connect_db() as db:
                    db.execute("DELETE FROM sessions WHERE token_hash=?", (hashed,))
            return None, None
        return row, row

    def ensure_admin(self) -> tuple[sqlite3.Row | None, sqlite3.Row | None]:
        return self.current_admin()

    def admin_cookie(self, token: str, max_age: int = SESSION_SECONDS) -> str:
        return self.cookie_header("ARYLIDE_SESSION", token, max_age)

    def render_home(self) -> tuple[str, str | None]:
        csrf, set_cookie = self.public_csrf()
        index_file = (FRONTEND_DIR / "index.html") if (FRONTEND_DIR / "index.html").is_file() else (ROOT / "index.html")
        page = index_file.read_text(encoding="utf-8")
        if (ROOT / APK_FILENAME).is_file():
            page = page.replace("data-apk-download hidden", "data-apk-download")
        if (ROOT / WINDOWS_INSTALLER_FILENAME).is_file():
            page = page.replace("data-windows-download hidden", "data-windows-download")
        settings = get_settings()
        cms = get_public_cms_data()
        for key, value in cms["stats"].items():
            pattern = rf'(<strong data-stat="{re.escape(key)}">).*?(</strong>)'
            page = re.sub(pattern, lambda m, v=value: m.group(1) + escape(v) + m.group(2), page, count=1)
        reward = "৳" + format_bdt(settings.get("referral_reward_bdt", "200000"))
        page = re.sub(r'(<span data-setting="reward_display">).*?(</span>)', lambda m: m.group(1) + escape(reward) + m.group(2), page)
        page = page.replace("__PUBLIC_CSRF__", escape(csrf))
        seed = safe_json_for_script(cms)
        page = page.replace("</head>", f"<script>window.ARYLIDE_CMS_SEED={seed};</script></head>", 1)
        return page, set_cookie

    def serve_asset(self, relative: str) -> None:
        candidate = (FRONTEND_DIR / relative).resolve()
        if not candidate.is_file():
            candidate = (CONFIG_DIR / relative).resolve()
        if not candidate.is_file():
            candidate = (ROOT / relative).resolve()
        try:
            candidate.relative_to(ROOT.resolve())
        except ValueError:
            self.send_body(404, b"Not found", "text/plain; charset=utf-8")
            return
        if not candidate.is_file():
            self.send_body(404, b"Not found", "text/plain; charset=utf-8")
            return
        mime, _ = mimetypes.guess_type(str(candidate))
        data = candidate.read_bytes()
        headers = {"Cache-Control": "no-store" if candidate.name == "config.js" else "public, max-age=3600"}
        self.send_body(200, data, mime or "application/octet-stream", headers)

    def do_GET(self) -> None:  # noqa: N802
        path = unquote(urlsplit(self.path).path)
        if path in {"/", "/index.html", "/login", "/signup", "/my-meetings", "/book-meeting", "/projects", "/sectors", "/meetings", "/videos", "/more"} or path.startswith("/project/") or path.startswith("/sector/"): 
            page, cookie = self.render_home()
            self.send_html(200, page, cookie)
            return
        if path in {"/admin", "/admin/", "/admin.html"}:
            self.admin_home()
            return
        if path in {"/admin/export.csv", "/admin/referrals/export.csv", "/admin/appointments/export.csv", "/admin/enquiries/export.csv", "/admin/meetings/export.csv"}:
            self.admin_export()
            return
        if path == "/api/health":
            self.send_json(200, {"ok": True, "service": "arylide-local-app"})
            return
        if path == "/api/public-config":
            self.send_json(200, get_public_cms_data())
            return
        if path in {"/api/meeting-availability", "/api/meetings/availability"}:
            query = parse_qs(urlsplit(self.path).query)
            month = query.get("month", [""])[0]
            if not re.fullmatch(r"20\d{2}-(0[1-9]|1[0-2])", month):
                self.send_json(400, {"ok": False, "error": "Use a YYYY-MM month value."})
                return
            with connect_db() as db:
                rows = db.execute("SELECT meeting_date,meeting_time FROM meetings WHERE meeting_date LIKE ? AND status IN ('Pending','Confirmed','Rescheduled')", (month + "-%",)).fetchall()
            self.send_json(200, {"ok": True, "booked": [{"date": row["meeting_date"], "time": row["meeting_time"]} for row in rows]})
            return
        if path.startswith("/meeting-attachments/"):
            attachment_id = path[len("/meeting-attachments/"):]
            if not re.fullmatch(r"[a-f0-9]{32}", attachment_id):
                self.send_body(404, b"Not found", "text/plain; charset=utf-8")
                return
            query = parse_qs(urlsplit(self.path).query)
            attachment = None
            if query.get("admin") == ["1"]:
                session, _admin = self.ensure_admin()
                if session:
                    for item in get_cms_data().get("meeting_attachments", []):
                        if isinstance(item, dict) and item.get("id") == attachment_id:
                            attachment = item
                            break
            else:
                meeting_id = query.get("meeting_id", [""])[0]
                manage_token = query.get("manage_token", [""])[0]
                if re.fullmatch(r"[a-f0-9]{32}", meeting_id) and len(manage_token) >= 32:
                    with connect_db() as db:
                        meeting = db.execute(
                            "SELECT manage_token_hash,confirmation_attachments_json FROM meetings WHERE id=?",
                            (meeting_id,),
                        ).fetchone()
                    if meeting and hmac.compare_digest(meeting["manage_token_hash"], token_hash(manage_token)):
                        try:
                            meeting_attachments = json.loads(meeting["confirmation_attachments_json"])
                        except (TypeError, json.JSONDecodeError):
                            meeting_attachments = []
                        attachment = next(
                            (item for item in meeting_attachments if isinstance(item, dict) and item.get("id") == attachment_id),
                            None,
                        )
            if not isinstance(attachment, dict):
                self.send_body(404, b"Not found", "text/plain; charset=utf-8")
                return
            relative = str(attachment.get("path") or "")
            if not re.fullmatch(r"[a-f0-9]{32}\.[a-z0-9]{1,8}", relative):
                self.send_body(404, b"Not found", "text/plain; charset=utf-8")
                return
            attachment_root = (BACKEND_DIR / "data" / "meeting_attachments").resolve() if (BACKEND_DIR / "data").is_dir() else (ROOT / "data" / "meeting_attachments").resolve()
            file_path = (attachment_root / relative).resolve()
            try:
                file_path.relative_to(attachment_root)
            except ValueError:
                self.send_body(404, b"Not found", "text/plain; charset=utf-8")
                return
            if not file_path.is_file():
                self.send_body(404, b"Not found", "text/plain; charset=utf-8")
                return
            mime = mimetypes.guess_type(relative)[0] or "application/octet-stream"
            disposition = "inline" if mime.startswith(("image/", "video/")) or mime == "application/pdf" else "attachment"
            self.send_file(file_path, mime, {
                "Content-Disposition": f'{disposition}; filename="{file_path.name}"',
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "no-referrer",
            })
            return
        if path == "/config.js":
            self.serve_asset("config.js")
            return
        if path == "/favicon.ico":
            self.serve_asset("assets/favicon-64.png")
            return
        if path == "/download/android":
            apk = ROOT / APK_FILENAME
            if not apk.is_file():
                self.send_body(404, b"Android APK not included in this deployment.", "text/plain; charset=utf-8")
                return
            self.send_file(apk, "application/vnd.android.package-archive", {
                "Content-Disposition": f'attachment; filename="{APK_FILENAME}"',
                "Cache-Control": "no-store",
            })
            return
        if path == "/download/windows":
            installer = ROOT / WINDOWS_INSTALLER_FILENAME
            if not installer.is_file():
                self.send_body(404, b"Windows installer not included in this deployment.", "text/plain; charset=utf-8")
                return
            self.send_file(installer, "application/octet-stream", {
                "Content-Disposition": f'attachment; filename="{WINDOWS_INSTALLER_FILENAME}"',
                "Cache-Control": "no-store",
            })
            return
        if path in {"/manifest.webmanifest", "/service-worker.js", "/config.js", "/i18n.js", "/firebase.js", "/app.js", "/app.css", "/SOURCES.md", "/ANDROID-APK-INSTALL.md"}:
            self.serve_asset(path.lstrip("/"))
            return
        if path.startswith("/assets/"):
            self.serve_asset(path.lstrip("/"))
            return
        self.send_body(404, b"Not found", "text/plain; charset=utf-8")

    def do_HEAD(self) -> None:  # noqa: N802
        self.do_GET()

    def admin_home(self) -> None:
        with connect_db() as db:
            admin_count = db.execute("SELECT COUNT(*) AS n FROM admins").fetchone()["n"]
        session, admin = self.ensure_admin()
        if not session:
            csrf, cookie = self.public_csrf()
            if admin_count == 0 and ALLOW_WEB_ADMIN_SETUP:
                page = admin_setup_html(csrf)
            else:
                page = admin_login_html(csrf, setup_required=(admin_count == 0))
            self.send_html(200, page, cookie)
            return
        with connect_db() as db:
            referrals = db.execute("SELECT * FROM referral_leads ORDER BY id DESC").fetchall()
            appointments = db.execute("SELECT * FROM appointments ORDER BY id DESC").fetchall()
            enquiries = db.execute(
                "SELECT l.*, r.referral_code AS referrer_code FROM leads l "
                "LEFT JOIN leads r ON r.id=l.referred_by_id ORDER BY l.id DESC"
            ).fetchall()
            meetings = db.execute("SELECT * FROM meetings ORDER BY meeting_date DESC,meeting_time DESC").fetchall()
        landowners = [row for row in enquiries if "land" in str(row["interest"]).lower()]
        cms_data = get_cms_data()
        counts = {
            "referrals": len(referrals),
            "appointments": len(appointments),
            "enquiries": len(enquiries),
            "landowners": len(landowners),
            "meetings": len([row for row in meetings if row["status"] in {"Pending", "Confirmed"}]),
            "total": len(referrals) + len(appointments) + len(enquiries) + len(meetings),
            "projects": len(cms_data.get("projects", [])),
            "videos": len(cms_data.get("videos", [])),
            "pending_meetings": len([row for row in meetings if str(row["status"]).lower() == "pending"]),
            "pending_enquiries": len([row for row in enquiries if str(row["status"]).lower() == "pending"]),
            "pending_referrals": len([row for row in referrals if str(row["status"]).lower() == "pending"]),
            "total_pending": (
                len([row for row in meetings if str(row["status"]).lower() == "pending"])
                + len([row for row in enquiries if str(row["status"]).lower() == "pending"])
                + len([row for row in referrals if str(row["status"]).lower() == "pending"])
            ),
        }
        parsed = parse_qs(urlsplit(self.path).query)
        active_tab = parsed.get("tab", ["dashboard"])[0]
        valid_tabs = {
            "dashboard", "activity-logs", "cms", "projects", "referrals",
            "appointments", "enquiries", "landowners", "meetings", "videos",
            "social", "calculator", "media", "users", "security", "ai"
        }
        if active_tab not in valid_tabs:
            active_tab = "dashboard"
        toast_key = parsed.get("saved", [""])[0]
        toast = {
            "cms": "Homepage statistics and company info saved.",
            "project": "Project published to the website.",
            "referral": "Referral lead updated.",
            "deleted": "Referral lead deleted.",
            "enquiry": "Enquiry status updated.",
            "meeting": "Meeting settings saved.",
            "meeting_status": "Meeting status updated.",
            "meeting_deleted": "Meeting deleted.",
            "video": "Video library saved.",
            "social": "Social links saved.",
            "calculator": "Calculator assumptions saved.",
        }.get(toast_key, "")
        notifications_enabled = bool(
            os.environ.get("ARYLIDE_TELEGRAM_BOT_TOKEN", "").strip()
            and os.environ.get("ARYLIDE_TELEGRAM_CHAT_ID", "").strip()
        ) or bool(os.environ.get("ARYLIDE_N8N_WEBHOOK_URL", "").strip())
        page = admin_dashboard_html(
            admin, session, get_cms_data(), get_settings(), referrals, appointments,
            enquiries, counts, active_tab, toast, notifications_enabled, meetings=meetings,
        )
        self.send_html(200, page)

    def admin_export(self) -> None:
        session, _admin = self.ensure_admin()
        if not session:
            self.redirect("/admin.html")
            return
        path = unquote(urlsplit(self.path).path)
        with connect_db() as db:
            if path == "/admin/referrals/export.csv":
                rows = db.execute("SELECT * FROM referral_leads ORDER BY id DESC").fetchall()
                columns = ("id", "created_at", "your_name", "your_mobile", "buyer_name", "buyer_mobile", "project", "status", "updated_at")
                filename = "arylide-referrals"
            elif path == "/admin/appointments/export.csv":
                rows = db.execute("SELECT * FROM appointments ORDER BY id DESC").fetchall()
                columns = ("id", "created_at", "name", "phone", "appointment_date", "service", "message", "updated_at")
                filename = "arylide-appointments"
            elif path == "/admin/meetings/export.csv":
                rows = db.execute("SELECT id,serial_number,meeting_date,meeting_time,name,mobile,email,project,status,message,created_at,updated_at FROM meetings ORDER BY meeting_date,meeting_time").fetchall()
                columns = ("serial_number", "name", "mobile", "email", "project", "meeting_date", "meeting_time", "status", "message", "created_at", "updated_at")
                filename = "arylide-meetings"
            else:
                rows = db.execute(
                    "SELECT l.*, r.referral_code AS referrer_code FROM leads l "
                    "LEFT JOIN leads r ON r.id=l.referred_by_id ORDER BY l.id DESC"
                ).fetchall()
                columns = ("id", "name", "email", "phone", "interest", "referral_code", "referral_code_used", "referrer_code", "status", "reward_amount_bdt", "reward_paid", "message", "created_at", "updated_at")
                filename = "arylide-enquiries"
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(columns)
        for row in rows:
            safe_values = []
            for key in columns:
                text = str(row[key] if row[key] is not None else "")
                if text.lstrip().startswith(("=", "+", "-", "@", "\t")):
                    text = "'" + text
                safe_values.append(text)
            writer.writerow(safe_values)
        data = ("\ufeff" + output.getvalue()).encode("utf-8")
        self.send_body(200, data, "text/csv; charset=utf-8", {
            "Content-Disposition": f"attachment; filename={filename}-{datetime.now().strftime('%Y%m%d')}.csv"
        })

    def do_POST(self) -> None:  # noqa: N802
        path = unquote(urlsplit(self.path).path)
        data, error = self.parse_body()
        if error or data is None:
            if path.startswith("/api/"):
                self.send_json(400, {"ok": False, "error": error or "Invalid request."})
            else:
                self.send_body(400, b"Invalid request", "text/plain; charset=utf-8")
            return
        routes = {
            "/api/leads": self.create_lead,
            "/api/referral-leads": self.create_referral_lead,
            "/api/appointments": self.create_appointment,
            "/api/meetings": self.create_meeting,
            "/api/meetings/manage": self.manage_meeting,
            "/admin/setup": self.admin_setup,
            "/admin/login": self.admin_login,
            "/admin/update": self.admin_update,
            "/admin/settings": self.admin_settings,
            "/admin/cms": self.admin_cms,
            "/admin/project/create": self.admin_project_create,
            "/admin/project/save": self.admin_project_save,
            "/admin/videos/save": self.admin_videos_save,
            "/admin/social/save": self.admin_social_save,
            "/admin/calculator/save": self.admin_calculator_save,
            "/admin/meetings/settings": self.admin_meeting_settings,
            "/admin/meetings/update": self.admin_meeting_update,
            "/admin/meetings/delete": self.admin_meeting_delete,
            "/admin/referral/update": self.admin_referral_update,
            "/admin/referral/delete": self.admin_referral_delete,
            "/admin/logout": self.admin_logout,
        }
        handler = routes.get(path)
        if handler:
            handler(data)
        else:
            self.send_body(404, b"Not found", "text/plain; charset=utf-8")

    def create_referral_lead(self, data: dict[str, object]) -> None:
        if not self.check_public_csrf(data):
            self.send_json(403, {"ok": False, "error": "Session check failed. Refresh the page and try again."})
            return
        ip = self.client_address[0] if self.client_address else "local"
        if not allow_rate("referral-lead", ip, 30, 3600):
            self.send_json(429, {"ok": False, "error": "Too many submissions. Please try again later."})
            return
        your_name = str(data.get("your_name", "")).strip()
        your_mobile = str(data.get("your_mobile", "")).strip()
        buyer_name = str(data.get("buyer_name", "")).strip()
        buyer_mobile = str(data.get("buyer_mobile", "")).strip()
        project = str(data.get("project", "")).strip()
        client_id = str(data.get("client_id", "")).strip()
        if not re.fullmatch(r"[A-Za-z0-9._:-]{8,80}", client_id):
            client_id = secrets.token_urlsafe(18)
        if not your_name or len(your_name) > 100 or not buyer_name or len(buyer_name) > 100:
            self.send_json(400, {"ok": False, "error": "Enter both names (100 characters maximum)."})
            return
        if not valid_phone(your_mobile) or not valid_phone(buyer_mobile):
            self.send_json(400, {"ok": False, "error": "Enter valid mobile numbers."})
            return
        if not project or len(project) > 120:
            self.send_json(400, {"ok": False, "error": "Enter the project name (120 characters maximum)."})
            return
        now = utc_now()
        with connect_db() as db:
            cursor = db.execute(
                "INSERT OR IGNORE INTO referral_leads(client_id,your_name,your_mobile,buyer_name,buyer_mobile,project,status,created_at,updated_at) "
                "VALUES(?,?,?,?,?,?,?,?,?)",
                (client_id, your_name, your_mobile, buyer_name, buyer_mobile, project, "pending", now, now),
            )
            row = db.execute("SELECT id,created_at,status FROM referral_leads WHERE client_id=?", (client_id,)).fetchone()
        if cursor.rowcount:
            queue_notifications("referral", {
                "your_name": your_name, "your_mobile": your_mobile,
                "buyer_name": buyer_name, "buyer_mobile": buyer_mobile, "project": project,
            })
        self.send_json(201, {"ok": True, "message": "✅ Submitted!", "id": int(row["id"]), "created_at": row["created_at"], "status": row["status"]})

    def create_appointment(self, data: dict[str, object]) -> None:
        if not self.check_public_csrf(data):
            self.send_json(403, {"ok": False, "error": "Session check failed. Refresh the page and try again."})
            return
        ip = self.client_address[0] if self.client_address else "local"
        if not allow_rate("appointment", ip, 30, 3600):
            self.send_json(429, {"ok": False, "error": "Too many submissions. Please try again later."})
            return
        name = str(data.get("name", "")).strip()
        phone = str(data.get("phone", "")).strip()
        appointment_date = str(data.get("appointment_date", "")).strip()
        service = str(data.get("service", "")).strip()
        message = str(data.get("message", "")).strip()
        client_id = str(data.get("client_id", "")).strip()
        if not re.fullmatch(r"[A-Za-z0-9._:-]{8,80}", client_id):
            client_id = secrets.token_urlsafe(18)
        try:
            datetime.strptime(appointment_date, "%Y-%m-%d")
        except ValueError:
            self.send_json(400, {"ok": False, "error": "Choose a valid appointment date."})
            return
        if not name or len(name) > 100 or not valid_phone(phone):
            self.send_json(400, {"ok": False, "error": "Enter a name and valid mobile number."})
            return
        if not service or len(service) > 120 or len(message) > 1000:
            self.send_json(400, {"ok": False, "error": "Choose a service and keep the message under 1,000 characters."})
            return
        now = utc_now()
        with connect_db() as db:
            cursor = db.execute(
                "INSERT OR IGNORE INTO appointments(client_id,name,phone,appointment_date,service,message,created_at,updated_at) "
                "VALUES(?,?,?,?,?,?,?,?)",
                (client_id, name, phone, appointment_date, service, message, now, now),
            )
            row = db.execute("SELECT id,created_at FROM appointments WHERE client_id=?", (client_id,)).fetchone()
        if cursor.rowcount:
            queue_notifications("appointment", {
                "name": name, "phone": phone, "appointment_date": appointment_date,
                "service": service, "message": message,
            })
        self.send_json(201, {"ok": True, "message": "✅ Submitted!", "id": int(row["id"]), "created_at": row["created_at"]})

    def validate_meeting_slot(self, meeting_date: str, meeting_time: str) -> str | None:
        try:
            parsed_date = datetime.strptime(meeting_date, "%Y-%m-%d").date()
        except ValueError:
            return "Choose a valid meeting date."
        if parsed_date < date.today():
            return "Past dates cannot be booked."
        if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", meeting_time):
            return "Choose a valid meeting time."
        settings = get_cms_data()["meeting_settings"]
        off_days = settings.get("off_days", [5]) if isinstance(settings, dict) else [5]
        if ((parsed_date.weekday() + 1) % 7) in {int(day) for day in off_days if str(day).isdigit()}:
            return "This day is closed for meetings. Choose another date."
        slots = settings.get("slot_times", DEFAULT_MEETING_SETTINGS["slot_times"])
        if meeting_time not in slots:
            return "That meeting time is not available. Refresh and choose another slot."
        return None

    def create_meeting(self, data: dict[str, object]) -> None:
        if not self.check_public_csrf(data):
            self.send_json(403, {"ok": False, "error": "Session check failed. Refresh the app and try again."})
            return
        ip = self.client_address[0] if self.client_address else "local"
        if not allow_rate("meeting", ip, 12, 3600):
            self.send_json(429, {"ok": False, "error": "Too many booking attempts. Please try again later."})
            return
        name = str(data.get("name", "")).strip()
        mobile = str(data.get("mobile", "")).strip()
        email_address = str(data.get("email", "")).strip().lower()
        project = str(data.get("project", "")).strip()
        meeting_date = str(data.get("meeting_date", data.get("date", ""))).strip()
        meeting_time = str(data.get("meeting_time", data.get("time", ""))).strip()
        message = str(data.get("message", "")).strip()
        user_id = str(data.get("user_id", "")).strip()[:128]
        if firebase_auth_configured():
            firebase_user = verify_firebase_id_token(str(data.get("firebase_id_token", "")).strip())
            if not firebase_user:
                self.send_json(401, {"ok": False, "error": "Sign in to book a meeting; the Firebase session could not be verified."})
                return
            if user_id and user_id != firebase_user["uid"]:
                self.send_json(403, {"ok": False, "error": "The signed-in account does not match this booking."})
                return
            user_id = firebase_user["uid"]
            if firebase_user["email"]:
                email_address = firebase_user["email"]
        if not name or len(name) > 100 or not valid_phone(mobile):
            self.send_json(400, {"ok": False, "error": "Enter your name and a valid mobile number."})
            return
        if email_address and (not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email_address) or len(email_address) > 180):
            self.send_json(400, {"ok": False, "error": "Enter a valid email address."})
            return
        if not project or len(project) > 160 or len(message) > 1200:
            self.send_json(400, {"ok": False, "error": "Choose a project and keep the message under 1,200 characters."})
            return
        slot_error = self.validate_meeting_slot(meeting_date, meeting_time)
        if slot_error:
            self.send_json(400, {"ok": False, "error": slot_error})
            return
        meeting_id = uuid4().hex
        manage_token = secrets.token_urlsafe(32)
        now = utc_now()
        confirmation = get_cms_data()
        confirmation_attachments = confirmation.get("meeting_attachments", [])
        if not isinstance(confirmation_attachments, list):
            confirmation_attachments = []
        try:
            with connect_db() as db:
                db.execute("BEGIN IMMEDIATE")
                serial_number = generate_meeting_serial(db)
                cursor = db.execute(
                    "INSERT INTO meetings(id,serial_number,name,mobile,email,project,meeting_date,meeting_time,message,user_id,status,manage_token_hash,confirmation_message_en,confirmation_message_bn,confirmation_attachments_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (meeting_id, serial_number, name, mobile, email_address, project, meeting_date, meeting_time, message, user_id, "Pending", token_hash(manage_token), confirmation["meeting_message_en"], confirmation["meeting_message_bn"], json.dumps(confirmation_attachments, ensure_ascii=False), now, now),
                )
        except sqlite3.IntegrityError:
            self.send_json(409, {"ok": False, "error": "That time was just booked. Please choose another slot."})
            return
        payload = {"name": name, "mobile": mobile, "email": email_address, "project": project, "meeting_date": meeting_date, "meeting_time": meeting_time, "message": message, "meeting_id": meeting_id}
        queue_notifications("meeting", payload)
        customer_attachments = [{
            "id": item.get("id"),
            "name": item.get("name"),
            "type": item.get("type"),
            "size": item.get("size"),
            "url": f"/meeting-attachments/{item.get('id')}?meeting_id={meeting_id}&manage_token={manage_token}",
        } for item in confirmation_attachments if isinstance(item, dict) and re.fullmatch(r"[a-f0-9]{32}", str(item.get("id", "")))]
        self.send_json(201, {"ok": True, "message": "Submitted.", "id": meeting_id, "serial_number": serial_number, "manage_token": manage_token, "created_at": now, "status": "Pending", "name": name, "mobile": mobile, "email": email_address, "meeting_date": meeting_date, "meeting_time": meeting_time, "project": project, "confirmation_message_en": confirmation["meeting_message_en"], "confirmation_message_bn": confirmation["meeting_message_bn"], "confirmation_attachments": customer_attachments})

    def manage_meeting(self, data: dict[str, object]) -> None:
        if not self.check_public_csrf(data):
            self.send_json(403, {"ok": False, "error": "Session check failed. Refresh the app and try again."})
            return
        ip = self.client_address[0] if self.client_address else "local"
        if not allow_rate("meeting_manage", ip, 30, 3600):
            self.send_json(429, {"ok": False, "error": "Too many meeting-management requests. Please try again later."})
            return
        meeting_id = str(data.get("id", "")).strip()
        manage_token = str(data.get("manage_token", "")).strip()
        action = str(data.get("action", "")).strip().lower()
        if not re.fullmatch(r"[a-f0-9]{32}", meeting_id) or len(manage_token) < 32 or action not in {"cancel", "reschedule"}:
            self.send_json(400, {"ok": False, "error": "Invalid meeting-management request."})
            return
        firebase_user = None
        if firebase_auth_configured():
            firebase_user = verify_firebase_id_token(str(data.get("firebase_id_token", "")).strip())
            if not firebase_user:
                self.send_json(401, {"ok": False, "error": "Sign in to manage this meeting; the Firebase session could not be verified."})
                return
        with connect_db() as db:
            row = db.execute("SELECT * FROM meetings WHERE id=?", (meeting_id,)).fetchone()
            if not row or not hmac.compare_digest(row["manage_token_hash"], token_hash(manage_token)):
                self.send_json(404, {"ok": False, "error": "Meeting not found or management link is invalid."})
                return
            if firebase_user and row["user_id"] and row["user_id"] != firebase_user["uid"]:
                self.send_json(404, {"ok": False, "error": "Meeting not found or management link is invalid."})
                return
            if row["status"] in {"Completed", "Cancelled"}:
                self.send_json(400, {"ok": False, "error": "This meeting can no longer be changed."})
                return
            now = utc_now()
            if action == "cancel":
                db.execute("UPDATE meetings SET status='Cancelled',updated_at=? WHERE id=?", (now, meeting_id))
                self.send_json(200, {"ok": True, "status": "Cancelled"})
                return
            meeting_date = str(data.get("meeting_date", "")).strip()
            meeting_time = str(data.get("meeting_time", "")).strip()
            slot_error = self.validate_meeting_slot(meeting_date, meeting_time)
            if slot_error:
                self.send_json(400, {"ok": False, "error": slot_error})
                return
            try:
                db.execute("UPDATE meetings SET meeting_date=?,meeting_time=?,status='Pending',updated_at=? WHERE id=?", (meeting_date, meeting_time, now, meeting_id))
            except sqlite3.IntegrityError:
                self.send_json(409, {"ok": False, "error": "That time was just booked. Please choose another slot."})
                return
        self.send_json(200, {"ok": True, "status": "Pending", "meeting_date": meeting_date, "meeting_time": meeting_time})

    def admin_cms(self, data: dict[str, object]) -> None:
        session, _admin = self.require_admin_post(data)
        if not session:
            return
        stat_fields = {
            "projects": "stat_projects", "completed": "stat_completed", "happy_clients": "stat_happy_clients",
            "years_trust": "stat_years_trust", "area_built": "stat_area_built", "vision_sqft": "stat_vision_sqft",
        }
        stats: dict[str, str] = {}
        for key, field in stat_fields.items():
            value = str(data.get(field, "")).strip()
            if not re.fullmatch(r"[0-9][0-9,]{0,22}\+?", value):
                self.send_body(400, b"Statistics must contain digits, optional commas, and an optional trailing plus sign.", "text/plain; charset=utf-8")
                return
            stats[key] = value
        phone = str(data.get("company_phone", "")).strip()
        email_address = str(data.get("company_email", "")).strip().lower()
        address = str(data.get("company_address", "")).strip()
        if not valid_phone(phone) or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email_address) or len(email_address) > 180 or not address or len(address) > 220:
            self.send_body(400, b"Enter valid company contact information.", "text/plain; charset=utf-8")
            return
        try:
            reward = int(str(data.get("referral_reward_bdt", "")).strip())
        except ValueError:
            self.send_body(400, b"Enter a whole-number reward amount.", "text/plain; charset=utf-8")
            return
        if reward < 0 or reward > 10_000_000:
            self.send_body(400, b"Reward amount is outside the allowed range.", "text/plain; charset=utf-8")
            return
        set_setting("stats_json", json.dumps(stats, ensure_ascii=False, separators=(",", ":")))
        set_setting("company_info_json", json.dumps({"phone": phone, "email": email_address, "address": address}, ensure_ascii=False, separators=(",", ":")))
        set_setting("referral_reward_bdt", str(reward))
        self.redirect("/admin.html?tab=cms&saved=cms")

    def admin_project_save(self, data: dict[str, object]) -> None:
        session, _admin = self.require_admin_post(data)
        if not session:
            return
        name = str(data.get("name", "")).strip()
        name_bn = str(data.get("name_bn", "")).strip()
        location = str(data.get("location", "")).strip()
        location_bn = str(data.get("location_bn", "")).strip()
        description_en = str(data.get("description_en", data.get("description", ""))).strip()
        description_bn = str(data.get("description_bn", "")).strip()
        amenities_en = str(data.get("amenities_en", "")).strip()
        amenities_bn = str(data.get("amenities_bn", "")).strip()
        raw_images = data.get("images", data.get("images_text", []))
        if isinstance(raw_images, str):
            images = [line.strip() for line in raw_images.splitlines() if line.strip()]
        elif isinstance(raw_images, list):
            images = [str(value).strip() for value in raw_images if str(value).strip()]
        else:
            images = []
        if not images and str(data.get("image_url", "")).strip():
            images = [str(data.get("image_url", "")).strip()]
        if not name or len(name) > 100 or not location or len(location) > 140 or len(description_en) > 2000 or len(description_bn) > 2000 or len(amenities_en) > 1200 or len(amenities_bn) > 1200:
            self.send_json(400, {"ok": False, "error": "Complete the project title and location, and keep descriptions within the limits."})
            return
        if len(images) > 10:
            self.send_json(400, {"ok": False, "error": "Add at most 10 project images."})
            return
        for image in images:
            parsed = urlsplit(image)
            local_image = image.startswith("/assets/") and ".." not in Path(image).parts
            remote_image = parsed.scheme == "https" and bool(parsed.netloc) and not parsed.username and not parsed.password
            if len(image) > 2048 or not (local_image or remote_image):
                self.send_json(400, {"ok": False, "error": "Project images must be HTTPS URLs or app-local /assets/ paths."})
                return
        try:
            position = int(str(data.get("position", "99") or "99"))
            area_sft = int(str(data.get("area_sft", "0") or "0"))
            price_per_sft = int(str(data.get("price_per_sft", "0") or "0"))
            sector = str(data.get("sector", "")).strip()
            if position < 1 or position > 999 or area_sft < 0 or area_sft > 1000000 or price_per_sft < 0 or price_per_sft > 10000000:
                raise ValueError
        except ValueError:
            self.send_json(400, {"ok": False, "error": "Position, area, or price is outside the allowed range."})
            return
        status = str(data.get("status", "details")).strip().lower()
        if status not in {"booking", "sold", "completed", "coming_soon", "details", "land"}:
            self.send_json(400, {"ok": False, "error": "Choose a valid project status."})
            return
        project_id = str(data.get("id", "")).strip() or secrets.token_hex(8)
        if not re.fullmatch(r"[A-Za-z0-9_-]{2,80}", project_id):
            project_id = secrets.token_hex(8)
        project = {
            "id": project_id, "name": name, "name_bn": name_bn or name,
            "location": location, "location_bn": location_bn or location, "sector": sector,
            "status": status, "type": str(data.get("type", "residential")).strip()[:80],
            "images": images, "description_en": description_en, "description_bn": description_bn or description_en,
            "amenities_en": amenities_en, "amenities_bn": amenities_bn or amenities_en,
            "price_per_sft": str(price_per_sft) if price_per_sft else "",
            "area_sft": str(area_sft) if area_sft else "",
            "featured": str(data.get("featured", "")).lower() in {"1", "true", "yes", "on"},
            "position": position, "map_query": str(data.get("map_query", "")).strip()[:200],
        }
        cms = get_cms_data()
        projects = list(cms["projects"])
        existing_index = next((index for index, item in enumerate(projects) if str(item.get("id", "")) == project_id), None)
        if existing_index is None:
            if len(projects) >= 200:
                self.send_json(400, {"ok": False, "error": "The project list has reached its limit."})
                return
            projects.append(project)
        else:
            projects[existing_index] = project
        projects.sort(key=lambda item: int(item.get("position", 999) or 999))
        set_setting("projects_json", json.dumps(projects, ensure_ascii=False, separators=(",", ":")))
        self.send_json(200, {"ok": True, "message": "Project saved.", "project": project})

    def admin_videos_save(self, data: dict[str, object]) -> None:
        session, _admin = self.require_admin_post(data)
        if not session:
            return
        raw = data.get("videos", [])
        if not isinstance(raw, list) or len(raw) > 100:
            self.send_json(400, {"ok": False, "error": "Video list is invalid or too large."})
            return
        videos = []
        for index, item in enumerate(raw):
            if not isinstance(item, dict):
                continue
            title = str(item.get("title_en", item.get("title", ""))).strip()[:160]
            title_bn = str(item.get("title_bn", title)).strip()[:160] or title
            youtube = str(item.get("youtube_url", item.get("url", ""))).strip()
            thumbnail = str(item.get("thumbnail", "")).strip()
            parsed = urlsplit(youtube)
            if not title or parsed.scheme != "https" or parsed.netloc.lower() not in {"youtube.com", "www.youtube.com", "youtu.be", "www.youtube-nocookie.com", "m.youtube.com"}:
                self.send_json(400, {"ok": False, "error": "Each video needs a title and a valid HTTPS YouTube link."})
                return
            local_image = thumbnail.startswith("/assets/") and ".." not in Path(thumbnail).parts
            remote_image = False
            if thumbnail.startswith("data:image/"):
                remote_image = len(thumbnail) <= 2_000_000 and re.match(r"^data:image/(png|jpeg|webp);base64,[A-Za-z0-9+/=]+$", thumbnail) is not None
            else:
                image_parts = urlsplit(thumbnail)
                remote_image = image_parts.scheme == "https" and bool(image_parts.netloc) and not image_parts.username and not image_parts.password
            if thumbnail and not (local_image or remote_image):
                self.send_json(400, {"ok": False, "error": "Thumbnail must be an HTTPS URL, app-local image, or small PNG/JPEG/WebP upload."})
                return
            videos.append({"id": str(item.get("id", ""))[:80] or secrets.token_hex(8), "title": title, "title_en": title, "title_bn": title_bn, "thumbnail": thumbnail, "youtube_url": youtube, "position": index + 1})
        set_setting("videos_json", json.dumps(videos, ensure_ascii=False, separators=(",", ":")))
        self.send_json(200, {"ok": True, "videos": videos})

    def admin_social_save(self, data: dict[str, object]) -> None:
        session, _admin = self.require_admin_post(data)
        if not session:
            return
        fields = {"facebook":"facebook", "linkedin":"linkedin", "x":"x", "youtube":"youtube", "post_embed_link":"post_embed_link"}
        values = {}
        for key, field in fields.items():
            value = str(data.get(key, "")).strip()
            if value:
                parsed = urlsplit(value)
                if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
                    self.send_json(400, {"ok": False, "error": "Social links must use valid HTTPS URLs."})
                    return
                if key == "post_embed_link" and parsed.netloc.lower() not in {"facebook.com", "www.facebook.com", "m.facebook.com", "youtube.com", "www.youtube.com", "youtu.be", "www.youtube-nocookie.com"}:
                    self.send_json(400, {"ok": False, "error": "Post embed URL must be a Facebook or YouTube link."})
                    return
            values[key] = value[:1000]
        set_setting("social_links_json", json.dumps(values, ensure_ascii=False, separators=(",", ":")))
        self.send_json(200, {"ok": True, "social": values})

    def admin_calculator_save(self, data: dict[str, object]) -> None:
        session, _admin = self.require_admin_post(data)
        if not session:
            return
        try:
            values = {
                "area_sft": int(str(data.get("area_sft", 2850))),
                "price_per_sft": int(str(data.get("price_per_sft", 8500))),
                "down_percent": int(str(data.get("down_percent", 50))),
                "months": int(str(data.get("months", 36))),
                "annual_growth_percent": float(str(data.get("annual_growth_percent", 14))),
                "growth_years": int(str(data.get("growth_years", 3))),
            }
        except (TypeError, ValueError):
            self.send_json(400, {"ok": False, "error": "Enter valid numeric calculator assumptions."})
            return
        if not (1 <= values["area_sft"] <= 1000000 and 1 <= values["price_per_sft"] <= 10000000 and 0 <= values["down_percent"] <= 100 and 1 <= values["months"] <= 600 and 0 <= values["annual_growth_percent"] <= 100 and 1 <= values["growth_years"] <= 50):
            self.send_json(400, {"ok": False, "error": "Calculator values are outside the allowed range."})
            return
        set_setting("calculator_json", json.dumps(values, ensure_ascii=False, separators=(",", ":")))
        self.send_json(200, {"ok": True, "calculator": values})

    def admin_meeting_settings(self, data: dict[str, object]) -> None:
        session, _admin = self.require_admin_post(data)
        if not session:
            return
        current = get_cms_data()
        settings = dict(current.get("meeting_settings", DEFAULT_MEETING_SETTINGS))
        schedule_fields = {"off_days", "slot_times", "working_start", "working_end", "slot_duration", "location_bn", "location_en"}
        if schedule_fields.intersection(data):
            raw_off_days = data.get("off_days", settings.get("off_days", [5]))
            raw_slots = data.get("slot_times", settings.get("slot_times", []))
            off_days = raw_off_days if isinstance(raw_off_days, list) else str(raw_off_days).split(",")
            slots = raw_slots if isinstance(raw_slots, list) else str(raw_slots).split(",")
            try:
                off_days = sorted({int(str(day).strip()) for day in off_days if str(day).strip() != ""})
                start = str(data.get("working_start", settings.get("working_start", "10:00"))).strip()
                end = str(data.get("working_end", settings.get("working_end", "18:00"))).strip()
                duration = int(str(data.get("slot_duration", settings.get("slot_duration", 60))))
            except (TypeError, ValueError):
                self.send_json(400, {"ok": False, "error": "Meeting schedule settings are invalid."})
                return
            slots = sorted({str(value).strip() for value in slots if re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", str(value).strip())})
            if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", start) or not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", end) or not 15 <= duration <= 240 or any(day < 0 or day > 6 for day in off_days) or not slots or len(slots) > 30:
                self.send_json(400, {"ok": False, "error": "Set valid working hours, off days, duration and at least one time slot."})
                return
            settings = {"working_start":start,"working_end":end,"slot_duration":duration,"off_days":off_days,"slot_times":slots,"location_bn":str(data.get("location_bn", settings.get("location_bn", ""))).strip()[:300] or DEFAULT_MEETING_SETTINGS["location_bn"],"location_en":str(data.get("location_en", settings.get("location_en", ""))).strip()[:300] or DEFAULT_MEETING_SETTINGS["location_en"]}

        message_en = current["meeting_message_en"]
        message_bn = current["meeting_message_bn"]
        if "meeting_message_en" in data:
            message_en = str(data.get("meeting_message_en", "")).strip()[:2000] or DEFAULT_MEETING_CONFIRMATION["en"]
        if "meeting_message_bn" in data:
            message_bn = str(data.get("meeting_message_bn", "")).strip()[:2000] or DEFAULT_MEETING_CONFIRMATION["bn"]
        raw_attachments = data.get("meeting_attachments")
        attachment_payload = current.get("meeting_attachments", [])
        if isinstance(raw_attachments, dict) or isinstance(raw_attachments, list):
            try:
                persisted = persist_uploaded_attachments(raw_attachments)
            except ValueError as error:
                self.send_json(400, {"ok": False, "error": str(error)})
                return
            remove_ids = data.get("remove_attachment_ids", [])
            if not isinstance(remove_ids, list):
                remove_ids = [remove_ids]
            remove_ids = {str(item) for item in remove_ids}
            attachment_payload = [item for item in attachment_payload if str(item.get("id", "")) not in remove_ids]
            attachment_payload = persisted + attachment_payload
        if schedule_fields.intersection(data):
            set_setting("meeting_settings_json", json.dumps(settings, ensure_ascii=False, separators=(",", ":")))
        if "meeting_message_en" in data:
            set_setting("meeting_message_en", message_en)
        if "meeting_message_bn" in data:
            set_setting("meeting_message_bn", message_bn)
        if isinstance(raw_attachments, dict) or isinstance(raw_attachments, list):
            set_setting("meeting_attachments_json", json.dumps(attachment_payload, ensure_ascii=False, separators=(",", ":")))
        self.send_json(200, {"ok": True, "meeting_settings": settings, "meeting_message_en": message_en or DEFAULT_MEETING_CONFIRMATION["en"], "meeting_message_bn": message_bn or DEFAULT_MEETING_CONFIRMATION["bn"], "meeting_attachments": attachment_payload})

    def admin_meeting_update(self, data: dict[str, object]) -> None:
        session, _admin = self.require_admin_post(data)
        if not session:
            return
        meeting_id = str(data.get("meeting_id", "")).strip()
        status = str(data.get("status", "")).strip().title()
        if status not in {"Pending", "Confirmed", "Completed", "Cancelled"}:
            self.send_json(400, {"ok": False, "error": "Invalid meeting status."})
            return
        try:
            with connect_db() as db:
                db.execute("UPDATE meetings SET status=?,updated_at=? WHERE id=?", (status, utc_now(), meeting_id))
                if db.total_changes == 0:
                    self.send_json(404, {"ok": False, "error": "Meeting not found."})
                    return
        except sqlite3.IntegrityError:
            self.send_json(409, {"ok": False, "error": "That time is already occupied."})
            return
        self.send_json(200, {"ok": True, "status": status})

    def admin_meeting_delete(self, data: dict[str, object]) -> None:
        session, _admin = self.require_admin_post(data)
        if not session:
            return
        meeting_id = str(data.get("meeting_id", "")).strip()
        with connect_db() as db:
            cursor = db.execute("DELETE FROM meetings WHERE id=?", (meeting_id,))
        if cursor.rowcount == 0:
            self.send_json(404, {"ok": False, "error": "Meeting not found."})
            return
        self.send_json(200, {"ok": True})

    def admin_project_create(self, data: dict[str, object]) -> None:
        session, _admin = self.require_admin_post(data)
        if not session:
            return
        name = str(data.get("name", "")).strip()
        location = str(data.get("location", "")).strip()
        image_url = str(data.get("image_url", "")).strip()
        description = str(data.get("description", "")).strip()
        if not name or len(name) > 100 or not location or len(location) > 120 or not description or len(description) > 1000:
            self.send_body(400, b"Complete the project name, location, and description within their limits.", "text/plain; charset=utf-8")
            return
        parsed = urlsplit(image_url)
        local_image = image_url.startswith("/assets/") and ".." not in Path(image_url).parts
        remote_image = parsed.scheme == "https" and bool(parsed.netloc) and not parsed.username and not parsed.password
        if len(image_url) > 2048 or not (local_image or remote_image):
            self.send_body(400, b"Image URL must be HTTPS or an app-local /assets/ path.", "text/plain; charset=utf-8")
            return
        cms = get_cms_data()
        projects = list(cms["projects"])
        if len(projects) >= 200:
            self.send_body(400, b"The project list has reached its limit.", "text/plain; charset=utf-8")
            return
        projects.append({"id": secrets.token_hex(8), "name": name, "location": location, "image_url": image_url, "description": description, "created_at": utc_now()})
        set_setting("projects_json", json.dumps(projects, ensure_ascii=False, separators=(",", ":")))
        self.redirect("/admin.html?tab=cms&saved=project")

    def admin_referral_update(self, data: dict[str, object]) -> None:
        session, _admin = self.require_admin_post(data)
        if not session:
            return
        try:
            referral_id = int(str(data.get("referral_id", "")))
        except ValueError:
            self.send_body(400, b"Invalid referral ID", "text/plain; charset=utf-8")
            return
        status = str(data.get("status", "")).strip().lower()
        if status not in REFERRAL_STATUSES:
            self.send_body(400, b"Invalid referral status", "text/plain; charset=utf-8")
            return
        with connect_db() as db:
            cursor = db.execute("UPDATE referral_leads SET status=?,updated_at=? WHERE id=?", (status, utc_now(), referral_id))
        if not cursor.rowcount:
            self.send_body(404, b"Referral lead not found", "text/plain; charset=utf-8")
            return
        self.redirect(f"/admin.html?tab=referrals&saved=referral&id={referral_id}&status={status}")

    def admin_referral_delete(self, data: dict[str, object]) -> None:
        session, _admin = self.require_admin_post(data)
        if not session:
            return
        try:
            referral_id = int(str(data.get("referral_id", "")))
        except ValueError:
            self.send_body(400, b"Invalid referral ID", "text/plain; charset=utf-8")
            return
        with connect_db() as db:
            cursor = db.execute("DELETE FROM referral_leads WHERE id=?", (referral_id,))
        if not cursor.rowcount:
            self.send_body(404, b"Referral lead not found", "text/plain; charset=utf-8")
            return
        self.redirect(f"/admin.html?tab=referrals&saved=deleted&id={referral_id}")

    def admin_setup(self, data: dict[str, object]) -> None:
        if not ALLOW_WEB_ADMIN_SETUP:
            self.send_body(403, b"Web admin setup is disabled. Use the local CLI.", "text/plain; charset=utf-8")
            return
        if not self.check_public_csrf(data):
            self.send_body(403, b"Session check failed. Reload the setup page and try again.", "text/plain; charset=utf-8")
            return
        identity = self.client_address[0] if self.client_address else "local"
        if not allow_rate("admin-setup", identity, 5, 3600):
            self.send_html(429, admin_setup_html(str(data.get("csrf", "")), "Too many setup attempts. Try again later."))
            return
        email_address = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))
        confirmation = str(data.get("confirmation", ""))
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email_address) or len(email_address) > 180:
            self.send_html(400, admin_setup_html(str(data.get("csrf", "")), "Enter a valid admin email address."))
            return
        if len(password) < 12 or len(password) > 200:
            self.send_html(400, admin_setup_html(str(data.get("csrf", "")), "Choose a password between 12 and 200 characters."))
            return
        if not hmac.compare_digest(password, confirmation):
            self.send_html(400, admin_setup_html(str(data.get("csrf", "")), "The passwords did not match."))
            return
        if password.lower() in {"password123456", "changeme123456"}:
            self.send_html(400, admin_setup_html(str(data.get("csrf", "")), "Choose a private password, not a common demo credential."))
            return
        password_hash = make_password_hash(password)
        try:
            with connect_db() as db:
                db.execute("BEGIN IMMEDIATE")
                admin_count = db.execute("SELECT COUNT(*) FROM admins").fetchone()[0]
                if admin_count:
                    self.redirect("/admin.html")
                    return
                db.execute("INSERT INTO admins(email,password_hash,created_at) VALUES(?,?,?)", (email_address, password_hash, utc_now()))
        except sqlite3.IntegrityError:
            self.send_html(400, admin_setup_html(str(data.get("csrf", "")), "That admin email is already in use."))
            return
        self.redirect("/admin.html")

    def create_lead(self, data: dict[str, object]) -> None:
        if not self.check_public_csrf(data):
            self.send_json(403, {"ok": False, "error": "Session check failed. Refresh the page and try again."})
            return
        ip = self.client_address[0] if self.client_address else "local"
        if not allow_rate("lead", ip, 30, 3600):
            self.send_json(429, {"ok": False, "error": "Too many submissions. Please try again later."})
            return
        name = str(data.get("name", "")).strip()
        email_address = str(data.get("email", "")).strip().lower()
        phone = str(data.get("phone", "")).strip()
        interest = str(data.get("interest", "")).strip()
        message = str(data.get("message", "")).strip()
        used_code = str(data.get("referral_code", "")).strip().upper()
        if not name or len(name) > 100:
            self.send_json(400, {"ok": False, "error": "Enter your name (up to 100 characters)."})
            return
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email_address) or len(email_address) > 180:
            self.send_json(400, {"ok": False, "error": "Enter a valid email address."})
            return
        if not re.fullmatch(r"[0-9+() \-]{8,20}", phone):
            self.send_json(400, {"ok": False, "error": "Enter a valid phone number."})
            return
        if interest not in VALID_INTERESTS:
            self.send_json(400, {"ok": False, "error": "Choose a service interest from the list."})
            return
        if len(message) > 2000:
            self.send_json(400, {"ok": False, "error": "Message must be 2,000 characters or fewer."})
            return
        if len(used_code) > 24 or (used_code and not re.fullmatch(r"[A-Z0-9-]+", used_code)):
            self.send_json(400, {"ok": False, "error": "Referral code format is invalid."})
            return
        with connect_db() as db:
            referrer = None
            if used_code:
                referrer = db.execute("SELECT id FROM leads WHERE referral_code=?", (used_code,)).fetchone()
                if not referrer:
                    self.send_json(400, {"ok": False, "error": "That referral code was not found. Check it and try again, or clear the field."})
                    return
            code = generate_referral_code(db)
            now = utc_now()
            cursor = db.execute(
                "INSERT INTO leads(referral_code,referral_code_used,referred_by_id,name,email,phone,interest,message,status,created_at,updated_at) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (code, used_code, referrer["id"] if referrer else None, name, email_address, phone, interest, message, "pending", now, now),
            )
            lead_id = int(cursor.lastrowid)
        queue_notifications("enquiry", {"name": name, "email": email_address, "phone": phone, "interest": interest, "message": message, "referral_code": used_code})
        self.send_json(201, {
            "ok": True,
            "message": "✅ Submitted!",
            "id": lead_id,
            "created_at": now,
            "referral_code": code,
            "referred": bool(used_code),
        })

    def admin_login(self, data: dict[str, object]) -> None:
        if not self.check_public_csrf(data):
            self.send_body(403, b"Session check failed. Return to the login page and try again.", "text/plain; charset=utf-8")
            return
        identity = self.client_address[0] if self.client_address else "local"
        if not allow_rate("login", identity, 6, 600):
            self.send_html(429, admin_login_html(str(data.get("csrf", "")), "Too many login attempts. Wait a few minutes and try again."))
            return
        email_address = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))
        with connect_db() as db:
            admin = db.execute("SELECT id,email,password_hash FROM admins WHERE email=?", (email_address,)).fetchone()
        if not admin or not verify_password(password, admin["password_hash"]):
            time.sleep(0.35)
            self.send_html(401, admin_login_html(str(data.get("csrf", "")), "Email or password was not correct."))
            return
        token = secrets.token_urlsafe(40)
        hashed = token_hash(token)
        now = int(time.time())
        csrf = secrets.token_urlsafe(32)
        with connect_db() as db:
            db.execute("DELETE FROM sessions WHERE expires_at < ?", (now,))
            db.execute("INSERT INTO sessions(token_hash,admin_id,csrf_token,expires_at,created_at) VALUES(?,?,?,?,?)", (hashed, admin["id"], csrf, now + SESSION_SECONDS, now))
        self.redirect("/admin.html", self.admin_cookie(token))

    def require_admin_post(self, data: dict[str, object]) -> tuple[sqlite3.Row | None, sqlite3.Row | None]:
        session, admin = self.ensure_admin()
        if not session:
            self.redirect("/admin.html")
            return None, None
        submitted = str(data.get("csrf", ""))
        if not hmac.compare_digest(submitted, session["csrf_token"]):
            self.send_body(403, b"Session expired. Reload the admin page and try again.", "text/plain; charset=utf-8")
            return None, None
        return session, admin

    def admin_update(self, data: dict[str, object]) -> None:
        session, _admin = self.require_admin_post(data)
        if not session:
            return
        try:
            lead_id = int(str(data.get("lead_id", "")))
        except ValueError:
            self.send_body(400, b"Invalid lead ID", "text/plain; charset=utf-8")
            return
        status = str(data.get("status", "")).strip().lower()
        if status not in VALID_STATUSES:
            self.send_body(400, b"Invalid status", "text/plain; charset=utf-8")
            return
        paid = "reward_paid" in data
        with connect_db() as db:
            lead = db.execute("SELECT * FROM leads WHERE id=?", (lead_id,)).fetchone()
            if not lead:
                self.send_body(404, b"Lead not found", "text/plain; charset=utf-8")
                return
            if lead["reward_paid"] and status != "converted":
                self.send_body(400, b"A paid referral cannot be moved out of Converted status.", "text/plain; charset=utf-8")
                return
            if paid and (status != "converted" or not lead["referred_by_id"]):
                self.send_body(400, b"Only a converted referral lead can be marked paid.", "text/plain; charset=utf-8")
                return
            amount = int(lead["reward_amount_bdt"] or 0)
            if lead["referred_by_id"] and status == "converted" and lead["status"] != "converted":
                settings = dict(db.execute("SELECT key,value FROM settings").fetchall())
                amount = int(settings.get("referral_reward_bdt", DEFAULT_SETTINGS["referral_reward_bdt"]))
            elif status != "converted" and not lead["reward_paid"]:
                amount = 0
            elif not lead["referred_by_id"]:
                amount = 0
                paid = False
            db.execute(
                "UPDATE leads SET status=?, reward_amount_bdt=?, reward_paid=?, updated_at=? WHERE id=?",
                (status, amount, int(paid), utc_now(), lead_id),
            )
        self.redirect(f"/admin.html?tab=enquiries&saved=enquiry&id={lead_id}&status={status}")

    def admin_settings(self, data: dict[str, object]) -> None:
        """Backward-compatible reward-only settings endpoint."""
        session, _admin = self.require_admin_post(data)
        if not session:
            return
        try:
            reward = int(str(data.get("referral_reward_bdt", "")).strip())
        except ValueError:
            self.send_body(400, b"Enter a whole-number reward amount.", "text/plain; charset=utf-8")
            return
        if reward < 0 or reward > 10_000_000:
            self.send_body(400, b"Reward amount is outside the allowed range.", "text/plain; charset=utf-8")
            return
        set_setting("referral_reward_bdt", str(reward))
        self.redirect("/admin.html?tab=cms&saved=cms")

    def admin_logout(self, data: dict[str, object]) -> None:
        session, _admin = self.require_admin_post(data)
        if not session:
            return
        with connect_db() as db:
            db.execute("DELETE FROM sessions WHERE token_hash=?", (session["token_hash"],))
        self.redirect("/admin.html", self.cookie_header("ARYLIDE_SESSION", "", 0))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ARYLIDE local website and referral CRM")
    parser.add_argument("--host", default=os.environ.get("ARYLIDE_HOST", "127.0.0.1"), help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("ARYLIDE_PORT", "4173")), help="Port (default: 4173)")
    parser.add_argument("--create-admin", action="store_true", help="Create the first admin account")
    parser.add_argument("--reset-admin", action="store_true", help="Reset an existing admin password")
    parser.add_argument("--email", default=DEFAULT_ADMIN_EMAIL, help=f"Admin email for create/reset (default: {DEFAULT_ADMIN_EMAIL})")
    args = parser.parse_args()
    init_db()
    if args.create_admin and args.reset_admin:
        raise SystemExit("Choose either --create-admin or --reset-admin, not both.")
    if args.create_admin:
        create_or_reset_admin(args.email, reset=False)
        return
    if args.reset_admin:
        create_or_reset_admin(args.email, reset=True)
        return
    with connect_db() as db:
        admin_count = db.execute("SELECT COUNT(*) FROM admins").fetchone()[0]
    if not admin_count:
        print("Admin setup is required before opening /admin.")
        print("Stop this server after startup and run: python run.py --create-admin")
    server = ThreadingHTTPServer((args.host, args.port), AppHandler)
    server.daemon_threads = True
    print(f"ARYLIDE local app running at http://{args.host}:{args.port}/")
    print(f"Admin panel: http://{args.host}:{args.port}/admin")
    print(f"Local database: {DB_PATH}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping ARYLIDE app…")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
