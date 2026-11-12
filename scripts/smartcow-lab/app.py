#!/usr/bin/env python3
"""smartcow-lab - replika backend IoT & Firebase untuk Target Node PBL TEK1314 Kelompok 12.

Meniru alur data dan otentikasi proyek SmartCow:
- Device cow-sprinkler-01: telemetry, log, control, status, dan events.
- Firebase Auth & Access RBAC: login, session, user management, dan permissions.
"""
import hashlib
import json
import math
import os
import re
import secrets
import threading
import time
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

BASE = "/devices/cow-sprinkler-01"

TOKEN = os.environ.get("SMARTCOW_TOKEN", "")
BIND = os.environ.get("SMARTCOW_BIND", "127.0.0.1")
PORT = int(os.environ.get("SMARTCOW_PORT", "9000"))
VALIDATE = os.environ.get("SMARTCOW_VALIDATE", "0") == "1"
LOG_PATH = os.environ.get("SMARTCOW_LOG", "")
DATA_DIR = os.environ.get("SMARTCOW_DATA", "/home/smartcow-lab/data").rstrip("/") or "/"
STATE_PATH = os.path.join(DATA_DIR, "state.json")
USERS_PATH = os.path.join(DATA_DIR, "users.json")
EVENTS_PATH = os.path.join(DATA_DIR, "events.json")
HISTORY_PATH = os.path.join(DATA_DIR, "history.json")

# Rentang sensor mengikuti domain SmartCow
TEMP_RANGE = (-20.0, 70.0)
HUM_RANGE = (0.0, 100.0)
THI_RANGE = (0.0, 130.0)
REQUIRED_TELEMETRY = ("t1", "t2", "t3", "t4", "t5", "t6", "h1", "h2", "h3", "h4")
ALLOWED_TELEMETRY = REQUIRED_TELEMETRY + (
    "avg", "thi", "validCount", "validMask", "humidityValidCount", "humidityValidMask",
    "measuredTs", "ts", "leftOnline", "controlPolicyVersion", "ssr",
    "d1", "d2", "d3", "d4", "temperatureAgeMs", "humidityAgeMs", "leftAgeMs", "n"
)
ALLOWED_CONTROL = (
    "controlPolicyVersion", "controlBasis", "mode", "manualSsr", "tempThreshold", "thiThreshold",
    "tempHysteresis", "thiHysteresis", "tempMaxDuration", "thiMaxDuration", "tempCooldown",
    "thiCooldown", "tempAutoSrc", "thiAutoSrc", "tempSchN", "thiSchN", "updatedBy", "updatedAt",
    "threshold", "hysteresis", "maxDuration", "cooldown", "autoSrc", "schN", "schOn", "profiles"
)

_lock = threading.Lock()


def now_iso():
    return (datetime.now(timezone.utc) + timedelta(hours=7)).strftime("%Y-%m-%dT%H:%M:%S+07:00")


def now_ms():
    return int(time.time() * 1000)


def log_event(kind, detail):
    if not LOG_PATH:
        return
    line = "%s %s %s\n" % (now_iso(), kind, detail)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError:
        pass


def hash_password(password, salt=None):
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return hashed, salt


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
    os.replace(tmp, path)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def load_state():
    state = load_json(STATE_PATH, {})
    if "control" not in state:
        state["control"] = {
            "controlPolicyVersion": 2,
            "controlBasis": "temperature",
            "mode": "auto",
            "manualSsr": "off",
            "tempThreshold": 28.5,
            "thiThreshold": 72.0,
            "tempHysteresis": 1.0,
            "thiHysteresis": 1.5,
            "tempMaxDuration": 180,
            "thiMaxDuration": 180,
            "tempCooldown": 300,
            "thiCooldown": 300,
            "tempAutoSrc": "threshold",
            "thiAutoSrc": "threshold",
            "tempSchN": 0,
            "thiSchN": 0,
            "updatedAt": now_ms(),
            "updatedBy": "system-init"
        }
    return state


