#!/usr/bin/env python3
"""smartcow-lab - replika backend IoT untuk Target Node PBL TEK1314 Kelompok 12.

Meniru alur data proyek SmartCow (Firebase Realtime Database) pada device
cow-sprinkler-01: telemetry, log, control, status, dan events.

Token API dibaca dari environment SMARTCOW_TOKEN. Setelah hardening, token
tidak lagi ada di dalam berkas ini; nilainya diambil dari berkas .env yang
hanya bisa dibaca akun aplikasi.
"""
import json
import os
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

BASE = "/devices/cow-sprinkler-01"

# Token fallback. Hardening tahap C2 menghapus literal ini.

TOKEN = os.environ.get("SMARTCOW_TOKEN", "")
BIND = os.environ.get("SMARTCOW_BIND", "0.0.0.0")
PORT = int(os.environ.get("SMARTCOW_PORT", "9000"))
VALIDATE = os.environ.get("SMARTCOW_VALIDATE", "0") == "1"
LOG_PATH = os.environ.get("SMARTCOW_LOG", "")
DATA_DIR = os.environ.get("SMARTCOW_DATA", "/home/smartcow-lab/data")
STATE_PATH = os.path.join(DATA_DIR, "state.json")

# Rentang sensor mengikuti domain SmartCow.
TEMP_RANGE = (-20.0, 70.0)
HUM_RANGE = (0.0, 100.0)
THI_RANGE = (0.0, 130.0)
REQUIRED_TELEMETRY = ("t1", "t2", "t3", "t4", "t5", "t6", "h1", "h2", "h3", "h4")
ALLOWED_TELEMETRY = REQUIRED_TELEMETRY + ("avg", "thi", "validCount", "validMask", "measuredTs", "ts")
ALLOWED_CONTROL = (
    "controlPolicyVersion", "controlBasis", "mode", "manualSsr", "tempThreshold", "thiThreshold",
    "tempHysteresis", "thiHysteresis", "tempMaxDuration", "thiMaxDuration", "tempCooldown",
    "thiCooldown", "tempAutoSrc", "thiAutoSrc", "tempSchN", "thiSchN", "updatedBy",
)

_lock = threading.Lock()


def now_iso():
    return (datetime.now(timezone.utc) + timedelta(hours=7)).strftime("%Y-%m-%dT%H:%M:%S+07:00")


def log_event(kind, detail):
    if not LOG_PATH:
        return
    line = "%s %s %s\n" % (now_iso(), kind, detail)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError:
        pass


def load_state():
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def save_state(state):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)
    os.replace(tmp, STATE_PATH)
    os.chmod(STATE_PATH, 0o600)


def secret_ok(query):
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
    for field in ("tempThreshold", "thiThreshold"):
        if field in payload:
            val = payload[field]
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                return "%s harus angka" % field
            if not (-20.0 <= float(val) <= 90.0):
                return "%s di luar rentang" % field
    return None


