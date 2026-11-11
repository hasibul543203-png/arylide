import sqlite3
import json
import os
import hashlib
from datetime import datetime, timezone
import shutil

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DB = os.path.join(APP_DIR, 'data', 'arylide.sqlite3')
BACKEND_DB = os.path.join(APP_DIR, 'backend', 'data', 'arylide.sqlite3')

def get_sha256(path):
    if not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def export_backup():
    print("=== ARYLIDE ZERO-DATA-LOSS BACKUP & SEED EXPORTER ===")
    hash_data = get_sha256(DATA_DB)
    hash_backend = get_sha256(BACKEND_DB)
    print(f"Initial data/arylide.sqlite3 SHA-256: {hash_data}")
    print(f"Initial backend/data/arylide.sqlite3 SHA-256: {hash_backend}")

    backups_dir = os.path.join(APP_DIR, 'backups')
    os.makedirs(backups_dir, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # Safe timestamped file copies of databases
    if os.path.exists(DATA_DB):
        shutil.copy2(DATA_DB, os.path.join(backups_dir, f"arylide_data_{ts}.sqlite3"))
    if os.path.exists(BACKEND_DB):
        shutil.copy2(BACKEND_DB, os.path.join(backups_dir, f"arylide_backend_{ts}.sqlite3"))

    target_db = BACKEND_DB if os.path.exists(BACKEND_DB) else DATA_DB
    conn = sqlite3.connect(f"file:{target_db}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    tables = ['settings', 'leads', 'referral_leads', 'appointments', 'meetings']
    snapshot = {
        'exported_at': datetime.now(timezone.utc).isoformat(),
        'source': target_db,
        'tables': {}
    }

    for t in tables:
        try:
            c.execute(f"SELECT * FROM {t}")
            rows = [dict(r) for r in c.fetchall()]
            snapshot['tables'][t] = rows
            print(f"Exported table '{t}': {len(rows)} rows")
        except Exception as e:
            print(f"Note on table '{t}': {e}")
            snapshot['tables'][t] = []

    conn.close()

    snapshot_path = os.path.join(backups_dir, 'sqlite-full-snapshot.json')
    with open(snapshot_path, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    print(f"Saved snapshot to: {snapshot_path}")

    # Build CMS Seed
    c_settings = {r['key']: r['value'] for r in snapshot['tables'].get('settings', [])}
    def parse_j(val, default):
        if not val:
            return default
        try:
            return json.loads(val)
        except Exception:
            return default

    cms_seed = {
        'stats': parse_j(c_settings.get('stats_json'), {}),
        'projects': parse_j(c_settings.get('projects_json'), []),
        'company': parse_j(c_settings.get('company_info_json'), {}),
        'meeting_settings': parse_j(c_settings.get('meeting_settings_json'), {}),
        'calculator': parse_j(c_settings.get('calculator_json'), {}),
        'social': parse_j(c_settings.get('social_links_json'), {}),
        'videos': parse_j(c_settings.get('videos_json'), []),
        'referral_reward_bdt': c_settings.get('referral_reward_bdt', '200000'),
        'meeting_message_en': c_settings.get('meeting_message_en', ''),
        'meeting_message_bn': c_settings.get('meeting_message_bn', '')
    }

    seed_js = "/* window.ARYLIDE_CMS_SEED auto-generated from read-only SQLite snapshot */\nwindow.ARYLIDE_CMS_SEED = " + json.dumps(cms_seed, indent=2, ensure_ascii=False) + ";\n"

    for dest in [os.path.join(APP_DIR, 'frontend', 'cms-seed.js'), os.path.join(APP_DIR, 'cms-seed.js')]:
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(seed_js)
        print(f"Written: {dest}")

    # Verify hashes unchanged
    new_hash_data = get_sha256(DATA_DB)
    new_hash_backend = get_sha256(BACKEND_DB)
    assert hash_data == new_hash_data, "DATA_DB hash altered!"
    assert hash_backend == new_hash_backend, "BACKEND_DB hash altered!"
    print("SUCCESS: 0 bytes altered in SQLite databases.")

if __name__ == '__main__':
    export_backup()