def init_dummy_data():
    now = now_ms()
    # 1. Events
    events = load_json(EVENTS_PATH, [])
    if not isinstance(events, list) or len(events) < 5:
        events = [
            {"type": "system", "reason": "Sistem monitoring SmartCow aktif. 6 sensor suhu DS18B20 & 4 sensor DHT22 online.", "ts": now - 7200000},
            {"type": "sprinkler", "reason": "Suhu rata-rata kandang 30.8°C melebihi ambang batas 29.5°C. Sprinkler otomatis AKTIF.", "ts": now - 5400000},
            {"type": "sprinkler", "reason": "Suhu turun ke 27.6°C. Siklus pendinginan selesai, sprinkler otomatis MATI.", "ts": now - 4800000},
            {"type": "thi", "reason": "Indeks THI kandang 80.4 (kategori waspada stres sapi). Siklus semprot interval 60 detik dijalankan.", "ts": now - 3600000},
            {"type": "audit", "reason": "Pengujian konektivitas ICMP dan protokol IoT diverifikasi oleh Purple Team.", "ts": now - 1800000},
            {"type": "sprinkler", "reason": "Sprinkler otomatis aktif: suhu rata-rata mencapai 30.5°C.", "ts": now - 600000},
            {"type": "manual", "reason": "Pemeriksaan manual aktuator solenoid sprinkler oleh admin.", "ts": now - 120000}
        ]
        save_json(EVENTS_PATH, events)

    # 2. History
    history = load_json(HISTORY_PATH, [])
    if not isinstance(history, list) or len(history) < 30:
        history = []
        base_time = now - (60 * 10000)
        for i in range(60):
            pt_ts = base_time + (i * 10000)
            t_base = 29.8 + (1.2 * math.sin(i / 10.0))
            h_base = 68.0 - (4.0 * math.sin(i / 10.0))
            is_ssr = 1 if t_base > 30.2 else 0
            history.append({
                "avg": round(t_base, 2),
                "controlPolicyVersion": 2,
                "h1": round(h_base + 1.2, 1),
                "h2": round(h_base - 0.8, 1),
                "h3": round(h_base + 0.5, 1),
                "h4": round(h_base - 1.1, 1),
                "humidityValidCount": 4,
                "humidityValidMask": 15,
                "leftOnline": True,
                "measuredTs": pt_ts,
                "ssr": is_ssr,
                "t1": round(t_base + 0.4, 2),
                "t2": round(t_base - 0.3, 2),
                "t3": round(t_base - 0.5, 2),
                "t4": round(t_base + 0.2, 2),
                "t5": round(t_base + 0.1, 2),
                "t6": round(t_base + 0.1, 2),
                "ts": pt_ts,
                "validCount": 6,
                "validMask": 63
            })
        save_json(HISTORY_PATH, history)


def save_state(state):
    save_json(STATE_PATH, state)


def load_users():
    data = load_json(USERS_PATH, {})
    if "users" not in data or "admin_kel12" not in data.get("users", {}):
        # Inisialisasi default admin tunggal
        # Kata sandi admin awal tidak ditulis di kode. Diambil dari environment,
        # atau dibangkitkan acak dan dicatat pada berkas rahasia mode 600.
        seed_pw = os.environ.get("SMARTCOW_ADMIN_PASSWORD")
        if not seed_pw:
            seed_pw = secrets.token_urlsafe(12)
            seed_path = os.path.join(os.path.dirname(DATA_DIR), "secrets", "admin_password")
            try:
                os.makedirs(os.path.dirname(seed_path), exist_ok=True)
                with open(seed_path, "w") as fh:
                    fh.write(seed_pw + "\n")
                os.chmod(seed_path, 0o600)
            except OSError as exc:
                print("PERINGATAN: gagal menyimpan admin_password: %s" % exc)
        pw_hash, salt = hash_password(seed_pw)
        data = {
            "users": {
                "admin_kel12": {
                    "uid": "admin_kel12",
                    "email": "kelompok12@gmail.com",
                    "name": "Kelompok 12 Admin",
                    "password_hash": pw_hash,
                    "salt": salt,
                    "role": "admin",
                    "enabled": True,
                    "permissions": {
                        "monitor": True,
                        "settings": True,
                        "operate": True
                    },
                    "createdAt": now_ms(),
                    "updatedAt": now_ms()
                }
            },
            "sessions": {}
        }
        save_json(USERS_PATH, data)
    return data


def save_users(data):
    save_json(USERS_PATH, data)


def get_session_user(token):
    if not token:
        return None
    with _lock:
        data = load_users()
        sessions = data.get("sessions", {})
        session = sessions.get(token)
        if not session:
            return None
        if session.get("expiresAt", 0) < now_ms():
            del sessions[token]
            save_users(data)
            return None
        uid = session.get("uid")
        user = data.get("users", {}).get(uid)
        if not user or not user.get("enabled"):
            return None
        return user