DASHBOARD_HTML = """<!doctype html>
<html lang="id"><head><meta charset="utf-8"><title>SmartCow Lab - Kandang A</title>
<style>body{font-family:system-ui,sans-serif;background:#0f1720;color:#e2e8f0;margin:0;padding:24px}
h1{font-size:20px;margin:0 0 4px}.sub{color:#94a3b8;font-size:13px;margin-bottom:18px}
table{border-collapse:collapse;width:100%;max-width:760px;background:#16202b;border-radius:8px;overflow:hidden}
th,td{padding:8px 12px;border-bottom:1px solid #22303f;font-size:13px;text-align:left}
th{background:#1d2937;color:#9fb3c8;font-weight:600}tr:last-child td{border-bottom:none}
code{background:#0b1219;padding:1px 5px;border-radius:4px;color:#7dd3fc}</style></head>
<body>
<h1>SmartCow Lab - replika backend Target Node</h1>
<div class="sub">Device cow-sprinkler-01 &middot; data simulasi &middot; bukan data operasional</div>
<table id="t"><thead><tr><th>Kolom</th><th>Nilai</th></tr></thead><tbody>
<tr><td>telemetry</td><td id="tel">memuat...</td></tr>
<tr><td>control</td><td id="ctl">memuat...</td></tr>
<tr><td>status</td><td id="sts">memuat...</td></tr>
</tbody></table>
<script>
function get(id,url){fetch(url).then(r=>r.json()).then(d=>{document.getElementById(id).textContent=JSON.stringify(d).slice(0,300);}).catch(e=>{document.getElementById(id).textContent='gagal: '+e;});}
get('tel','/api/devices/cow-sprinkler-01/telemetry/latest');
get('ctl','/api/devices/cow-sprinkler-01/control');
get('sts','/api/devices/cow-sprinkler-01/status');
</script>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    server_version = "SmartCowLab"
    sys_version = ""

    def log_message(self, fmt, *args):
        log_event("http", "%s %s" % (self.address_string(), fmt % args))

    def _json(self, code, body):
        raw = json.dumps(body, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return None, "body kosong"
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8")), None
        except ValueError as exc:
            return None, "JSON tidak valid: %s" % exc

    def _route(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        query["__header__"] = [self.headers.get("Authorization", "")]
        return parsed.path.rstrip("/"), query

    def _authorised(self, query, need_write):
        if secret_ok(query):
            return True
        if need_write:
            log_event("denied", "%s %s tanpa token" % (self.command, self.path))
        return False

    def do_GET(self):
        path, query = self._route()
        if path in ("", "/"):
            raw = DASHBOARD_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        if path == "/health":
            self._json(200, {"status": "ok", "service": "smartcow-lab", "bind": BIND, "validate": VALIDATE})
            return
        if path.startswith(BASE):
            if path.endswith("/telemetry/latest") or path.endswith("/control") or path.endswith("/status"):
                if not self._authorised(query, need_write=False):
                    self._json(401, {"error": "Permission denied", "detail": "token tidak valid atau tidak ada"})
                    return
                state = load_state()
                if path.endswith("/telemetry/latest"):
                    self._json(200, state.get("telemetry", {}).get("latest", {}))
                elif path.endswith("/control"):
                    self._json(200, state.get("control", {}))
                else:
                    self._json(200, state.get("status", {}))
                return
            if "/telemetry/log/" in path:
                state = load_state()
                logs = state.get("telemetry", {}).get("log", {})
                key = path.split("/telemetry/log/")[1]
                self._json(200, logs.get(key, {}))
                return
        self._json(404, {"error": "not found", "path": path})

    def do_PUT(self):
        path, query = self._route()
        if not path.startswith(BASE):
            self._json(404, {"error": "not found", "path": path})
            return
        if not self._authorised(query, need_write=True):
            self._json(401, {"error": "Permission denied", "detail": "tulis butuh token valid"})
            return
        payload, err = self._read_body()
        if err:
            self._json(400, {"error": "bad request", "detail": err})
            return
        if path.endswith("/telemetry/latest"):
            problem = validate_telemetry(payload) if VALIDATE else None
            if problem:
                log_event("rejected", "telemetry ditolak: %s" % problem)
                self._json(400, {"error": "invalid payload", "detail": problem})
                return
            with _lock:
                state = load_state()
                state.setdefault("telemetry", {})["latest"] = payload
                state.setdefault("telemetry", {})["latest"]["ts"] = now_iso()
                save_state(state)
            log_event("write", "telemetry ditulis")
            self._json(200, {"ok": True, "path": path})
            return
        if path.endswith("/control"):
            problem = validate_control(payload) if VALIDATE else None
            if problem:
                log_event("rejected", "control ditolak: %s" % problem)
                self._json(400, {"error": "invalid payload", "detail": problem})
                return
            with _lock:
                state = load_state()
                state["control"] = payload
                state["control"]["updatedAt"] = now_iso()
                save_state(state)
            log_event("write", "control ditulis")
            self._json(200, {"ok": True, "path": path})
            return
        if "/events/" in path:
            with _lock:
                state = load_state()
                events = state.setdefault("events", {})
                events[path.split("/events/")[1]] = payload
                save_state(state)
            log_event("write", "event ditulis")
            self._json(200, {"ok": True, "path": path})
            return
        self._json(404, {"error": "not found", "path": path})

    def do_PATCH(self):
        path, query = self._route()
        if not path.startswith(BASE):
            self._json(404, {"error": "not found", "path": path})
            return
        if not self._authorised(query, need_write=True):
            self._json(401, {"error": "Permission denied", "detail": "tulis butuh token valid"})
            return
        payload, err = self._read_body()
        if err:
            self._json(400, {"error": "bad request", "detail": err})
            return
        if not path.endswith("/telemetry/latest"):
            self._json(404, {"error": "not found", "path": path})
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
            latest["ts"] = now_iso()
            save_state(state)
        log_event("write", "telemetry dipatch")
        self._json(200, {"ok": True, "path": path})


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    log_event("start", "smartcow-lab bind=%s port=%d validate=%s" % (BIND, PORT, VALIDATE))
    server = ThreadingHTTPServer((BIND, PORT), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
