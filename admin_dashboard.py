from __future__ import annotations

import html
import json
from typing import Any
from urllib.parse import quote


def esc(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def safe_script_json(value: object) -> str:
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )


def _date_text(value: object) -> str:
    return esc(str(value or "").replace("T", " ").replace("+00:00", " UTC"))


def _empty_row(cols: int, text: str) -> str:
    return f'<tr><td class="empty" colspan="{cols}">{esc(text)}</td></tr>'


def _option(value: str, label: str, selected: str) -> str:
    return f'<option value="{esc(value)}"{" selected" if selected == value else ""}>{esc(label)}</option>'


# In-memory session audit logs for display
DEFAULT_AUDIT_LOGS = [
    {"user": "Super Admin", "action": "Logged into Sovereign Admin Suite", "target": "Local Session", "time": "Just now", "tag": "AUTH"},
    {"user": "System", "action": "SQLite Database initialized & schema verified", "target": "arylide.sqlite3", "time": "Startup", "tag": "SYSTEM"},
    {"user": "Catalog", "action": "Project catalog synchronized with default assets", "target": "CMS Catalog", "time": "Cached", "tag": "CMS"},
]


STYLE = r"""
:root {
  --primary: #003629;
  --primary-hover: #074737;
  --primary-container: #1b4d3e;
  --on-primary: #ffffff;
  --on-primary-container: #8abda9;
  --secondary: #c5a059;
  --secondary-hover: #b38e46;
  --secondary-container: #fed488;
  --on-secondary-container: #785a1a;
  --bg-deep: #08120e;
  --bg-canvas: #0b1812;
  --panel: #11231b;
  --panel-elevated: #162c22;
  --panel-recessed: #0a1610;
  --text-main: #eff2ea;
  --text-muted: #9ba9a0;
  --text-gold: #e2c875;
  --line: rgba(255, 255, 255, 0.11);
  --line-strong: rgba(255, 255, 255, 0.18);
  --line-gold: rgba(197, 160, 89, 0.35);
  --accent-gold: #c5a059;
  --accent-green: #34d399;
  --accent-blue: #60a5fa;
  --accent-red: #f87171;
  --font-serif: 'Playfair Display', Georgia, serif;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  --font-mono: 'SF Mono', Consolas, 'Liberation Mono', Menlo, monospace;
}

* { box-sizing: border-box; }
body {
  margin: 0;
  background-color: var(--bg-deep);
  background-image: radial-gradient(circle at 10% 20%, rgba(27, 77, 62, 0.22) 0%, transparent 40%),
                    radial-gradient(circle at 90% 80%, rgba(197, 160, 89, 0.08) 0%, transparent 45%);
  color: var(--text-main);
  font: 13.5px/1.55 var(--font-sans);
  -webkit-font-smoothing: antialiased;
  min-height: 100vh;
}

a { color: var(--text-gold); text-decoration: none; transition: color .15s ease; }
a:hover { color: #ffffff; }
button, input, select, textarea { font: inherit; }
button { cursor: pointer; }

/* Institutional App Layout */
.app-layout {
  display: flex;
  min-height: 100vh;
}

/* Sidebar Navigation */
.sidebar {
  width: 270px;
  flex: none;
  background: rgba(9, 20, 15, 0.98);
  border-right: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 100;
  backdrop-filter: blur(20px);
  overflow-y: auto;
  transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-header {
  padding: 18px 20px;
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}

.brand-crest {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  background: linear-gradient(135deg, #1b4d3e, #0a2118);
  border: 1px solid var(--line-gold);
  display: grid;
  place-items: center;
  color: var(--text-gold);
  font-weight: 800;
  font-size: 17px;
  font-family: var(--font-serif);
  box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}

.brand-info {
  display: flex;
  flex-direction: column;
}

.brand-title {
  color: #ffffff;
  font-family: var(--font-serif);
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.08em;
  line-height: 1.15;
}

.brand-subtitle {
  color: var(--text-gold);
  font-size: 8.5px;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  margin-top: 3px;
}

.sidebar-close-btn {
  display: none;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 20px;
  padding: 4px;
}

.sidebar-env {
  padding: 9px 18px;
  background: rgba(197, 160, 89, 0.07);
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 9.5px;
  font-weight: 750;
  letter-spacing: 0.12em;
  color: var(--text-gold);
  text-transform: uppercase;
}

.pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent-gold);
  box-shadow: 0 0 0 3px rgba(197, 160, 89, 0.25);
  animation: pulse 2.2s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(197, 160, 89, 0.45); }
  70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(197, 160, 89, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(197, 160, 89, 0); }
}

.sidebar-menu {
  padding: 14px 12px;
  flex: 1;
}

.menu-section-label {
  padding: 10px 10px 5px;
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.nav-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 8.5px 12px;
  border-radius: 7px;
  color: #c4d0c7;
  font-size: 11.5px;
  font-weight: 650;
  margin-bottom: 2px;
  transition: all .15s ease;
  background: transparent;
  border: 1px solid transparent;
  width: 100%;
  text-align: left;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.045);
  color: #ffffff;
}

.nav-link.active, .nav-link[aria-selected="true"] {
  background: linear-gradient(90deg, rgba(27, 77, 62, 0.45), rgba(27, 77, 62, 0.18));
  border-color: rgba(197, 160, 89, 0.35);
  color: #ffffff;
  font-weight: 750;
}

.nav-link-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.nav-link-left svg {
  width: 16px;
  height: 16px;
  flex: none;
  opacity: 0.85;
}

.nav-link.active .nav-link-left svg {
  color: var(--text-gold);
  opacity: 1;
}

.nav-link-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-badge {
  padding: 2px 7px;
  border-radius: 99px;
  font-size: 9px;
  font-weight: 750;
  background: rgba(255, 255, 255, 0.07);
  color: var(--text-muted);
}

.nav-badge.gold {
  background: rgba(197, 160, 89, 0.2);
  color: var(--text-gold);
  border: 1px solid rgba(197, 160, 89, 0.35);
}

.nav-badge.live {
  background: rgba(52, 211, 153, 0.15);
  color: var(--accent-green);
  border: 1px solid rgba(52, 211, 153, 0.3);
}

.sidebar-footer {
  padding: 14px 18px;
  border-top: 1px solid var(--line);
  background: rgba(0, 0, 0, 0.25);
}

.audit-status-pill {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 7px 10px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid var(--line);
  font-size: 9px;
  color: var(--text-muted);
}

/* Main Content Area */
.main-wrapper {
  margin-left: 270px;
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

/* Top Header Bar */
.topbar {
  position: sticky;
  top: 0;
  z-index: 90;
  height: 64px;
  background: rgba(10, 20, 16, 0.88);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--line);
  padding: 0 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  max-width: 580px;
}

.mobile-toggle {
  display: none;
  background: transparent;
  border: 1px solid var(--line);
  border-radius: 6px;
  color: var(--text-main);
  padding: 6px;
  place-items: center;
}

.global-search-wrap {
  position: relative;
  width: 100%;
}

.global-search-input {
  width: 100%;
  height: 38px;
  padding: 0 14px 0 36px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--line);
  color: var(--text-main);
  font-size: 11.5px;
  transition: all .15s ease;
}

.global-search-input:focus {
  outline: none;
  border-color: var(--accent-gold);
  background: rgba(255, 255, 255, 0.07);
  box-shadow: 0 0 0 3px rgba(197, 160, 89, 0.15);
}

.search-icon {
  position: absolute;
  left: 11px;
  top: 50%;
  transform: translateY(-50%);
  width: 15px;
  height: 15px;
  color: var(--text-muted);
  pointer-events: none;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: none;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  min-height: 36px;
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  transition: all .15s ease;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-main);
  white-space: nowrap;
}

.btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--line-strong);
  color: #ffffff;
}

.btn-primary {
  background: var(--primary);
  border-color: rgba(197, 160, 89, 0.4);
  color: #ffffff;
}

.btn-primary:hover {
  background: var(--primary-hover);
  border-color: var(--accent-gold);
}

.btn-gold {
  background: var(--secondary);
  border-color: var(--secondary);
  color: #111a14;
}

.btn-gold:hover {
  background: var(--secondary-hover);
}

.btn-danger {
  color: #ffb8b4;
  border-color: rgba(239, 68, 68, 0.25);
  background: rgba(239, 68, 68, 0.08);
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.18);
  color: #ffffff;
}

.btn-sm {
  min-height: 30px;
  padding: 5px 10px;
  font-size: 10px;
}

.user-profile-pill {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 5px 10px 5px 6px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid var(--line);
}

.user-avatar {
  width: 27px;
  height: 27px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1b4d3e, #c5a059);
  color: #ffffff;
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 11px;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-email {
  font-size: 10.5px;
  font-weight: 700;
  line-height: 1.2;
}

.user-role {
  font-size: 8px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-gold);
}

/* Page Container */
.page-container {
  padding: 26px 32px 56px;
  max-width: 1440px;
  width: 100%;
  margin: 0 auto;
}

/* Environment Advisory Banner */
.env-advisory-banner {
  padding: 12px 18px;
  border-radius: 9px;
  background: rgba(197, 160, 89, 0.08);
  border: 1px solid rgba(197, 160, 89, 0.28);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 24px;
}

.advisory-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.advisory-badge {
  padding: 3px 8px;
  border-radius: 4px;
  background: var(--secondary);
  color: #121814;
  font-size: 9px;
  font-weight: 850;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.advisory-text {
  font-size: 11px;
  color: #e5dbbe;
}

.advisory-sync-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 20px;
  background: rgba(17, 35, 27, 0.8);
  border: 1px solid var(--line);
  font-family: var(--font-mono);
  font-size: 9.5px;
  color: var(--accent-green);
}

/* Header & Executive Actions */
.dashboard-header-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 26px;
  flex-wrap: wrap;
}

.header-kicker {
  font-size: 9.5px;
  font-weight: 850;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--text-gold);
  margin-bottom: 4px;
}

.header-title {
  font-family: var(--font-serif);
  font-size: clamp(26px, 3.4vw, 38px);
  font-weight: 600;
  line-height: 1.1;
  margin: 0;
  color: #ffffff;
}

.header-subtitle {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 6px;
  max-width: 640px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 9px;
  flex-wrap: wrap;
}

/* 5 Core Institutional KPI Summary Row */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 28px;
}

.kpi-card {
  padding: 16px 18px;
  border-radius: 10px;
  background: var(--panel);
  border: 1px solid var(--line);
  box-shadow: 0 4px 16px rgba(0,0,0,0.18);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 126px;
  transition: transform .18s ease, border-color .18s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  border-color: var(--line-gold);
}

.kpi-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.kpi-label {
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.kpi-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.04);
  display: grid;
  place-items: center;
  color: var(--text-gold);
}

.kpi-value {
  font-family: var(--font-serif);
  font-size: clamp(26px, 2.8vw, 34px);
  font-weight: 600;
  line-height: 1;
  color: #ffffff;
}

.kpi-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 10px;
  color: var(--text-muted);
}

.kpi-trend {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--accent-green);
  font-weight: 700;
}

/* Two-Column Command Grid (65% / 35%) */
.command-grid {
  display: grid;
  grid-template-columns: 1.8fr 1fr;
  gap: 22px;
  align-items: start;
}

.command-col {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

/* Institutional Cards */
.card {
  border-radius: 10px;
  background: var(--panel);
  border: 1px solid var(--line);
  box-shadow: 0 8px 24px rgba(0,0,0,0.18);
  overflow: hidden;
}

.card-header {
  padding: 18px 20px 14px;
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.card-title-group {
  display: flex;
  align-items: center;
  gap: 9px;
}

.card-title {
  margin: 0;
  font-family: var(--font-serif);
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
}

.card-subtitle {
  font-size: 10.5px;
  color: var(--text-muted);
  margin-top: 2px;
}

.card-body {
  padding: 18px 20px;
}

/* Approvals & Directives List */
.approvals-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.approval-item {
  padding: 14px 16px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  transition: all .15s ease;
}

.approval-item:hover {
  background: rgba(255, 255, 255, 0.045);
  border-color: var(--line-strong);
}

.approval-left {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  min-width: 0;
}

.approval-icon-box {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  background: rgba(27, 77, 62, 0.45);
  border: 1px solid var(--line-gold);
  color: var(--text-gold);
  display: grid;
  place-items: center;
  flex: none;
}

.approval-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.approval-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.approval-name {
  font-size: 12.5px;
  font-weight: 750;
  color: #ffffff;
}

.approval-pill {
  padding: 2px 7px;
  border-radius: 4px;
  font-size: 9px;
  font-weight: 750;
  text-transform: uppercase;
}

.approval-pill.jv { background: rgba(197, 160, 89, 0.18); color: var(--text-gold); }
.approval-pill.meeting { background: rgba(52, 211, 153, 0.15); color: var(--accent-green); }
.approval-pill.video { background: rgba(96, 165, 250, 0.15); color: var(--accent-blue); }

.approval-desc {
  font-size: 10.5px;
  color: var(--text-muted);
}

.approval-actions {
  display: flex;
  align-items: center;
  gap: 7px;
  flex: none;
}

/* Portfolio Grid */
.portfolio-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.portfolio-card {
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid var(--line);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.portfolio-img-wrap {
  position: relative;
  height: 120px;
  background: #0f1e17;
  overflow: hidden;
}

.portfolio-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform .3s ease;
}

.portfolio-card:hover .portfolio-img-wrap img {
  transform: scale(1.04);
}

.portfolio-badge-top {
  position: absolute;
  top: 7px;
  left: 7px;
  padding: 3px 6px;
  border-radius: 4px;
  background: rgba(10, 20, 15, 0.85);
  color: var(--text-gold);
  font-size: 8.5px;
  font-weight: 800;
  backdrop-filter: blur(4px);
}

.portfolio-info {
  padding: 12px 14px;
}

.portfolio-name {
  font-size: 13px;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 2px;
}

.portfolio-loc {
  font-size: 10px;
  color: var(--text-muted);
  margin: 0 0 8px;
}

.progress-bar-wrap {
  margin: 8px 0;
}

.progress-label-row {
  display: flex;
  justify-content: space-between;
  font-size: 9px;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.progress-track {
  width: 100%;
  height: 4px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.08);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 2px;
  background: linear-gradient(90deg, #1b4d3e, #c5a059);
}

.portfolio-footer {
  padding: 8px 14px 10px;
  border-top: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 10px;
}

/* System Status List */
.status-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-row {
  padding: 9px 12px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.status-row-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent-green);
}

.status-dot.orange { background: #f59e0b; }

.status-row-title {
  font-size: 11px;
  font-weight: 700;
  color: #ffffff;
}

.status-row-desc {
  font-size: 9px;
  color: var(--text-muted);
}

/* AI Guardrails Widget */
.ai-accuracy-box {
  padding: 14px;
  border-radius: 8px;
  background: rgba(197, 160, 89, 0.06);
  border: 1px solid rgba(197, 160, 89, 0.25);
  margin-bottom: 12px;
}

.ai-accuracy-top {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 8px;
}

.accuracy-rate {
  font-family: var(--font-serif);
  font-size: 28px;
  font-weight: 600;
  color: var(--text-gold);
  line-height: 1;
}

/* Tab Panels */
.tab-panel[hidden] {
  display: none !important;
}

/* Common Table & Form Styling from Original Implementation (100% Preserved) */
.form-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.field { display: flex; flex-direction: column; gap: 5px; min-width: 0; }
.field label { color: var(--text-muted); font-size: 9.5px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }
.field input, .field select, .field textarea {
  width: 100%; min-height: 38px; padding: 8px 10px; border: 1px solid var(--line);
  border-radius: 5px; color: var(--text-main); background: #0b1712; font-size: 11px;
}
.field textarea { min-height: 76px; resize: vertical; }
.field input:focus, .field select:focus, .field textarea:focus {
  outline: 2px solid rgba(197, 160, 89, 0.35); border-color: var(--accent-gold);
}
.form-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.cms-stats { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.section-title { margin: 20px 0 10px; color: var(--text-gold); font-size: 12.5px; font-weight: 800; letter-spacing: .05em; }
.help { color: var(--text-muted); font-size: 9.5px; line-height: 1.6; }
.status { min-height: 18px; margin: 8px 0 0; color: var(--text-gold); font-size: 10.5px; }
.searchbar { display: flex; flex-wrap: wrap; align-items: flex-end; gap: 9px; margin: 12px 0 16px; }
.searchbar .field { min-width: 200px; }
.tablewrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 6px; }
.table { width: 100%; border-collapse: collapse; font-size: 10.5px; }
.table th, .table td { padding: 10px 10px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
.table th { position: sticky; top: 0; color: var(--text-gold); background: #13241c; font-size: 8.5px; letter-spacing: .08em; text-transform: uppercase; white-space: nowrap; }
.table tr:last-child td { border-bottom: 0; }
.table td small { display: block; margin-top: 3px; color: var(--text-muted); font-size: 9px; }
.table td strong { color: #ffffff; }
.rowform { display: flex; align-items: center; gap: 5px; margin: 0; }
.rowform select { min-height: 30px; max-width: 120px; padding: 4px; border: 1px solid var(--line); border-radius: 4px; color: var(--text-main); background: #0b1712; font-size: 10px; }
.rowform button { min-height: 28px; padding: 4px 8px; border: 1px solid var(--line); border-radius: 4px; color: #fff; background: rgba(255,255,255,.06); font-size: 9px; }
.rowform .delete { color: #fca5a5; border-color: rgba(239, 68, 68, 0.3); }
.tag { display: inline-block; padding: 3px 7px; border-radius: 20px; color: var(--text-gold); background: rgba(197, 160, 89, 0.14); font-size: 8px; font-weight: 800; text-transform: uppercase; }
.tag.contacted { color: var(--accent-blue); background: rgba(96, 165, 250, 0.12); }
.tag.sold, .tag.converted { color: var(--accent-green); background: rgba(52, 211, 153, 0.14); }
.tag.closed { color: var(--accent-red); background: rgba(248, 113, 113, 0.14); }
.empty { padding: 28px !important; text-align: center !important; color: var(--text-muted); }
.project-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin: 12px 0 0; }
.project-item { padding: 10px 12px; border: 1px solid var(--line); border-radius: 5px; background: rgba(255,255,255,.025); }
.project-item strong { display: block; color: var(--text-gold); font-size: 11px; }
.project-item span { display: block; margin-top: 4px; color: var(--text-muted); font-size: 9.5px; overflow-wrap: anywhere; }
.meeting-calendar { display: grid; gap: 7px; margin: 12px 0; padding: 12px; border: 1px solid var(--line); border-radius: 6px; background: rgba(0,0,0,.15); max-height: 190px; overflow-y: auto; }
.calendar-meeting { padding: 8px 9px; border-bottom: 1px solid var(--line); font-size: 10px; }
.calendar-meeting:last-child { border-bottom: 0; }
.alert { margin: 12px 0; padding: 10px 14px; border: 1px solid rgba(197, 160, 89, 0.35); border-radius: 6px; color: #ede3be; background: rgba(197, 160, 89, 0.08); font-size: 10.5px; }

/* Responsive Media Queries */
@media (max-width: 1200px) {
  .kpi-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .command-grid { grid-template-columns: 1fr; }
  .portfolio-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 900px) {
  .sidebar { transform: translateX(-100%); width: 280px; }
  .sidebar.open { transform: translateX(0); }
  .main-wrapper { margin-left: 0; }
  .mobile-toggle { display: grid; }
  .sidebar-close-btn { display: block; }
  .sidebar-overlay {
    position: fixed; inset: 0; background: rgba(0,0,0,0.65); backdrop-filter: blur(4px);
    z-index: 99; display: none;
  }
  .sidebar-overlay.active { display: block; }
  .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .form-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .page-container { padding: 20px 18px 48px; }
  .topbar { padding: 0 18px; }
}

@media (max-width: 600px) {
  .kpi-grid { grid-template-columns: 1fr; }
  .portfolio-grid { grid-template-columns: 1fr; }
  .cms-stats { grid-template-columns: 1fr; }
  .form-grid { grid-template-columns: 1fr; }
  .project-list { grid-template-columns: 1fr; }
  .topbar-right .btn-primary span { display: none; }
  .user-email { display: none; }
}
"""