def secret_ok(query):
    # Fail-closed: tanpa SMARTCOW_TOKEN tidak ada jalur otentikasi token statis.
    if not TOKEN:
        return False
    supplied = query.get("auth", [""])[0]
    header = query.get("__header__", [""])[0]
    if supplied and supplied == TOKEN:
        return True
    if header:
        raw = header.split(" ", 1)
        if len(raw) == 2 and raw[0].lower() == "bearer" and raw[1] == TOKEN:
            return True
    return False


def validate_telemetry(payload):
    if not isinstance(payload, dict):
        return "payload harus objek JSON"
    missing = [f for f in REQUIRED_TELEMETRY if f not in payload]
    if missing:
        return "field wajib kurang: %s" % ", ".join(missing)
    extra = [f for f in payload if f not in ALLOWED_TELEMETRY]
    if extra:
        return "field tidak dikenal: %s" % ", ".join(sorted(extra))
    for field in ("t1", "t2", "t3", "t4", "t5", "t6", "avg"):
        if field in payload:
            val = payload[field]
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                return "%s harus angka" % field
            if not (TEMP_RANGE[0] <= float(val) <= TEMP_RANGE[1]):
                return "%s di luar rentang %s..%s" % (field, TEMP_RANGE[0], TEMP_RANGE[1])
    for field in ("h1", "h2", "h3", "h4", "humidityAvg"):
        if field in payload:
            val = payload[field]
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                return "%s harus angka" % field
            if not (HUM_RANGE[0] <= float(val) <= HUM_RANGE[1]):
                return "%s di luar rentang %s..%s" % (field, HUM_RANGE[0], HUM_RANGE[1])
    if "thi" in payload:
        val = payload["thi"]
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            return "thi harus angka"
        if not (THI_RANGE[0] <= float(val) <= THI_RANGE[1]):
            return "thi di luar rentang %s..%s" % (THI_RANGE[0], THI_RANGE[1])
    return None


def validate_control(payload):
    if not isinstance(payload, dict):
        return "payload harus objek JSON"
    extra = [f for f in payload if f not in ALLOWED_CONTROL]
    if extra:
        return "field tidak dikenal: %s" % ", ".join(sorted(extra))
    if "mode" in payload and payload["mode"] not in ("auto", "manual"):
        return "mode harus auto atau manual"
    if "manualSsr" in payload and payload["manualSsr"] not in ("on", "off"):
        return "manualSsr harus on atau off"
    for field in ("tempThreshold", "thiThreshold", "threshold"):
        if field in payload:
            val = payload[field]
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                return "%s harus angka" % field
            if not (-20.0 <= float(val) <= 90.0):
                return "%s di luar rentang" % field
    return None


