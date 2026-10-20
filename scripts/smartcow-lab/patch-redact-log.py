#!/usr/bin/env python3
"""Sensor: jangan menulis token ke access log (query string auth=...)."""
import io
import re

PATH = "/home/smartcow-lab/app.py"
OLD = '''    def log_message(self, fmt, *args):
        log_event("http", "%s %s" % (self.address_string(), fmt % args))'''

NEW = '''    def log_message(self, fmt, *args):
        line = fmt % args
        line = re.sub(r"auth=[^&\\s\\"]+", "auth=REDACTED", line)
        log_event("http", "%s %s" % (self.address_string(), line))'''

src = io.open(PATH, encoding="utf-8").read()
if "auth=REDACTED" in src:
    print("sensor sudah terpasang")
else:
    if OLD not in src:
        print("GAGAL: blok log_message tidak ditemukan")
        raise SystemExit(1)
    src = src.replace(OLD, NEW)
    if "\nimport re\n" not in src:
        src = src.replace("\nimport json\n", "\nimport json\nimport re\n", 1)
    io.open(PATH, "w", encoding="utf-8").write(src)
    print("redaksi token pada access log terpasang")