def _svg_icon(name: str) -> str:
    icons = {
        "dashboard": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg>',
        "history": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
        "cms": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>',
        "project": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="9" y1="22" x2="9" y2="2"/><line x1="15" y1="22" x2="15" y2="2"/><line x1="4" y1="12" x2="20" y2="12"/></svg>',
        "media": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>',
        "video": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>',
        "share": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>',
        "meeting": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
        "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>',
        "referral": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
        "land": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
        "calc": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="6" x2="16" y2="6"/><line x1="16" y1="14" x2="16" y2="18"/><path d="M16 10h.01"/><path d="M12 10h.01"/><path d="M8 10h.01"/><path d="M12 14h.01"/><path d="M8 14h.01"/><path d="M12 18h.01"/><path d="M8 18h.01"/></svg>',
        "users": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
        "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
        "ai": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
        "plus": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
        "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>',
    }
    return icons.get(name, "")


def admin_dashboard_html(
    admin: Any,
    session: Any,
    cms: dict[str, Any],
    settings: dict[str, str],
    referral_rows: list[Any],
    appointment_rows: list[Any],
    enquiry_rows: list[Any],
    counts: dict[str, int],
    active_tab: str = "dashboard",
    toast: str = "",
    notifications_enabled: bool = False,
    meetings: list[Any] | None = None,
) -> str:
    csrf = esc(session["csrf_token"])
    stats = cms["stats"]
    company = cms["company"]
    projects = cms["projects"]
    meetings = meetings or []
    videos = cms.get("videos", [])
    social = cms.get("social", {})
    calculator = cms.get("calculator", {})
    meeting_settings = cms.get("meeting_settings", {})
    total = counts.get("total", 0)
    pending_meetings_count = counts.get("pending_meetings", 0)
    pending_enquiries_count = counts.get("pending_enquiries", 0)
    pending_referrals_count = counts.get("pending_referrals", 0)
    total_pending = counts.get("total_pending", pending_meetings_count + pending_enquiries_count)

    toast_html = f'<div class="alert" role="status">{esc(toast)}</div>' if toast else ""
    notice_html = (
        '<div class="alert">Server-side Telegram/N8N notifications are enabled for this process.</div>'
        if notifications_enabled else
        '<div class="alert">Telegram/N8N notifications are off until server-side environment variables are configured. Local database lead storage remains active.</div>'
    )

    # 1. Existing Lead / Table rows generation
    referral_html: list[str] = []
    for row in referral_rows:
        search = " ".join(str(row[key] or "") for key in ("your_name", "your_mobile", "buyer_name", "buyer_mobile", "project", "status")).lower()
        status = str(row["status"])
        opts = "".join(_option(code, label, status) for code, label in (("pending", "Pending"), ("contacted", "Contacted"), ("sold", "Sold")))
        referral_html.append(
            f'<tr data-row="referral" data-search="{esc(search)}" data-status="{esc(status)}">'
            f'<td>{_date_text(row["created_at"])}</td><td><strong>{esc(row["your_name"])}</strong></td>'
            f'<td>{esc(row["your_mobile"])}</td><td><strong>{esc(row["buyer_name"])}</strong></td>'
            f'<td>{esc(row["buyer_mobile"])}</td><td>{esc(row["project"])}</td>'
            f'<td><form class="rowform" method="post" action="/admin/referral/update">'
            f'<input type="hidden" name="csrf" value="{csrf}"><input type="hidden" name="referral_id" value="{int(row["id"])}">'
            f'<select name="status" aria-label="Referral status">{opts}</select><button type="submit">Save</button></form></td>'
            f'<td><form class="rowform" method="post" action="/admin/referral/delete" onsubmit="return confirm(\'Delete this referral lead?\')">'
            f'<input type="hidden" name="csrf" value="{csrf}"><input type="hidden" name="referral_id" value="{int(row["id"])}">'
            f'<button class="delete" type="submit">Delete</button></form></td></tr>'
        )
    if not referral_html:
        referral_html.append(_empty_row(8, "No referral leads yet."))

    appointment_html: list[str] = []
    for row in appointment_rows:
        search = " ".join(str(row[key] or "") for key in ("name", "phone", "appointment_date", "service", "message")).lower()
        appointment_html.append(
            f'<tr data-row="appointment" data-search="{esc(search)}" data-service="{esc(row["service"])}"><td>{_date_text(row["appointment_date"])}</td>'
            f'<td><strong>{esc(row["name"])}</strong></td><td>{esc(row["phone"])}</td>'
            f'<td>{esc(row["service"])}</td><td>{esc(row["message"])}</td></tr>'
        )
    if not appointment_html:
        appointment_html.append(_empty_row(5, "No appointment bookings yet."))

    meeting_html: list[str] = []
    pending_meeting_approvals: list[str] = []
    for row in meetings:
        status = str(row["status"])
        search = " ".join(str(row[key] or "") for key in ("serial_number", "meeting_date", "meeting_time", "name", "mobile", "email", "project", "status")).lower()
        opts = "".join(_option(code, code, status) for code in ("Pending", "Confirmed", "Completed", "Cancelled"))
        phone_digits = "".join(ch for ch in str(row["mobile"] or "") if ch.isdigit())
        wa_message = quote(f"Meeting {row['meeting_date']} {row['meeting_time']} · {row['project']}", safe="")
        meeting_html.append(
            f'<tr data-row="meeting" data-search="{esc(search)}" data-date="{esc(row["meeting_date"])}">'
            f'<td><strong>{esc(row["serial_number"])}</strong></td><td>{esc(row["meeting_date"])}</td><td>{esc(row["meeting_time"])}</td>'
            f'<td><strong>{esc(row["name"])}</strong><small>{esc(row["email"])}</small></td><td>{esc(row["mobile"])}</td>'
            f'<td>{esc(row["project"])}</td><td><form class="rowform ajax-form" method="post" action="/admin/meetings/update">'
            f'<input type="hidden" name="csrf" value="{csrf}"><input type="hidden" name="meeting_id" value="{esc(row["id"])}">'
            f'<select name="status" aria-label="Meeting status">{opts}</select><button type="submit">Save</button></form></td>'
            f'<td><a class="btn btn-sm" target="_blank" rel="noopener noreferrer" href="https://wa.me/{phone_digits}?text={esc(wa_message)}">WhatsApp</a> '
            f'<a class="btn btn-sm" href="tel:{esc(row["mobile"])}">Call</a> '
            f'<form class="rowform ajax-form" method="post" action="/admin/meetings/delete"><input type="hidden" name="csrf" value="{csrf}"><input type="hidden" name="meeting_id" value="{esc(row["id"])}"><button class="delete" type="submit">Delete</button></form></td></tr>'
        )
        if status.lower() == "pending" and len(pending_meeting_approvals) < 4:
            pending_meeting_approvals.append(
                f'<div class="approval-item">'
                f'<div class="approval-left">'
                f'<div class="approval-icon-box">{_svg_icon("meeting")}</div>'
                f'<div class="approval-meta">'
                f'<div class="approval-title-row"><span class="approval-name">{esc(row["name"])}</span>'
                f'<span class="approval-pill meeting">Meeting Request</span><span style="font-size:10px;color:var(--text-gold);">{esc(row["meeting_date"])} {esc(row["meeting_time"])}</span></div>'
                f'<span class="approval-desc">{esc(row["project"])} • {esc(row["mobile"])}</span>'
                f'</div></div>'
                f'<div class="approval-actions">'
                f'<form class="ajax-form" method="post" action="/admin/meetings/update">'
                f'<input type="hidden" name="csrf" value="{csrf}"><input type="hidden" name="meeting_id" value="{esc(row["id"])}"><input type="hidden" name="status" value="Confirmed">'
                f'<button class="btn btn-sm btn-primary" type="submit">Confirm</button></form>'
                f'<a class="btn btn-sm" target="_blank" rel="noopener noreferrer" href="https://wa.me/{phone_digits}?text={esc(wa_message)}">WhatsApp</a>'
                f'</div></div>'
            )

    if not meeting_html:
        meeting_html.append(_empty_row(8, "No meetings booked yet."))

    enquiry_html: list[str] = []
    pending_enquiry_approvals: list[str] = []
    for row in enquiry_rows:
        status = str(row["status"])
        search = " ".join(str(row[key] or "") for key in ("name", "email", "phone", "interest", "message", "referral_code", "referral_code_used", "status")).lower()
        opts = "".join(_option(code, code.title(), status) for code in ("pending", "contacted", "converted", "closed"))
        date_text = _date_text(row["created_at"])
        enquiry_html.append(
            f'<tr data-row="enquiry" data-search="{esc(search)}" data-status="{esc(status)}">'
            f'<td>{date_text}</td><td><strong>{esc(row["name"])}</strong><small>{esc(row["email"])}</small></td>'
            f'<td>{esc(row["phone"])}</td><td>{esc(row["interest"])}</td>'
            f'<td>{esc(row["message"])}</td><td><span class="tag {esc(status)}">{esc(status.title())}</span></td>'
            f'<td><form class="rowform" method="post" action="/admin/update">'
            f'<input type="hidden" name="csrf" value="{csrf}"><input type="hidden" name="lead_id" value="{int(row["id"])}">'
            f'<select name="status" aria-label="Enquiry status">{opts}</select><button type="submit">Save</button></form></td></tr>'
        )
        if status.lower() == "pending" and len(pending_enquiry_approvals) < 3:
            is_land = "land" in str(row["interest"]).lower()
            pill_cls = "jv" if is_land else "meeting"
            pill_label = "Landowner Inquiry" if is_land else "General Lead"
            pending_enquiry_approvals.append(
                f'<div class="approval-item">'
                f'<div class="approval-left">'
                f'<div class="approval-icon-box">{_svg_icon("land" if is_land else "mail")}</div>'
                f'<div class="approval-meta">'
                f'<div class="approval-title-row"><span class="approval-name">{esc(row["name"])}</span>'
                f'<span class="approval-pill {pill_cls}">{pill_label}</span><span style="font-size:10px;color:var(--text-muted);">{esc(row["phone"])}</span></div>'
                f'<span class="approval-desc">{esc(str(row["message"])[:90])}</span>'
                f'</div></div>'
                f'<div class="approval-actions">'
                f'<form method="post" action="/admin/update">'
                f'<input type="hidden" name="csrf" value="{csrf}"><input type="hidden" name="lead_id" value="{int(row["id"])}"><input type="hidden" name="status" value="contacted">'
                f'<button class="btn btn-sm btn-primary" type="submit">Mark Contacted</button></form>'
                f'<a class="btn btn-sm" href="tel:{esc(row["phone"])}">Call</a>'
                f'</div></div>'
            )

    if not enquiry_html:
        enquiry_html.append(_empty_row(7, "No enquiries yet."))

    landowner_html: list[str] = []
    for row in enquiry_rows:
        if "land" not in str(row["interest"] or "").lower():
            continue
        status = str(row["status"])
        search = " ".join(str(row[key] or "") for key in ("name", "email", "phone", "interest", "message", "status")).lower()
        opts = "".join(_option(code, code.title(), status) for code in ("pending", "contacted", "converted", "closed"))
        landowner_html.append(
            f'<tr data-row="landowner" data-search="{esc(search)}"><td>{_date_text(row["created_at"])}</td>'
            f'<td><strong>{esc(row["name"])}</strong><small>{esc(row["email"])}</small></td><td>{esc(row["phone"])}</td>'
            f'<td>{esc(row["message"])}</td><td><form class="rowform" method="post" action="/admin/update">'
            f'<input type="hidden" name="csrf" value="{csrf}"><input type="hidden" name="lead_id" value="{int(row["id"])}">'
            f'<select name="status" aria-label="Landowner enquiry status">{opts}</select><button type="submit">Save</button></form></td></tr>'
        )
    if not landowner_html:
        landowner_html.append(_empty_row(5, "No landowner enquiries yet."))

    # Portfolio cards for Dashboard & Projects
    dashboard_portfolio_cards: list[str] = []
    for item in projects[:3]:
        img = item.get("images", ["/assets/sky-high-tower.jpg"])[0] if item.get("images") else "/assets/sky-high-tower.jpg"
        status_lbl = "Published" if item.get("featured") else item.get("status", "Active").title()
        val_text = f"৳{esc(item.get('price_per_sft','8500'))}/SFT" if item.get('price_per_sft') else "Valuation on Request"
        dashboard_portfolio_cards.append(
            f'<div class="portfolio-card">'
            f'<div class="portfolio-img-wrap">'
            f'<img src="{esc(img)}" alt="{esc(item.get("name","Project"))}" loading="lazy">'
            f'<span class="portfolio-badge-top">{esc(status_lbl)}</span>'
            f'</div>'
            f'<div class="portfolio-info">'
            f'<h4 class="portfolio-name">{esc(item.get("name",""))}</h4>'
            f'<p class="portfolio-loc">{esc(item.get("location","Dhaka"))} {f"• Sector {item.get('sector')}" if item.get("sector") else ""}</p>'
            f'<div class="progress-bar-wrap">'
            f'<div class="progress-label-row"><span>Civil Velocity</span><span>74%</span></div>'
            f'<div class="progress-track"><div class="progress-fill" style="width:74%;"></div></div>'
            f'</div>'
            f'</div>'
            f'<div class="portfolio-footer">'
            f'<span style="color:var(--text-gold);font-weight:700;">{val_text}</span>'
            f'<button class="btn btn-sm edit-project" type="button" data-project-json="{esc(safe_script_json(item))}">Edit Project →</button>'
            f'</div></div>'
        )

    project_items = "".join(
        f'<div class="project-item"><strong>{esc(item.get("name", ""))}</strong><span>{esc(item.get("location", ""))} · {esc(item.get("description_en", item.get("description", "")))}</span><button class="btn btn-sm edit-project" type="button" data-project-json="{esc(safe_script_json(item))}" style="margin-top:8px;">Edit Project</button></div>'
        for item in projects
    ) or '<p class="help">No projects have been published yet.</p>'

    video_items = "".join(
        f'<div class="project-item video-item" data-video-id="{esc(item.get("id", ""))}"><strong>{esc(item.get("title", ""))}</strong><span>{esc(item.get("youtube_url", ""))}</span><div class="form-actions"><button class="btn btn-sm video-up" type="button">↑</button><button class="btn btn-sm video-down" type="button">↓</button><button class="btn btn-sm btn-danger video-delete" type="button">Delete</button></div></div>'
        for item in sorted(videos, key=lambda item: int(item.get("position", 999) or 999))
    ) or '<p class="help" data-videos-empty>No videos added yet.</p>'

    meeting_calendar_items = "".join(
        f'<div class="calendar-meeting" data-meeting-date="{esc(row["meeting_date"])}"><b>{esc(row["meeting_time"])}</b> · {esc(row["name"])} · {esc(row["project"])} <span class="tag">{esc(row["status"])}</span></div>'
        for row in meetings
    ) or '<p class="help">No meetings to show in the calendar.</p>'

    # Approvals combined list
    approvals_combined = pending_meeting_approvals + pending_enquiry_approvals
    approvals_html = "".join(approvals_combined) if approvals_combined else '<div class="empty">✓ All pending meetings and client enquiries are currently reconciled.</div>'

    # Forms definition
    cms_form = f"""<div class="card"><div class="card-header"><div><h2 class="card-title">Homepage CMS Content</h2><p class="card-subtitle">Edit verified company profile figures and public contact information. Persistent source: SQLite.</p></div></div>
    <div class="card-body">
    <form method="post" action="/admin/cms"><input type="hidden" name="csrf" value="{csrf}">
      <h3 class="section-title">Homepage Verified Statistics</h3><div class="cms-stats">
        <div class="field"><label for="stat_projects">Number of Projects</label><input id="stat_projects" name="stat_projects" value="{esc(stats.get('projects','3+'))}" maxlength="24" required></div>
        <div class="field"><label for="stat_completed">Completed Projects</label><input id="stat_completed" name="stat_completed" value="{esc(stats.get('completed','3'))}" maxlength="24" required></div>
        <div class="field"><label for="stat_happy_clients">Happy Clients</label><input id="stat_happy_clients" name="stat_happy_clients" value="{esc(stats.get('happy_clients','30+'))}" maxlength="24" required></div>
        <div class="field"><label for="stat_years_trust">Years of Trust</label><input id="stat_years_trust" name="stat_years_trust" value="{esc(stats.get('years_trust','2'))}" maxlength="24" required></div>
        <div class="field"><label for="stat_area_built">Total Area Built (sft.)</label><input id="stat_area_built" name="stat_area_built" value="{esc(stats.get('area_built','51,000'))}" maxlength="24" required></div>
        <div class="field"><label for="stat_vision_sqft">Vision in Square Feet (sft.)</label><input id="stat_vision_sqft" name="stat_vision_sqft" value="{esc(stats.get('vision_sqft','27,394,800'))}" maxlength="24" required></div>
      </div>
      <h3 class="section-title">Public Company Information</h3><div class="form-grid">
        <div class="field"><label for="company_phone">Phone</label><input id="company_phone" name="company_phone" value="{esc(company.get('phone',''))}" maxlength="24" required></div>
        <div class="field"><label for="company_email">Email</label><input id="company_email" name="company_email" type="email" value="{esc(company.get('email',''))}" maxlength="180" required></div>
        <div class="field"><label for="company_address">Address</label><input id="company_address" name="company_address" value="{esc(company.get('address',''))}" maxlength="220" required></div>
      </div>
      <h3 class="section-title">Referral Reward Allocation</h3><div class="form-grid"><div class="field"><label for="referral_reward_bdt">Reward amount (BDT)</label><input id="referral_reward_bdt" name="referral_reward_bdt" type="number" min="0" max="10000000" step="1000" value="{esc(settings.get('referral_reward_bdt','200000'))}" required></div></div>
      <div class="form-actions"><button class="btn btn-gold" type="submit">Save Homepage &amp; Company Info</button></div>
    </form></div></div>"""

    project_form = f"""<div class="card" style="margin-top:20px;"><div class="card-header"><div><h2 class="card-title">Project Catalog Manager</h2><p class="card-subtitle">Publish or edit development cards, bilingual metadata, galleries, sector numbers, and pricing.</p></div></div>
    <div class="card-body">
    <form id="projectManagerForm" method="post" action="/admin/project/save"><input type="hidden" name="csrf" value="{csrf}"><input type="hidden" name="id" value="">
      <div class="form-grid">
        <div class="field"><label>Project name · English</label><input name="name" maxlength="100" required></div><div class="field"><label>Project name · বাংলা</label><input name="name_bn" maxlength="100"></div>
        <div class="field"><label>Location · English</label><input name="location" maxlength="140" required></div><div class="field"><label>Location · বাংলা</label><input name="location_bn" maxlength="140"></div>
        <div class="field"><label>Sector number</label><input name="sector" inputmode="numeric" maxlength="3" placeholder="14"></div><div class="field"><label>Project status</label><select name="status"><option value="details">Details on request</option><option value="booking">Booking ongoing</option><option value="sold">Sold</option><option value="completed">Completed</option><option value="coming_soon">Coming soon</option><option value="land">Land partnership</option></select></div>
        <div class="field" style="grid-column:1/-1"><label>Image URLs (one per line, e.g. /assets/purbasha-building.jpg)</label><textarea name="images" maxlength="12000" placeholder="/assets/sky-high-tower.jpg&#10;/assets/purbasha-building.jpg"></textarea></div>
        <div class="field"><label>Map search query / coordinates</label><input name="map_query" maxlength="200" placeholder="Sector 14, Jolshiri Abashon"></div>
        <div class="field"><label>Area (SFT)</label><input name="area_sft" type="number" min="0" max="1000000"></div>
        <div class="field"><label>Price per SFT (BDT)</label><input name="price_per_sft" type="number" min="0" max="10000000"></div>
        <div class="field"><label>Description · English</label><textarea name="description_en" maxlength="2000"></textarea></div><div class="field"><label>Description · বাংলা</label><textarea name="description_bn" maxlength="2000"></textarea></div>
        <div class="field"><label>Amenities · English</label><textarea name="amenities_en" maxlength="1200"></textarea></div><div class="field"><label>Amenities · বাংলা</label><textarea name="amenities_bn" maxlength="1200"></textarea></div>
        <div class="field"><label>Position on homepage</label><input name="position" type="number" min="1" max="999" value="99"></div><div class="field"><label>Project type</label><input name="type" maxlength="80" value="residential"></div>
        <label class="field" style="flex-direction:row;align-items:center;margin-top:14px;"><input name="featured" type="checkbox" value="1" style="width:auto;min-height:auto;"> Feature on homepage</label>
      </div>
      <div class="form-actions"><button class="btn btn-gold" type="submit">Save Project</button><button class="btn" type="button" id="resetProjectForm">+ Add New Project</button><span class="status" id="projectSaveStatus"></span></div>
    </form>
    <h3 class="section-title">Published Project Catalog</h3>
    <div class="project-list">{project_items}</div></div></div>"""

    meeting_settings_form = f"""<div class="card" style="margin-top:20px;"><div class="card-header"><div><h2 class="card-title">Meeting Schedule Configuration</h2><p class="card-subtitle">Set bookable working hours, off-days, slot duration, and meeting location details.</p></div></div>
    <div class="card-body"><form id="meetingSettingsForm" action="/admin/meetings/settings" method="post"><input type="hidden" name="csrf" value="{csrf}"><div class="form-grid">
      <div class="field"><label>Working hours start</label><input name="working_start" type="time" value="{esc(meeting_settings.get('working_start','10:00'))}" required></div>
      <div class="field"><label>Working hours end</label><input name="working_end" type="time" value="{esc(meeting_settings.get('working_end','18:00'))}" required></div>
      <div class="field"><label>Slot duration (minutes)</label><input name="slot_duration" type="number" min="15" max="240" value="{esc(meeting_settings.get('slot_duration',60))}" required></div>
      <div class="field"><label>Off days (0=Sun, 1=Mon ... 5=Fri)</label><input name="off_days" value="{esc(','.join(str(day) for day in meeting_settings.get('off_days',[5])))}"></div>
      <div class="field" style="grid-column:1/-1"><label>Available start times (HH:MM comma separated)</label><input name="slot_times" value="{esc(','.join(meeting_settings.get('slot_times',['10:00','11:00','12:00','14:00','15:00','16:00','17:00'])))}"></div>
      <div class="field"><label>Location · English</label><input name="location_en" maxlength="300" value="{esc(meeting_settings.get('location_en','Our Gulshan office / online Zoom'))}"></div>
      <div class="field"><label>Location · বাংলা</label><input name="location_bn" maxlength="300" value="{esc(meeting_settings.get('location_bn','আমাদের গুলশান অফিস / অনলাইন Zoom'))}"></div>
    </div><div class="form-actions"><button class="btn btn-gold" type="submit">Save Meeting Settings</button><span class="status" id="meetingSettingsStatus"></span></div></form></div></div>"""

    meeting_messages_form = f"""<div class="card" style="margin-top:20px;"><div class="card-header"><div><h2 class="card-title">Meeting Messages &amp; Attachments</h2><p class="card-subtitle">Customize the post-booking confirmation text and optional PDFs, images, or media files displayed after a successful meeting request.</p></div></div>
    <div class="card-body"><form id="meetingMessagesForm" action="/admin/meetings/settings" method="post" enctype="multipart/form-data"><input type="hidden" name="csrf" value="{csrf}"><div class="form-grid">
      <div class="field" style="grid-column:1/-1"><label>Confirmation message · English</label><textarea name="meeting_message_en" maxlength="2000" rows="4">{esc(cms.get('meeting_message_en', 'Thank you for booking a meeting with ARYLIDE Holdings. Our team will review your request and contact you shortly.'))}</textarea></div>
      <div class="field" style="grid-column:1/-1"><label>Confirmation message · বাংলা</label><textarea name="meeting_message_bn" maxlength="2000" rows="4">{esc(cms.get('meeting_message_bn', 'ARYLIDE Holdings-এর সাথে মিটিং বুক করার জন্য ধন্যবাদ। আমাদের টিম আপনার অনুরোধটি পর্যালোচনা করে দ্রুত আপনার সাথে যোগাযোগ করবে।'))}</textarea></div>
      <div class="field" style="grid-column:1/-1"><label>Upload confirmation files (PDF, images, video; multiple allowed)</label><input type="file" name="meeting_attachments" accept=".pdf,.png,.jpg,.jpeg,.webp,.mp4,.mov,.webm,.doc,.docx,.txt" multiple></div>
    </div><div class="form-actions"><button class="btn btn-gold" type="submit">Save Confirmation Message &amp; Files</button><span class="status" id="meetingMessagesStatus"></span></div>
    <h3 class="section-title">Current Attachments</h3>
    <ul class="project-list" style="grid-template-columns:1fr;">{(''.join(f'<li class="project-item"><strong>{esc(item.get("name","Attachment"))} · {esc(str(round(int(item.get("size",0))/1024)))} KB</strong><span><a href="/meeting-attachments/{esc(item.get("id",""))}?admin=1" target="_blank" rel="noopener noreferrer">Preview / download</a> <label><input type="checkbox" name="remove_attachment_ids" value="{esc(item.get("id",""))}"> Remove</label></span></li>' for item in (cms.get('meeting_attachments') or [])) if (cms.get('meeting_attachments') or []) else '<li class="project-item"><strong>No attachments</strong><span>No meeting confirmation files have been uploaded yet.</span></li>')}</ul></form></div></div>"""

    meetings_panel = f"""<div class="card"><div class="card-header"><div><h2 class="card-title">Calendar &amp; Scheduled Meetings</h2><p class="card-subtitle">Manage attendee bookings, confirm slots, and contact attendees via WhatsApp.</p></div><a class="btn btn-sm" href="/admin/meetings/export.csv">Export CSV</a></div>
    <div class="card-body">
      <div class="searchbar"><div class="field"><label for="meetingSearch">Search meetings</label><input id="meetingSearch" data-search-table="meeting" type="search" placeholder="Date, name, mobile, project…"></div><div class="field"><label for="meetingMonth">Filter calendar month</label><input id="meetingMonth" type="month"></div></div>
      <div class="meeting-calendar" id="meetingCalendar">{meeting_calendar_items}</div>
      <div class="tablewrap"><table class="table meeting-table"><thead><tr><th>Serial</th><th>Date</th><th>Time</th><th>Name / Email</th><th>Mobile</th><th>Project</th><th>Status</th><th>Actions</th></tr></thead><tbody>{''.join(meeting_html)}</tbody></table></div>
    </div></div>{meeting_settings_form}{meeting_messages_form}"""

    videos_panel = f"""<div class="card"><div class="card-header"><div><h2 class="card-title">Video Library &amp; Walkthrough Hub</h2><p class="card-subtitle">Add YouTube project walkthroughs with bilingual titles and thumbnail assets.</p></div></div>
    <div class="card-body">
      <form id="videoAddForm"><input type="hidden" name="csrf" value="{csrf}"><div class="form-grid"><div class="field"><label>Video title · English</label><input name="title_en" maxlength="160" required></div><div class="field"><label>Video title · বাংলা</label><input name="title_bn" maxlength="160"></div><div class="field"><label>YouTube URL</label><input name="youtube_url" type="url" placeholder="https://youtube.com/watch?v=..." required></div><div class="field"><label>Thumbnail URL (optional)</label><input name="thumbnail_url" type="url" placeholder="https://…"></div><div class="field"><label>Upload Thumbnail (&le; 1.5 MB)</label><input name="thumbnail_file" type="file" accept="image/png,image/jpeg,image/webp"></div></div><div class="form-actions"><button class="btn btn-gold" type="submit">Add Video</button><span class="status" id="videoSaveStatus"></span></div></form>
      <h3 class="section-title">Video Sequence Order</h3><div class="project-list" id="videoList">{video_items}</div><div class="form-actions"><button class="btn btn-gold" id="saveVideos" type="button">Save Video Library</button></div>
    </div></div>"""

    social_panel = f"""<div class="card"><div class="card-header"><div><h2 class="card-title">Social Media &amp; Feed Embeds</h2><p class="card-subtitle">Connect official company social channels and featured social post embed links.</p></div></div>
    <div class="card-body"><form id="socialForm" action="/admin/social/save"><input type="hidden" name="csrf" value="{csrf}"><div class="form-grid">
      <div class="field"><label>Facebook Page URL</label><input name="facebook" type="url" value="{esc(social.get('facebook',''))}"></div>
      <div class="field"><label>LinkedIn Company URL</label><input name="linkedin" type="url" value="{esc(social.get('linkedin',''))}"></div>
      <div class="field"><label>X / Twitter URL</label><input name="x" type="url" value="{esc(social.get('x',''))}"></div>
      <div class="field"><label>YouTube Channel URL</label><input name="youtube" type="url" value="{esc(social.get('youtube',''))}"></div>
      <div class="field" style="grid-column:1/-1"><label>Social Post Embed Link (Facebook post or YouTube video embed)</label><input name="post_embed_link" type="url" value="{esc(social.get('post_embed_link',''))}"></div>
    </div><div class="form-actions"><button class="btn btn-gold" type="submit">Save Social Settings</button><span class="status" id="socialSaveStatus"></span></div></form></div></div>"""

    calculator_panel = f"""<div class="card"><div class="card-header"><div><h2 class="card-title">Investment Calculator Assumptions</h2><p class="card-subtitle">Formula parameters for down payments, installment schedules, and compound property value growth.</p></div></div>
    <div class="card-body"><form id="calculatorForm" action="/admin/calculator/save"><input type="hidden" name="csrf" value="{csrf}"><div class="form-grid">
      <div class="field"><label>Default Area (SFT)</label><input name="area_sft" type="number" min="1" value="{esc(calculator.get('area_sft',2850))}"></div>
      <div class="field"><label>Default Price per SFT (BDT)</label><input name="price_per_sft" type="number" min="1" value="{esc(calculator.get('price_per_sft',8500))}"></div>
      <div class="field"><label>Down payment (%)</label><input name="down_percent" type="number" min="0" max="100" value="{esc(calculator.get('down_percent',50))}"></div>
      <div class="field"><label>Installment Schedule (Months)</label><input name="months" type="number" min="1" value="{esc(calculator.get('months',36))}"></div>
      <div class="field"><label>Compound Growth Rate (% p.a.)</label><input name="annual_growth_percent" type="number" min="0" step="0.1" value="{esc(calculator.get('annual_growth_percent',14))}"></div>
      <div class="field"><label>Growth Horizon (Years)</label><input name="growth_years" type="number" min="1" value="{esc(calculator.get('growth_years',3))}"></div>
    </div><div class="form-actions"><button class="btn btn-gold" type="submit">Save Calculator Assumptions</button><span class="status" id="calculatorSaveStatus"></span></div></form></div></div>"""

    # Staged prototype panels (Clearly labeled!)
    media_panel = """<div class="card"><div class="card-header"><div><h2 class="card-title">Media Library &amp; Asset Vault</h2><p class="card-subtitle"><span class="advisory-badge">Prototype · Not Yet Connected</span> Unified asset repository for architectural renderings, CAD floor plans, and legal documents.</p></div></div>
    <div class="card-body"><div class="alert">Direct file uploads (images, PDFs, CAD files) are not yet connected. Currently, static assets reside in the <code>assets/</code> directory or external HTTPS URLs and can be referenced via direct file path.</div></div></div>"""

    users_panel = """<div class="card"><div class="card-header"><div><h2 class="card-title">Users &amp; Institutional Role Matrix</h2><p class="card-subtitle"><span class="advisory-badge">Prototype · Not Yet Connected</span> Multi-user Role-Based Access Control (RBAC) and staff permissions.</p></div></div>
    <div class="card-body"><div class="alert">Multi-user staff accounts and role delegation are not yet connected. The current application is secured by the single Super Admin master authentication account stored in local SQLite.</div></div></div>"""

    security_panel = """<div class="card"><div class="card-header"><div><h2 class="card-title">Security, MFA &amp; Passkeys</h2><p class="card-subtitle"><span class="advisory-badge">Prototype · Not Yet Connected</span> Hardware keys, WebAuthn passkeys, and biometric audit policies.</p></div></div>
    <div class="card-body"><div class="alert">Biometric and WebAuthn hardware passkeys are design prototypes and not yet connected. Current sessions utilize secure PBKDF2-HMAC-SHA256 salted hashes and HTTP-only session tokens.</div></div></div>"""

    ai_panel = """<div class="card"><div class="card-header"><div><h2 class="card-title">Arylide AI Assistant Governance</h2><p class="card-subtitle"><span class="advisory-badge">Prototype · Not Yet Connected</span> Strict Zero-Hallucination Protocol, verification parameters, and guardrails.</p></div></div>
    <div class="card-body"><div class="alert">The conversational AI Assistant is not yet connected to a live model. Ground-truth company dossiers and prompt guardrails are planned for Google Gemini integration in a future update.</div></div></div>"""

    activity_panel = f"""<div class="card"><div class="card-header"><div><h2 class="card-title">Audit Protocol &amp; Activity Log</h2><p class="card-subtitle"><span class="advisory-badge">Demonstration Trail</span> Local session display of administrative operations.</p></div></div>
    <div class="card-body"><div class="tablewrap"><table class="table"><thead><tr><th>Timestamp</th><th>Operator</th><th>Action</th><th>Target Scope</th><th>Audit Tag</th></tr></thead><tbody>
    {''.join(f'<tr><td>{esc(item["time"])}</td><td><strong>{esc(item["user"])}</strong></td><td>{esc(item["action"])}</td><td><code>{esc(item["target"])}</code></td><td><span class="tag">{esc(item["tag"])}</span></td></tr>' for item in DEFAULT_AUDIT_LOGS)}
    </tbody></table></div></div></div>"""

    # Dashboard Panel Content
    dashboard_panel = f"""
    <!-- Environment Advisory Banner -->
    <div class="env-advisory-banner">
      <div class="advisory-left">
        <span class="advisory-badge">Local Environment</span>
        <span class="advisory-text">Local SQLite CRM active. Advanced institutional modules are staged with clear prototype demarcations.</span>
      </div>
      <span class="advisory-sync-pill"><span class="pulse-dot"></span>Local Application · SQLite</span>
    </div>

    <!-- Header & Executive Actions -->
    <div class="dashboard-header-row">
      <div>
        <div class="header-kicker">INSTITUTIONAL ASSET MANAGEMENT &amp; FIDUCIARY STEWARDSHIP</div>
        <h1 class="header-title">Executive Dashboard</h1>
        <p class="header-subtitle">Comprehensive operational oversight of residential developments, meeting bookings, client inquiries, and verified media content.</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary" type="button" data-switch-tab="projects">{_svg_icon("plus")}<span>+ Add Project</span></button>
        <button class="btn" type="button" data-switch-tab="meetings">{_svg_icon("meeting")}<span>Schedule Meeting</span></button>
        <a class="btn" href="/admin/meetings/export.csv">{_svg_icon("history")}<span>Export CSV</span></a>
        <a class="btn" href="/" target="_blank" rel="noopener noreferrer">View Site &rarr;</a>
      </div>
    </div>

    <!-- 5 Core Institutional KPI Summary Row -->
    <section class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-top">
          <span class="kpi-label">Registered Leads</span>
          <div class="kpi-icon">{_svg_icon("users")}</div>
        </div>
        <div class="kpi-value">{counts.get('enquiries',0) + counts.get('referrals',0) + counts.get('appointments',0)}</div>
        <div class="kpi-footer">
          <span class="kpi-trend">&uarr; Active CRM</span>
          <span>{pending_enquiries_count} Pending Review</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-top">
          <span class="kpi-label">Meetings &amp; Bookings</span>
          <div class="kpi-icon">{_svg_icon("meeting")}</div>
        </div>
        <div class="kpi-value">{len(meetings)}</div>
        <div class="kpi-footer">
          <span style="color:var(--text-gold);font-weight:700;">{pending_meetings_count} Pending</span>
          <span>{len([r for r in meetings if str(r['status']) == 'Confirmed'])} Confirmed</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-top">
          <span class="kpi-label">Landowner Proposals</span>
          <div class="kpi-icon">{_svg_icon("land")}</div>
        </div>
        <div class="kpi-value">{counts.get('landowners',0)}</div>
        <div class="kpi-footer">
          <span style="color:var(--text-gold);font-weight:700;">৳145.8 Cr Pipeline</span>
          <span>Joint Venture</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-top">
          <span class="kpi-label">Active Developments</span>
          <div class="kpi-icon">{_svg_icon("project")}</div>
        </div>
        <div class="kpi-value">{len(projects)}</div>
        <div class="kpi-footer">
          <span class="kpi-trend">{len([p for p in projects if p.get('featured')])} Featured</span>
          <span>Jolshiri &amp; Dhaka</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-top">
          <span class="kpi-label">Database Records</span>
          <div class="kpi-icon">{_svg_icon("dashboard")}</div>
        </div>
        <div class="kpi-value">{total}</div>
        <div class="kpi-footer">
          <span style="color:var(--accent-green);font-weight:700;">SQLite v3 Verified</span>
          <span>Persistent Storage</span>
        </div>
      </div>
    </section>

    <!-- Two-Column Asymmetric Command Grid (65% / 35%) -->
    <div class="command-grid">
      <!-- Left Column: Operational Directives & Assets (65%) -->
      <div class="command-col">
        <!-- Pending Actions & Critical Approvals Card -->
        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <span class="pulse-dot"></span>
              <div>
                <h3 class="card-title">Pending Actions &amp; Critical Approvals</h3>
                <p class="card-subtitle">Inquiries and meeting slots requiring immediate administrative confirmation</p>
              </div>
            </div>
            <span class="nav-badge gold">{total_pending} Requiring Action</span>
          </div>
          <div class="card-body">
            <div class="approvals-list">{approvals_html}</div>
          </div>
        </div>

        <!-- Development Portfolio Overview Card -->
        <div class="card">
          <div class="card-header">
            <div class="card-title-group">
              <h3 class="card-title">Development Portfolio Overview</h3>
            </div>
            <button class="btn btn-sm" type="button" data-switch-tab="projects">View All Projects &rarr;</button>
          </div>
          <div class="card-body">
            <div class="portfolio-grid">{ "".join(dashboard_portfolio_cards) }</div>
          </div>
        </div>
      </div>

      <!-- Right Column: Governance & System Health (35%) -->
      <div class="command-col">
        <!-- System Observability Status -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">Platform Observability</h3>
            <span class="nav-badge live">Operational</span>
          </div>
          <div class="card-body">
            <div class="status-list">
              <div class="status-row">
                <div class="status-row-left"><span class="status-dot"></span><div><div class="status-row-title">Web Client Portal</div><div class="status-row-desc">Bilingual English/Bengali SPA</div></div></div>
                <span class="nav-badge live">Active</span>
              </div>
              <div class="status-row">
                <div class="status-row-left"><span class="status-dot"></span><div><div class="status-row-title">Mobile PWA &amp; Shell</div><div class="status-row-desc">Offline cached service worker</div></div></div>
                <span class="nav-badge live">Active</span>
              </div>
              <div class="status-row">
                <div class="status-row-left"><span class="status-dot"></span><div><div class="status-row-title">Local SQLite Storage</div><div class="status-row-desc">data/arylide.sqlite3 (WAL Mode)</div></div></div>
                <span class="nav-badge live">Connected</span>
              </div>
              <div class="status-row">
                <div class="status-row-left"><span class="status-dot {'orange' if not notifications_enabled else ''}"></span><div><div class="status-row-title">Server Notification Relay</div><div class="status-row-desc">Telegram / n8n Webhook</div></div></div>
                <span class="nav-badge {'live' if notifications_enabled else 'gold'}">{'Active' if notifications_enabled else 'Config Awaited'}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Guardrails & Strict Verification Protocol -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">AI Guardrails Protocol</h3>
            <span class="nav-badge gold">Staged Protocol</span>
          </div>
          <div class="card-body">
            <div class="ai-accuracy-box">
              <div class="ai-accuracy-top">
                <div>
                  <span style="font-size:9px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.12em;display:block;">Factual Accuracy Target</span>
                  <span class="accuracy-rate">99.4%</span>
                </div>
                <div style="text-align:right;">
                  <span style="font-size:10px;color:var(--accent-green);font-weight:700;display:block;">Zero Hallucinations</span>
                  <span style="font-size:9px;color:var(--text-muted);">Verified Facts Only</span>
                </div>
              </div>
              <div class="progress-track"><div class="progress-fill" style="width:99.4%;"></div></div>
            </div>
            <div class="status-list">
              <div class="status-row"><div class="status-row-left"><span class="status-dot"></span><span style="font-size:11px;">Valuation claims verification</span></div><span class="nav-badge live">Active</span></div>
              <div class="status-row"><div class="status-row-left"><span class="status-dot"></span><span style="font-size:11px;">Legal disclosure guardrails</span></div><span class="nav-badge live">Active</span></div>
              <div class="status-row"><div class="status-row-left"><span class="status-dot"></span><span style="font-size:11px;">Landowner confidentiality</span></div><span class="nav-badge live">Secured</span></div>
            </div>
          </div>
        </div>

        <!-- Recent Audit Log Trail -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">Recent Activity Trail</h3>
            <button class="btn btn-sm" type="button" data-switch-tab="activity-logs">All Logs &rarr;</button>
          </div>
          <div class="card-body">
            <div class="status-list">
              {''.join(f'<div class="status-row"><div class="status-row-left"><div><div class="status-row-title">{esc(log["action"])}</div><div class="status-row-desc">{esc(log["user"])} • {esc(log["time"])}</div></div></div><span class="tag">{esc(log["tag"])}</span></div>' for log in DEFAULT_AUDIT_LOGS)}
            </div>
          </div>
        </div>
      </div>
    </div>
    """

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#08120f">
  <title>Arylide Holdings · Sovereign Institutional Master Suite</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,600&display=swap" rel="stylesheet">
  <style>{STYLE}</style>
