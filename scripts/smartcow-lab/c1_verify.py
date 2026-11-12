#!/usr/bin/env python3
"""c1_verify.py - verifikasi langsung kontrol C1 pada Target Node.

Menguji dua jalur:
  * MQTT: publish anonim, publish sah ke topik telemetri, publish ke topik kendali.
  * REST: payload sah, nilai kelembapan di luar rentang, dan request tanpa token.

Jalankan di Target Node sebagai root, karena kredensial broker dibaca dari
/home/smartcow-lab/secrets/mqtt_users.json dan token API dari /home/smartcow-lab/.env.
Nilai rahasia tidak pernah dicetak.

Contoh:
  sudo python3 c1_verify.py
  sudo python3 c1_verify.py --host 192.168.12.5 --port 80
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

LAB = "/home/smartcow-lab"
PUB = os.path.join(LAB, "mqtt_pub.py")
SECRETS = os.path.join(LAB, "secrets", "mqtt_users.json")
ENV = os.path.join(LAB, ".env")

FULL_TELEMETRY = {
    "t1": 30.5, "t2": 31.0, "t3": 30.8, "t4": 31.2, "t5": 30.9, "t6": 31.1,
    "h1": 60, "h2": 62, "h3": 58, "h4": 61,
}

results = []


def cred():
    raw = json.load(open(SECRETS))
    val = raw["esp32"]
    if not isinstance(val, str):
        raise SystemExit("kredensial esp32 harus berupa string")
    return val


def token():
    for line in open(ENV):
        if line.startswith("SMARTCOW_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("SMARTCOW_TOKEN tidak ditemukan pada .env")


def mqtt(host, topic, msg, user=None, pw=None):
    cmd = [sys.executable, PUB, "--host", host, "--topic", topic, "--message", msg]
    if user:
        cmd += ["--user", user, "--password", pw]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    tail = (p.stdout + p.stderr).strip().splitlines()[-1:]
    return p.returncode, tail


def api(host, port, method, path, body=None, tok=None):
    req = urllib.request.Request(
        "http://%s:%d%s" % (host, port, path),
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
    )
    req.add_header("Content-Type", "application/json")
    if tok:
        req.add_header("Authorization", "Bearer " + tok)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


def check(name, ok, detail):
    results.append((name, ok, detail))
    print(("PASS " if ok else "FAIL ") + name + " :: " + detail)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=9000)
    args = ap.parse_args()

    pw = cred()
    tok = token()
    base = "/api/devices/cow-sprinkler-01/telemetry/latest"

    rc, out = mqtt(args.host, "cow-sprinkler-01/control", '{"mode":"manual"}')
    check("mqtt-anon-rejected", rc == 3, "rc=%d %s" % (rc, out))

    rc, out = mqtt(args.host, "cow-sprinkler-01/telemetry/latest", '{"t1":30.5,"h1":60}', "esp32", pw)
    check("mqtt-auth-allowed-topic", rc == 0, "rc=%d %s" % (rc, out))

    rc, out = mqtt(args.host, "cow-sprinkler-01/control", '{"mode":"manual"}', "esp32", pw)
    check("mqtt-acl-forbidden-topic", rc == 4, "rc=%d %s" % (rc, out))

    st = api(args.host, args.port, "PUT", base, FULL_TELEMETRY, tok)
    check("api-valid-payload", st == 200, "HTTP %d" % st)

    bad = dict(FULL_TELEMETRY, h1=150)
    st = api(args.host, args.port, "PUT", base, bad, tok)
    check("api-humidity-out-of-range", st == 400, "HTTP %d" % st)

    st = api(args.host, args.port, "PUT", base, {"t1": 30.5})
    check("api-no-token-rejected", st == 401, "HTTP %d" % st)

    fails = [r for r in results if not r[1]]
    print("SUMMARY total=%d pass=%d fail=%d host=%s port=%d"
          % (len(results), len(results) - len(fails), len(fails), args.host, args.port))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