class Handler(BaseHTTPRequestHandler):
    server_version = "SmartCowLab"
    sys_version = ""

    def address_string(self):
        return self.client_address[0]

    def log_message(self, fmt, *args):
        line = fmt % args
        line = re.sub(r"auth=[^&\s\"]+", "auth=REDACTED", line)
        log_event("http", "%s %s" % (self.address_string(), line))

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, PATCH, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _json(self, code, body):
        raw = json.dumps(body, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self._cors_headers()
        self.end_headers()
        self.wfile.write(raw)

    def _read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return None, "body kosong"
        raw = self.rfile.read(length)
        try:
            body = json.loads(raw.decode("utf-8"))
        except ValueError as exc:
            return None, "JSON tidak valid: %s" % exc
        if not isinstance(body, dict):
            return None, "body harus objek JSON"
        return body, None

    def _route(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        header = self.headers.get("Authorization", "")
        query["__header__"] = [header]

        # Normalisasi path: hapus akhiran .json jika ada
        raw_path = parsed.path.rstrip("/")
        clean_path = re.sub(r"\.json$", "", raw_path)
        return clean_path, query

    def _get_bearer(self, query):
        header = query.get("__header__", [""])[0]
        if header.lower().startswith("bearer "):
            return header[7:].strip()
        auth_param = query.get("auth", [""])[0]
        if auth_param and auth_param != TOKEN:
            return auth_param
        return None

    def _check_auth(self, query, required_perm=None):
        # 1. Hardening token (simulator, attack script, backend curl)
        if secret_ok(query):
            return True, {"role": "admin", "permissions": {"monitor": True, "settings": True, "operate": True}}

        # 2. Web session token
        bearer = self._get_bearer(query)
        if bearer:
            user = get_session_user(bearer)
            if user:
                if user.get("role") == "admin":
                    return True, user
                if not required_perm:
                    return True, user
                perms = user.get("permissions", {})
                if perms.get(required_perm):
                    return True, user
        return False, None

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def do_GET(self):
        path, query = self._route()

        # Health & info
        if path in ("/health", "/api/health"):
            self._json(200, {"status": "ok", "service": "smartcow-lab", "bind": BIND, "validate": VALIDATE})
            return

        # Auth Session Check
        if path == "/api/auth/session":
            bearer = self._get_bearer(query)
            user = get_session_user(bearer)
            if not user:
                self._json(401, {"error": "Unauthorized", "detail": "Sesi tidak ditemukan atau kedaluwarsa"})
                return
            safe_user = {k: v for k, v in user.items() if k not in ("password_hash", "salt")}
            self._json(200, {"user": safe_user})
            return

        # Users directory for Admin
        if path == "/api/access":
            ok, user = self._check_auth(query, "admin")
            if not ok or user.get("role") != "admin":
                self._json(403, {"error": "Forbidden", "detail": "Hanya admin yang dapat mengelola akun"})
                return
            with _lock:
                data = load_users()
                users = list(data.get("users", {}).values())
                safe_users = [{k: v for k, v in u.items() if k not in ("password_hash", "salt")} for u in users]
            self._json(200, safe_users)
            return

        # Events list
        if path == "/api/events":
            ok, _ = self._check_auth(query, "monitor")
            if not ok:
                self._json(401, {"error": "Unauthorized"})
                return
            with _lock:
                events = load_json(EVENTS_PATH, [])
            self._json(200, events[-50:] if isinstance(events, list) else [])
            return

        # Telemetry Log History
        if path == "/api/telemetry/log":
            ok, _ = self._check_auth(query, "monitor")
            if not ok:
                self._json(401, {"error": "Unauthorized"})
                return
            with _lock:
                history = load_json(HISTORY_PATH, [])
            self._json(200, history[-120:] if isinstance(history, list) else [])
            return

        # Device endpoints (support both /devices/... and /api/devices/...)
        dev_path = path
        if dev_path.startswith("/api/devices/"):
            dev_path = dev_path[4:]

        if dev_path.startswith(BASE):
            sub = dev_path[len(BASE):]
            if sub in ("/telemetry/latest", "/control", "/status"):
                ok, _ = self._check_auth(query, "monitor")
                if not ok:
                    self._json(401, {"error": "Permission denied", "detail": "token tidak valid atau tidak ada"})
                    return
                state = load_state()
                if sub == "/telemetry/latest":
                    self._json(200, state.get("telemetry", {}).get("latest", {}))
                elif sub == "/control":
                    self._json(200, state.get("control", {}))
                else:
                    self._json(200, state.get("status", {}))
                return

        self._json(404, {"error": "not found", "path": path})

    def do_POST(self):
        path, query = self._route()
        payload, err = self._read_body()
        if err:
            self._json(400, {"error": "bad request", "detail": err})
            return

        # Login
        if path == "/api/auth/login":
            email = (payload.get("email") or "").strip().lower()
            password = payload.get("password") or ""
            with _lock:
                data = load_users()
                users = data.get("users", {})
                matched = None
                for u in users.values():
                    if u.get("email", "").lower() == email:
                        matched = u
                        break
                if not matched:
                    self._json(401, {"error": "Email atau password salah."})
                    return
                pw_hash, _ = hash_password(password, matched.get("salt", ""))
                if pw_hash != matched.get("password_hash"):
                    self._json(401, {"error": "Email atau password salah."})
                    return
                if not matched.get("enabled"):
                    self._json(403, {"error": "Akun ini telah dinonaktifkan."})
                    return
                token = secrets.token_hex(24)
                data.setdefault("sessions", {})[token] = {
                    "uid": matched["uid"],
                    "expiresAt": now_ms() + (24 * 3600 * 1000)
                }
                save_users(data)
            safe_user = {k: v for k, v in matched.items() if k not in ("password_hash", "salt")}
            log_event("login", "user=%s role=%s" % (email, matched.get("role")))
            self._json(200, {"token": token, "uid": matched["uid"], "email": email, "user": safe_user})
            return

        # Logout
        if path == "/api/auth/logout":
            bearer = self._get_bearer(query)
            if bearer:
                with _lock:
                    data = load_users()
                    if bearer in data.get("sessions", {}):
                        del data["sessions"][bearer]
                        save_users(data)
            self._json(200, {"ok": True})
            return

        # Create user (Admin only)
        if path == "/api/access":
            ok, user = self._check_auth(query, "admin")
            if not ok or user.get("role") != "admin":
                self._json(403, {"error": "Forbidden", "detail": "Hanya admin yang dapat membuat akun"})
                return
            email = (payload.get("email") or "").strip().lower()
            password = payload.get("password") or ""
            if not email or len(password) < 8:
                self._json(400, {"error": "Email valid dan password minimal 8 karakter diperlukan"})
                return
            with _lock:
                data = load_users()
                users = data.setdefault("users", {})
                for u in users.values():
                    if u.get("email", "").lower() == email:
                        self._json(400, {"error": "Email sudah terdaftar."})
                        return
                new_uid = "user_" + secrets.token_hex(8)
                pw_hash, salt = hash_password(password)
                role = "admin" if payload.get("role") == "admin" else "user"
                admin_flag = role == "admin"
                users[new_uid] = {
                    "uid": new_uid,
                    "email": email,
                    "name": payload.get("name", "").strip(),
                    "password_hash": pw_hash,
                    "salt": salt,
                    "role": role,
                    "enabled": bool(payload.get("enabled", True)),
                    "permissions": {
                        "monitor": admin_flag or bool(payload.get("monitor")),
                        "settings": admin_flag or bool(payload.get("settings")),
                        "operate": admin_flag or bool(payload.get("operate"))
                    },
                    "createdAt": now_ms(),
                    "updatedAt": now_ms()
                }
                save_users(data)
            log_event("create_user", "uid=%s email=%s role=%s" % (new_uid, email, role))
            self._json(200, {"uid": new_uid, "ok": True})
            return

        # Create event
        if path == "/api/events":
            ok, _ = self._check_auth(query, "operate")
            if not ok:
                self._json(401, {"error": "Unauthorized"})
                return
            with _lock:
                events = load_json(EVENTS_PATH, [])
                if not isinstance(events, list):
                    events = []
                event_entry = {
                    "type": payload.get("type", "web"),
                    "reason": str(payload.get("reason", "")).strip()[:500],
                    "ts": payload.get("ts") or now_ms()
                }
                events.append(event_entry)
                if len(events) > 100:
                    events = events[-100:]
                save_json(EVENTS_PATH, events)
            self._json(200, {"ok": True})
            return

        self._json(404, {"error": "not found", "path": path})

    def do_PUT(self):
        path, query = self._route()
        dev_path = path[4:] if path.startswith("/api/devices/") else path

        # Device endpoints
        if dev_path.startswith(BASE):
            sub = dev_path[len(BASE):]

            # Telemetry PUT (simulator / attack)
            if sub == "/telemetry/latest":
                ok, _ = self._check_auth(query, "operate")
                if not ok:
                    self._json(401, {"error": "Permission denied", "detail": "tulis butuh token valid"})
                    return
                payload, err = self._read_body()
                if err:
                    self._json(400, {"error": "bad request", "detail": err})
                    return
                problem = validate_telemetry(payload) if VALIDATE else None
                if problem:
                    log_event("rejected", "telemetry ditolak: %s" % problem)
                    self._json(400, {"error": "invalid payload", "detail": problem})
                    return

                ts_val = payload.get("ts")
                if not isinstance(ts_val, (int, float)):
                    ts_val = now_ms()
                payload["ts"] = ts_val
                if "measuredTs" not in payload:
                    payload["measuredTs"] = ts_val

                with _lock:
                    state = load_state()
                    state.setdefault("telemetry", {})["latest"] = payload
                    save_state(state)

                    # Update history
                    history = load_json(HISTORY_PATH, [])
                    if not isinstance(history, list):
                        history = []
                    history.append(payload)
                    if len(history) > 300:
                        history = history[-300:]
                    save_json(HISTORY_PATH, history)

                log_event("write", "telemetry ditulis")
                self._json(200, {"ok": True, "path": path})
                return

            # Control PUT (web UI / manual override)
            if sub == "/control":
                ok, _ = self._check_auth(query, "operate")
                if not ok:
                    self._json(401, {"error": "Permission denied", "detail": "tulis butuh token valid"})
                    return
                payload, err = self._read_body()
                if err:
                    self._json(400, {"error": "bad request", "detail": err})
                    return
                problem = validate_control(payload) if VALIDATE else None
                if problem:
                    log_event("rejected", "control ditolak: %s" % problem)
                    self._json(400, {"error": "invalid payload", "detail": problem})
                    return

                with _lock:
                    state = load_state()
                    ctrl = state.setdefault("control", {})
                    ctrl.update(payload)
                    ctrl["updatedAt"] = now_ms()
                    save_state(state)

                    # Simulasikan respon SSR pada telemetry
                    if "manualSsr" in payload:
                        ssr_val = 1 if payload["manualSsr"] == "on" else 0
                        state.setdefault("telemetry", {}).setdefault("latest", {})["ssr"] = ssr_val
                        save_state(state)

                log_event("write", "control ditulis: %s" % payload)
                self._json(200, {"ok": True, "path": path})
                return

        # User Access Update (Admin only): PUT /api/access/<uid>
        if path.startswith("/api/access/"):
            ok, user = self._check_auth(query, "admin")
            if not ok or user.get("role") != "admin":
                self._json(403, {"error": "Forbidden"})
                return
            target_uid = path[len("/api/access/"):]
            payload, err = self._read_body()
            if err:
                self._json(400, {"error": "bad request", "detail": err})
                return
            with _lock:
                data = load_users()
                users = data.get("users", {})
                if target_uid not in users:
                    self._json(404, {"error": "User tidak ditemukan"})
                    return
                rec = users[target_uid]
                if "name" in payload:
                    rec["name"] = str(payload["name"]).strip()
                if "enabled" in payload:
                    rec["enabled"] = bool(payload["enabled"])
                if "permissions" in payload and isinstance(payload["permissions"], dict):
                    rec["permissions"] = {
                        "monitor": bool(payload["permissions"].get("monitor")),
                        "settings": bool(payload["permissions"].get("settings")),
                        "operate": bool(payload["permissions"].get("operate"))
                    }
                rec["updatedAt"] = now_ms()
                save_users(data)
            log_event("update_user", "uid=%s" % target_uid)
            self._json(200, {"ok": True})
            return

        self._json(404, {"error": "not found", "path": path})

    def do_DELETE(self):
        path, query = self._route()
        if path.startswith("/api/access/"):
            ok, user = self._check_auth(query, "admin")
            if not ok or user.get("role") != "admin":
                self._json(403, {"error": "Forbidden"})
                return
            target_uid = path[len("/api/access/"):]
            if target_uid == user.get("uid"):
                self._json(400, {"error": "Tidak dapat menghapus akun admin sendiri."})
                return
            with _lock:
                data = load_users()
                users = data.get("users", {})
                if target_uid in users:
                    del users[target_uid]
                    # Hapus session aktif user tersebut
                    sessions = data.get("sessions", {})
                    to_del = [tok for tok, s in sessions.items() if s.get("uid") == target_uid]
                    for tok in to_del:
                        del sessions[tok]
                    save_users(data)
            log_event("delete_user", "uid=%s" % target_uid)
            self._json(200, {"ok": True})
            return
        self._json(404, {"error": "not found", "path": path})

    def do_PATCH(self):
        path, query = self._route()
        dev_path = path[4:] if path.startswith("/api/devices/") else path
        if not dev_path.startswith(BASE) or not dev_path.endswith("/telemetry/latest"):
            self._json(404, {"error": "not found", "path": path})
            return
        ok, _ = self._check_auth(query, "operate")
        if not ok:
            self._json(401, {"error": "Permission denied"})
            return
        payload, err = self._read_body()
        if err:
            self._json(400, {"error": "bad request", "detail": err})
            return
        problem = validate_telemetry(payload) if VALIDATE else None
        if problem:
            log_event("rejected", "telemetry ditolak: %s" % problem)
            self._json(400, {"error": "invalid payload", "detail": problem})
            return
        with _lock:
            state = load_state()
            latest = state.setdefault("telemetry", {}).setdefault("latest", {})
            latest.update(payload)
            latest["ts"] = now_ms()
            save_state(state)
        log_event("write", "telemetry dipatch")
        self._json(200, {"ok": True, "path": path})


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    load_users()
    load_state()
    init_dummy_data()
    log_event("start", "smartcow-lab bind=%s port=%d validate=%s" % (BIND, PORT, VALIDATE))
    server = ThreadingHTTPServer((BIND, PORT), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