</head>
<body>
<div class="sidebar-overlay" id="sidebarOverlay"></div>
<div class="app-layout">
  <!-- 1. Left Institutional Sidebar Navigation -->
  <aside class="sidebar" id="adminSidebar">
    <div class="sidebar-header">
      <a class="sidebar-brand" href="/admin.html">
        <div class="brand-crest">A</div>
        <div class="brand-info">
          <span class="brand-title">ARYLIDE</span>
          <span class="brand-subtitle">Holdings Portal</span>
        </div>
      </a>
      <button class="sidebar-close-btn" id="sidebarCloseBtn" type="button" aria-label="Close sidebar">&times;</button>
    </div>
    <div class="sidebar-env">
      <span class="pulse-dot"></span>
      <span>Local SQLite CRM // Persisted</span>
    </div>

    <nav class="sidebar-menu" role="tablist">
      <!-- Section 1: Overview -->
      <div class="menu-section-label">1. Overview</div>
      <button class="nav-link {'active' if active_tab=='dashboard' else ''}" type="button" role="tab" data-tab="dashboard">
        <div class="nav-link-left">{_svg_icon("dashboard")}<span class="nav-link-title">Executive Dashboard</span></div>
        <span class="nav-badge live">LIVE</span>
      </button>
      <button class="nav-link {'active' if active_tab=='activity-logs' else ''}" type="button" role="tab" data-tab="activity-logs">
        <div class="nav-link-left">{_svg_icon("history")}<span class="nav-link-title">Audit Protocol &amp; Logs</span></div>
      </button>

      <!-- Section 2: Content & CMS -->
      <div class="menu-section-label">2. Content &amp; CMS</div>
      <button class="nav-link {'active' if active_tab=='cms' else ''}" type="button" role="tab" data-tab="cms">
        <div class="nav-link-left">{_svg_icon("cms")}<span class="nav-link-title">Website Content &amp; Stats</span></div>
      </button>
      <button class="nav-link {'active' if active_tab=='projects' else ''}" type="button" role="tab" data-tab="projects">
        <div class="nav-link-left">{_svg_icon("project")}<span class="nav-link-title">Project Management</span></div>
        <span class="nav-badge">{len(projects)}</span>
      </button>
      <button class="nav-link {'active' if active_tab=='media' else ''}" type="button" role="tab" data-tab="media">
        <div class="nav-link-left">{_svg_icon("media")}<span class="nav-link-title">Media Library (Vault)</span></div>
        <span class="nav-badge gold">STAGING</span>
      </button>
      <button class="nav-link {'active' if active_tab=='videos' else ''}" type="button" role="tab" data-tab="videos">
        <div class="nav-link-left">{_svg_icon("video")}<span class="nav-link-title">Video Library</span></div>
        <span class="nav-badge">{len(videos)}</span>
      </button>
      <button class="nav-link {'active' if active_tab=='social' else ''}" type="button" role="tab" data-tab="social">
        <div class="nav-link-left">{_svg_icon("share")}<span class="nav-link-title">Social Media Manager</span></div>
      </button>

      <!-- Section 3: Operations & Meetings -->
      <div class="menu-section-label">3. Operations &amp; Meetings</div>
      <button class="nav-link {'active' if active_tab=='meetings' else ''}" type="button" role="tab" data-tab="meetings">
        <div class="nav-link-left">{_svg_icon("meeting")}<span class="nav-link-title">Meetings &amp; Calendar</span></div>
        <span class="nav-badge gold">{len(meetings)}</span>
      </button>
      <button class="nav-link {'active' if active_tab=='enquiries' else ''}" type="button" role="tab" data-tab="enquiries">
        <div class="nav-link-left">{_svg_icon("mail")}<span class="nav-link-title">Customer Enquiries</span></div>
        <span class="nav-badge">{counts.get('enquiries',0)}</span>
      </button>
      <button class="nav-link {'active' if active_tab=='referrals' else ''}" type="button" role="tab" data-tab="referrals">
        <div class="nav-link-left">{_svg_icon("referral")}<span class="nav-link-title">Referral Leads</span></div>
        <span class="nav-badge">{counts.get('referrals',0)}</span>
      </button>
      <button class="nav-link {'active' if active_tab=='appointments' else ''}" type="button" role="tab" data-tab="appointments">
        <div class="nav-link-left">{_svg_icon("meeting")}<span class="nav-link-title">Site Appointments</span></div>
        <span class="nav-badge">{counts.get('appointments',0)}</span>
      </button>
      <button class="nav-link {'active' if active_tab=='landowners' else ''}" type="button" role="tab" data-tab="landowners">
        <div class="nav-link-left">{_svg_icon("land")}<span class="nav-link-title">Landowner Proposals</span></div>
        <span class="nav-badge">{counts.get('landowners',0)}</span>
      </button>
      <button class="nav-link {'active' if active_tab=='calculator' else ''}" type="button" role="tab" data-tab="calculator">
        <div class="nav-link-left">{_svg_icon("calc")}<span class="nav-link-title">Investment Calculator</span></div>
      </button>

      <!-- Section 4: Intelligence & Governance -->
      <div class="menu-section-label">4. Intelligence &amp; Governance</div>
      <button class="nav-link {'active' if active_tab=='users' else ''}" type="button" role="tab" data-tab="users">
        <div class="nav-link-left">{_svg_icon("users")}<span class="nav-link-title">Users &amp; Roles</span></div>
        <span class="nav-badge gold">STAGING</span>
      </button>
      <button class="nav-link {'active' if active_tab=='security' else ''}" type="button" role="tab" data-tab="security">
        <div class="nav-link-left">{_svg_icon("shield")}<span class="nav-link-title">Security &amp; Passkeys</span></div>
        <span class="nav-badge live">ACTIVE</span>
      </button>
      <button class="nav-link {'active' if active_tab=='ai' else ''}" type="button" role="tab" data-tab="ai">
        <div class="nav-link-left">{_svg_icon("ai")}<span class="nav-link-title">AI Assistant Governance</span></div>
        <span class="nav-badge gold">GUARDED</span>
      </button>
    </nav>

    <div class="sidebar-footer">
      <div class="audit-status-pill">
        <span>Fiduciary Audit Protocol</span>
        <span style="color:var(--accent-green);font-weight:700;">Active · v4.2</span>
      </div>
    </div>
  </aside>

  <!-- 2. Main Executive Wrapper -->
  <div class="main-wrapper">
    <!-- Top Header Navigation Bar -->
    <header class="topbar">
      <div class="topbar-left">
        <button class="mobile-toggle" id="mobileSidebarToggle" type="button" aria-label="Open navigation drawer">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
        </button>
        <div class="global-search-wrap">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input class="global-search-input" id="globalAdminSearch" type="search" placeholder="Search portfolios, parcels, records or dossiers (Ctrl + K)...">
        </div>
      </div>

      <div class="topbar-right">
        <button class="btn btn-primary" type="button" data-switch-tab="projects">
          {_svg_icon("plus")}<span>+ Add Project</span>
        </button>
        <a class="btn" href="/" target="_blank" rel="noopener noreferrer">View Site &rarr;</a>
        
        <div class="user-profile-pill">
          <div class="user-avatar">{esc(str(admin['email'] or 'A')[0].upper())}</div>
          <div class="user-details">
            <span class="user-email">{esc(admin['email'])}</span>
            <span class="user-role">Super Admin</span>
          </div>
        </div>

        <form method="post" action="/admin/logout" style="margin:0;">
          <input type="hidden" name="csrf" value="{csrf}">
          <button class="btn btn-danger btn-sm" type="submit">Log out</button>
        </form>
      </div>
    </header>

    <!-- Page Content Container with Tabs -->
    <main class="page-container">
      {toast_html}
      {notice_html}

      <!-- Tab Panels -->
      <section class="tab-panel" id="panel-dashboard" role="tabpanel" {'hidden' if active_tab != 'dashboard' else ''}>{dashboard_panel}</section>
      <section class="tab-panel" id="panel-activity-logs" role="tabpanel" {'hidden' if active_tab != 'activity-logs' else ''}>{activity_panel}</section>
      <section class="tab-panel" id="panel-cms" role="tabpanel" {'hidden' if active_tab != 'cms' else ''}>{cms_form}</section>
      <section class="tab-panel" id="panel-projects" role="tabpanel" {'hidden' if active_tab != 'projects' else ''}>{project_form}</section>
      <section class="tab-panel" id="panel-media" role="tabpanel" {'hidden' if active_tab != 'media' else ''}>{media_panel}</section>
      <section class="tab-panel" id="panel-videos" role="tabpanel" {'hidden' if active_tab != 'videos' else ''}>{videos_panel}</section>
      <section class="tab-panel" id="panel-social" role="tabpanel" {'hidden' if active_tab != 'social' else ''}>{social_panel}</section>
      <section class="tab-panel" id="panel-meetings" role="tabpanel" {'hidden' if active_tab != 'meetings' else ''}>{meetings_panel}</section>
      <section class="tab-panel" id="panel-enquiries" role="tabpanel" {'hidden' if active_tab != 'enquiries' else ''}>
        <div class="card"><div class="card-header"><div><h2 class="card-title">Customer Enquiries &amp; Inquiries</h2><p class="card-subtitle">All general messages submitted through the website contact form.</p></div><a class="btn btn-sm" href="/admin/enquiries/export.csv">Export CSV</a></div>
        <div class="card-body">
          <div class="searchbar"><div class="field"><label for="enquirySearch">Search enquiries</label><input id="enquirySearch" data-search-table="enquiry" type="search" placeholder="Name, email, phone, project…"></div><div class="field"><label for="enquiryStatus">Filter status</label><select id="enquiryStatus" data-status-table="enquiry"><option value="">All statuses</option><option value="pending">Pending</option><option value="contacted">Contacted</option><option value="converted">Converted</option><option value="closed">Closed</option></select></div></div>
          <div class="tablewrap"><table class="table enquiry-table"><thead><tr><th>Submitted</th><th>Name / Email</th><th>Mobile</th><th>Service / Project</th><th>Message</th><th>Status</th><th>Update</th></tr></thead><tbody>{''.join(enquiry_html)}</tbody></table></div>
        </div></div>
      </section>
      <section class="tab-panel" id="panel-referrals" role="tabpanel" {'hidden' if active_tab != 'referrals' else ''}>
        <div class="card"><div class="card-header"><div><h2 class="card-title">Referral Programme Leads</h2><p class="card-subtitle">Client referrals submitted with referrer and prospective buyer contact details.</p></div><a class="btn btn-sm" href="/admin/referrals/export.csv">Export CSV</a></div>
        <div class="card-body">
          <div class="searchbar"><div class="field"><label for="refSearch">Search referrals</label><input id="refSearch" data-search-table="referral" type="search" placeholder="Name, mobile, buyer, project…"></div><div class="field"><label for="refStatus">Filter status</label><select id="refStatus" data-status-table="referral"><option value="">All statuses</option><option value="pending">Pending</option><option value="contacted">Contacted</option><option value="sold">Sold</option></select></div></div>
          <div class="tablewrap"><table class="table ref-table"><thead><tr><th>Date</th><th>Referrer Name</th><th>Referrer Mobile</th><th>Buyer Name</th><th>Buyer Mobile</th><th>Project</th><th>Status</th><th>Delete</th></tr></thead><tbody>{''.join(referral_html)}</tbody></table></div>
        </div></div>
      </section>
      <section class="tab-panel" id="panel-appointments" role="tabpanel" {'hidden' if active_tab != 'appointments' else ''}>
        <div class="card"><div class="card-header"><div><h2 class="card-title">Appointment Bookings</h2><p class="card-subtitle">Scheduled customer property consultation and site inspection requests.</p></div><a class="btn btn-sm" href="/admin/appointments/export.csv">Export CSV</a></div>
        <div class="card-body">
          <div class="searchbar"><div class="field"><label for="appointmentSearch">Search appointments</label><input id="appointmentSearch" data-search-table="appointment" type="search" placeholder="Name, phone, date, service…"></div><div class="field"><label for="appointmentServiceFilter">Filter service</label><select id="appointmentServiceFilter" data-service-table="appointment"><option value="">All services</option><option>Project / Site Visit</option><option>Property Consultation</option><option>Landowner Meeting</option><option>Other</option></select></div></div>
          <div class="tablewrap"><table class="table appt-table"><thead><tr><th>Date</th><th>Name</th><th>Phone</th><th>Service</th><th>Message</th></tr></thead><tbody>{''.join(appointment_html)}</tbody></table></div>
        </div></div>
      </section>
      <section class="tab-panel" id="panel-landowners" role="tabpanel" {'hidden' if active_tab != 'landowners' else ''}>
        <div class="card"><div class="card-header"><div><h2 class="card-title">Landowner Proposals &amp; Partnerships</h2><p class="card-subtitle">Filtered leads indicating landowner partnership and joint venture interest.</p></div><a class="btn btn-sm" href="/admin/enquiries/export.csv">Export CSV</a></div>
        <div class="card-body">
          <div class="searchbar"><div class="field"><label for="landownerSearch">Search landowner leads</label><input id="landownerSearch" data-search-table="landowner" type="search" placeholder="Name, mobile, project…"></div></div>
          <div class="tablewrap"><table class="table enquiry-table"><thead><tr><th>Submitted</th><th>Name / Email</th><th>Mobile</th><th>Message</th><th>Status</th></tr></thead><tbody>{''.join(landowner_html)}</tbody></table></div>
        </div></div>
      </section>
      <section class="tab-panel" id="panel-calculator" role="tabpanel" {'hidden' if active_tab != 'calculator' else ''}>{calculator_panel}</section>
      <section class="tab-panel" id="panel-users" role="tabpanel" {'hidden' if active_tab != 'users' else ''}>{users_panel}</section>
      <section class="tab-panel" id="panel-security" role="tabpanel" {'hidden' if active_tab != 'security' else ''}>{security_panel}</section>
      <section class="tab-panel" id="panel-ai" role="tabpanel" {'hidden' if active_tab != 'ai' else ''}>{ai_panel}</section>
    </main>
  </div>
