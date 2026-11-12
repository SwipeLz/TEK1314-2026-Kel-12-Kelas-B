#!/usr/bin/env python3
"""smartcow-lab - simulator sensor, meniru firmware ESP32 yang menulis telemetri.

Data yang dikirim sepenuhnya sintetis. Berguna sebagai baseline traffic yang
ditangkap sensor Security Onion, dan sebagai pembanding saat red team
menyuntikkan data palsu.
"""
import json
import os
import random
import time
import urllib.request

API = os.environ.get("SMARTCOW_API", "http://127.0.0.1:9000")
TOKEN = os.environ.get("SMARTCOW_TOKEN", "")
BASE = "/devices/cow-sprinkler-01"
INTERVAL = float(os.environ.get("SMARTCOW_SIM_INTERVAL", "2"))


def get_current_ssr():
    try:
        url = "%s%s/control?auth=%s" % (API, BASE, TOKEN)
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("manualSsr") == "on":
                return 1
            return 0
    except Exception:
        return 0


def telemetry():
    now_ms = int(time.time() * 1000)
    base = random.uniform(27.0, 31.5)
    values = {}
    for idx in range(1, 7):
        values["t%d" % idx] = round(base + random.uniform(-1.2, 1.2), 2)
    values["avg"] = round(sum(values["t%d" % i] for i in range(1, 7)) / 6.0, 2)
    for idx in range(1, 5):
        values["h%d" % idx] = round(random.uniform(58.0, 78.0), 1)
    values["validCount"] = 6
    values["validMask"] = 63
    values["humidityValidCount"] = 4
    values["humidityValidMask"] = 15
    values["leftOnline"] = True
    values["controlPolicyVersion"] = 2
    values["ssr"] = get_current_ssr()
    values["ts"] = now_ms
    values["measuredTs"] = now_ms
    return values


def put(path, payload):
    url = "%s%s%s?auth=%s" % (API, BASE, path, TOKEN)
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json"}, method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=4) as resp:
            return resp.status
    except Exception as exc:  # noqa: BLE001 - simulator hanya perlu status
        return "error: %s" % exc


def main():
    while True:
        status = put("/telemetry/latest", telemetry())
        print("telemetry -> %s" % status, flush=True)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
