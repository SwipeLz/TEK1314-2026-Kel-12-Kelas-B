#!/usr/bin/env python3
"""Buang literal token dari app.py dan rapikan docstring (hardening C2)."""
import sys

PATH = "/home/smartcow-lab/app.py"
OLD_DOC = ("Token API dibaca dari environment SMARTCOW_TOKEN. Sebelum hardening, token\n"
           "juga tersedia sebagai literal di berkas ini. Pola itu sengaja ditiru dari\n"
           "firmware ESP32 asli yang menyisipkan Database Secret di dalam sketch.")
NEW_DOC = ("Token API dibaca dari environment SMARTCOW_TOKEN. Setelah hardening, token\n"
           "tidak lagi ada di dalam berkas ini; nilainya diambil dari berkas .env yang\n"
           "hanya bisa dibaca akun aplikasi.")

src = open(PATH, encoding="utf-8").read()
lines = [line for line in src.splitlines() if not line.startswith("DEFAULT_TOKEN = ")]
src = "\n".join(lines) + "\n"
src = src.replace(
    'TOKEN = os.environ.get("SMARTCOW_TOKEN") or DEFAULT_TOKEN',
    'TOKEN = os.environ.get("SMARTCOW_TOKEN", "")',
)
src = src.replace(OLD_DOC, NEW_DOC)
open(PATH, "w", encoding="utf-8").write(src)
print("literal token dihapus dari app.py")
print("sisa kemunculan token di kode:",
      sum(1 for line in src.splitlines() if "smartcow-lab-token-2026" in line))
