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


def telemetry():
    base = random.uniform(27.0, 31.5)
    values = {}
    for idx in range(1, 7):
        values["t%d" % idx] = round(base + random.uniform(-1.2, 1.2), 2)
    values["avg"] = round(sum(values["t%d" % i] for i in range(1, 7)) / 6.0, 2)
    for idx in range(1, 5):
        values["h%d" % idx] = round(random.uniform(58.0, 78.0), 1)
    values["validCount"] = 6
    values["validMask"] = 63
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