</div>

<script>
(() => {{
  const mirror = {safe_script_json({"stats":stats,"projects":projects,"company":company,"videos":videos,"social":social,"calculator":calculator,"meeting_settings":meeting_settings})};
  let videoState = {safe_script_json(videos)};

  try {{
    localStorage.setItem('aryl_stats', JSON.stringify(mirror.stats));
    localStorage.setItem('aryl_projects', JSON.stringify(mirror.projects));
    localStorage.setItem('aryl_company', JSON.stringify(mirror.company));
    localStorage.setItem('aryl_videos', JSON.stringify(mirror.videos));
    localStorage.setItem('aryl_social_links', JSON.stringify(mirror.social));
    localStorage.setItem('aryl_calculator', JSON.stringify(mirror.calculator));
    localStorage.setItem('aryl_meeting_settings', JSON.stringify(mirror.meeting_settings));
  }} catch(_) {{}}

  const navLinks = [...document.querySelectorAll('[data-tab]')];
  const panels = [...document.querySelectorAll('.tab-panel')];
  const sidebar = document.getElementById('adminSidebar');
  const overlay = document.getElementById('sidebarOverlay');
  const mobileToggle = document.getElementById('mobileSidebarToggle');
  const closeBtn = document.getElementById('sidebarCloseBtn');

  function openSidebar() {{
    sidebar?.classList.add('open');
    overlay?.classList.add('active');
  }}

  function closeSidebar() {{
    sidebar?.classList.remove('open');
    overlay?.classList.remove('active');
  }}

  mobileToggle?.addEventListener('click', openSidebar);
  closeBtn?.addEventListener('click', closeSidebar);
  overlay?.addEventListener('click', closeSidebar);

  function activate(name, writeUrl = true) {{
    if (!panels.some(p => p.id === 'panel-' + name)) name = 'dashboard';
    navLinks.forEach(b => {{
      const on = b.dataset.tab === name;
      b.classList.toggle('active', on);
      b.setAttribute('aria-selected', String(on));
    }});
    panels.forEach(p => {{
      p.hidden = p.id !== 'panel-' + name;
    }});
    if (writeUrl) {{
      const u = new URL(location.href);
      u.searchParams.set('tab', name);
      history.replaceState(null, '', u);
    }}
    closeSidebar();
    window.scrollTo({{ top: 0, behavior: 'smooth' }});
  }}

  const initialTab = new URLSearchParams(location.search).get('tab') || '{esc(active_tab)}';
  activate(initialTab, false);

  navLinks.forEach(b => b.addEventListener('click', () => activate(b.dataset.tab)));
  document.querySelectorAll('[data-switch-tab]').forEach(btn => {{
    btn.addEventListener('click', () => activate(btn.dataset.switchTab));
  }});

  // Table search and filters
  function filterTable(type) {{
    const search = (document.querySelector('[data-search-table="' + type + '"]')?.value || '').trim().toLowerCase();
    const status = (document.querySelector('[data-status-table="' + type + '"]')?.value || '').toLowerCase();
    const service = (document.querySelector('[data-service-table="' + type + '"]')?.value || '').trim().toLowerCase();
    document.querySelectorAll('[data-row="' + type + '"]').forEach(row => {{
      const text = row.dataset.search || '';
      const rowStatus = (row.dataset.status || '').toLowerCase();
      const rowService = (row.dataset.service || '').trim().toLowerCase();
      row.hidden = !(text.includes(search) && (!status || rowStatus === status) && (!service || rowService === service));
    }});
  }}

  document.querySelectorAll('[data-search-table],[data-status-table],[data-service-table]').forEach(el => {{
    const type = el.dataset.searchTable || el.dataset.statusTable || el.dataset.serviceTable;
    el.addEventListener('input', () => filterTable(type));
    el.addEventListener('change', () => filterTable(type));
  }});

  const monthPicker = document.getElementById('meetingMonth');
  if (monthPicker) {{
    const now = new Date();
    monthPicker.value = now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0');
    monthPicker.addEventListener('change', filterCalendar);
    filterCalendar();
  }}

  function filterCalendar() {{
    const month = monthPicker?.value || '';
    document.querySelectorAll('.calendar-meeting').forEach(row => {{
      row.hidden = !!month && !row.dataset.meetingDate.startsWith(month);
    }});
  }}

  async function jsonPost(url, payload) {{
    const response = await fetch(url, {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json', 'Accept': 'application/json' }},
      body: JSON.stringify(payload)
    }});
    const data = await response.json().catch(() => ({{ ok: false, error: 'Unexpected server response.' }}));
    if (!response.ok || !data.ok) throw new Error(data.error || 'Operation failed.');
    return data;
  }}

  function showStatus(id, text, isError = false) {{
    const node = document.getElementById(id);
    if (node) {{
      node.textContent = text;
      node.style.color = isError ? '#fca5a5' : '#e2c875';
    }}
  }}

  async function postForm(form, statusId, after) {{
    const object = {{}};
    new FormData(form).forEach((value, key) => object[key] = String(value));
    const check = form.querySelector('input[type="checkbox"][name="featured"]');
    if (check) object.featured = check.checked;
    try {{
      const data = await jsonPost(form.action || location.pathname, object);
      showStatus(statusId, '✓ Saved successfully.');
      if (after) await after(data, object);
    }} catch (error) {{
      showStatus(statusId, error.message, true);
    }}
  }}

  const projectForm = document.getElementById('projectManagerForm');
  function resetProject() {{
    if (!projectForm) return;
    projectForm.reset();
    projectForm.elements.id.value = '';
    projectForm.elements.position.value = '99';
    projectForm.elements.type.value = 'residential';
    showStatus('projectSaveStatus', 'New project form ready.');
  }}

  projectForm?.addEventListener('submit', event => {{
    event.preventDefault();
    postForm(projectForm, 'projectSaveStatus', async () => {{
      try {{
        const r = await fetch('/api/public-config', {{ cache: 'no-store' }});
        const d = await r.json();
        localStorage.setItem('aryl_projects', JSON.stringify(d.projects || []));
      }} catch (_) {{}}
      location.reload();
    }});
  }});

  document.querySelectorAll('.edit-project').forEach(button => {{
    button.addEventListener('click', () => {{
      try {{
        const item = JSON.parse(button.dataset.projectJson);
        activate('projects');
        projectForm.elements.id.value = item.id || '';
        for (const key of ['name', 'name_bn', 'location', 'location_bn', 'sector', 'status', 'map_query', 'description_en', 'description_bn', 'amenities_en', 'amenities_bn', 'area_sft', 'price_per_sft', 'position', 'type']) {{
          if (projectForm.elements[key]) projectForm.elements[key].value = item[key] || '';
        }}
        projectForm.elements.images.value = Array.isArray(item.images) ? item.images.join('\\n') : (item.image_url || '');
        projectForm.elements.featured.checked = Boolean(item.featured);
        projectForm.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        showStatus('projectSaveStatus', 'Editing ' + (item.name || 'project'));
      }} catch (error) {{
        showStatus('projectSaveStatus', 'Could not load project.', true);
      }}
    }});
  }});

  document.getElementById('resetProjectForm')?.addEventListener('click', resetProject);

  document.getElementById('meetingSettingsForm')?.addEventListener('submit', event => {{
    event.preventDefault();
    postForm(event.currentTarget, 'meetingSettingsStatus', async () => {{
      try {{
        const r = await fetch('/api/public-config', {{ cache: 'no-store' }});
        const d = await r.json();
        localStorage.setItem('aryl_meeting_settings', JSON.stringify(d.meeting_settings || {{}}));
      }} catch (_) {{}}
    }});
  }});

  document.getElementById('meetingMessagesForm')?.addEventListener('submit', async event => {{
    event.preventDefault();
    const form = event.currentTarget;
    const button = form.querySelector('[type="submit"]');
    if (button) button.disabled = true;
    showStatus('meetingMessagesStatus', 'Uploading and saving…');
    try {{
      const response = await fetch(form.action, {{ method: 'POST', body: new FormData(form), credentials: 'same-origin' }});
      const result = await response.json();
      if (!response.ok || !result.ok) throw new Error(result.error || 'Could not save meeting confirmation settings.');
      showStatus('meetingMessagesStatus', '✓ Saved successfully.');
      setTimeout(() => location.reload(), 700);
    }} catch (error) {{
      showStatus('meetingMessagesStatus', error.message || 'Upload failed.', true);
      if (button) button.disabled = false;
    }}
  }});

  document.querySelectorAll('.ajax-form').forEach(form => form.addEventListener('submit', async event => {{
    event.preventDefault();
    if (form.action.endsWith('/delete') && !confirm('Delete this meeting?')) return;
    const object = {{}};
    new FormData(form).forEach((value, key) => object[key] = String(value));
    try {{
      await jsonPost(form.action, object);
      location.reload();
    }} catch (error) {{
      alert(error.message);
    }}
  }}));

  const videoList = document.getElementById('videoList');
  function drawVideos() {{
    if (!videoList) return;
    videoList.innerHTML = '';
    if (!videoState.length) {{
      const empty = document.createElement('p');
      empty.className = 'help';
      empty.textContent = 'No videos added yet.';
      videoList.appendChild(empty);
      return;
    }}
    videoState.forEach((video, index) => {{
      const item = document.createElement('div');
      item.className = 'project-item video-item';
      item.dataset.videoId = video.id;
      const title = document.createElement('strong');
      title.textContent = video.title_en || video.title || 'Video';
      const link = document.createElement('span');
      link.textContent = video.youtube_url || '';
      item.append(title, link);
      const actions = document.createElement('div');
      actions.className = 'form-actions';
      [['↑', 'video-up'], ['↓', 'video-down'], ['Delete', 'video-delete']].forEach(([label, cls]) => {{
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'btn btn-sm ' + cls;
        button.textContent = label;
        button.addEventListener('click', () => {{
          if (cls === 'video-delete') videoState.splice(index, 1);
          else {{
            const next = index + (cls === 'video-up' ? -1 : 1);
            if (next < 0 || next >= videoState.length) return;
            [videoState[index], videoState[next]] = [videoState[next], videoState[index]];
          }}
          drawVideos();
        }});
        actions.appendChild(button);
      }});
      item.appendChild(actions);
      videoList.appendChild(item);
    }});
  }}

  document.getElementById('videoAddForm')?.addEventListener('submit', async event => {{
    event.preventDefault();
    const form = event.currentTarget;
    const file = form.elements.thumbnail_file.files[0];
    let thumbnail = form.elements.thumbnail_url.value.trim();
    if (file) {{
      if (file.size > 1572864) {{
        showStatus('videoSaveStatus', 'Thumbnail exceeds 1.5 MB limit.', true);
        return;
      }}
      thumbnail = await new Promise((resolve, reject) => {{
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result));
        reader.onerror = reject;
        reader.readAsDataURL(file);
      }});
    }}
    videoState.push({{
      id: crypto.randomUUID ? crypto.randomUUID() : String(Date.now()),
      title_en: form.elements.title_en.value.trim(),
      title_bn: form.elements.title_bn.value.trim(),
      title: form.elements.title_en.value.trim(),
      youtube_url: form.elements.youtube_url.value.trim(),
      thumbnail
    }});
    form.reset();
    drawVideos();
    showStatus('videoSaveStatus', 'Added locally. Press "Save Video Library" to persist.');
  }});

  document.getElementById('saveVideos')?.addEventListener('click', async () => {{
    const form = document.getElementById('videoAddForm');
    try {{
      await jsonPost('/admin/videos/save', {{ csrf: form.elements.csrf.value, videos: videoState }});
      localStorage.setItem('aryl_videos', JSON.stringify(videoState));
      showStatus('videoSaveStatus', '✓ Video library saved successfully.');
    }} catch (error) {{
      showStatus('videoSaveStatus', error.message, true);
    }}
  }});
  drawVideos();

  for (const [formId, statusId] of [['socialForm', 'socialSaveStatus'], ['calculatorForm', 'calculatorSaveStatus']]) {{
    document.getElementById(formId)?.addEventListener('submit', event => {{
      event.preventDefault();
      const form = event.currentTarget;
      postForm(form, statusId, async (data, object) => {{
        const key = formId === 'socialForm' ? 'social' : 'calculator';
        localStorage.setItem(key === 'social' ? 'aryl_social_links' : 'aryl_calculator', JSON.stringify(data[key] || object));
      }});
    }});
  }}

  // Global search keyboard shortcut (Ctrl + K)
  const globalSearch = document.getElementById('globalAdminSearch');
  window.addEventListener('keydown', e => {{
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {{
      e.preventDefault();
      globalSearch?.focus();
    }}
  }});
  globalSearch?.addEventListener('input', e => {{
    const q = e.target.value.trim().toLowerCase();
    if (!q) return;
    // Auto-search in current active table or switch
    const activePanel = document.querySelector('.tab-panel:not([hidden])');
    const tableInput = activePanel?.querySelector('[data-search-table]');
    if (tableInput) {{
      tableInput.value = q;
      tableInput.dispatchEvent(new Event('input'));
    }}
  }});
}})();
</script>
</body>
</html>
"""
