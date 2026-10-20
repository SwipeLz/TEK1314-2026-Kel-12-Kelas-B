#!/usr/bin/env python3
"""Patch nginx.conf di Target Node agar dashboard + API replika dilayani.

Argumen "tokens" menambahkan server_tokens off (bagian hardening B3).
"""
import re
import sys

PATH = "/etc/nginx/nginx.conf"
MARK = "SMARTCOW-LAB"

BLOCK = """        # SMARTCOW-LAB mulai
        location /api/ {
            proxy_pass http://127.0.0.1:9000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location / {
            proxy_pass http://127.0.0.1:9000;
            proxy_set_header Host $host;
        }
        # SMARTCOW-LAB selesai
"""

src = open(PATH, encoding="utf-8").read()

if MARK not in src:
    pattern = r"location / \{\s*root\s+/usr/share/nginx/html;\s*index\s+index\.html index\.htm;\s*\}"
    patched, count = re.subn(pattern, BLOCK, src, count=1)
    if count == 0:
        print("GAGAL: blok location / tidak ditemukan")
        sys.exit(1)
    open(PATH, "w", encoding="utf-8").write(patched)
    print("blok proxy smartcow ditambahkan")
else:
    print("blok proxy sudah ada")

if len(sys.argv) > 1 and sys.argv[1] == "tokens":
    src = open(PATH, encoding="utf-8").read()
    if "server_tokens" not in src:
        src = src.replace("    sendfile        on;", "    server_tokens off;\n    sendfile        on;", 1)
        open(PATH, "w", encoding="utf-8").write(src)
        print("server_tokens off ditambahkan")
    else:
        print("server_tokens sudah diatur")
