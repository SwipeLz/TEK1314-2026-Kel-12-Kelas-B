#!/bin/bash
# verify-logging.sh — Jalankan dari ATTACKER-KEL12 (.100). Pastikan SOC-KEL12 (.200) sedang merekam.
# Bukti untuk Minggu 5: ping + MQTT publish harus muncul di Sguil/Squert.
set -e
TARGET=${1:-192.168.12.5}
MQTT_USER=${2:-sensor1}
MQTT_PASS=${3:-GantiPasswordKuat123!}
echo "Target: $TARGET"
echo "[1] Ping 10x..."
ping -c 10 "$TARGET"
echo "[2] Cek port..."
nmap -p 22,80,1883 "$TARGET" || nc -zv "$TARGET" 22; nc -zv "$TARGET" 80; nc -zv "$TARGET" 1883 || true
echo "[3] MQTT publish normal (harus SUKSES + tercatat di Onion)..."
mosquitto_pub -h "$TARGET" -u "$MQTT_USER" -P "$MQTT_PASS" -t greenhouse/suhu -m '{"t":27.5,"h":70,"src":"verify"}' && echo "OK publish"
echo "[4] MQTT anon (harus GAGAL setelah hardening)..."
mosquitto_pub -h "$TARGET" -t greenhouse/suhu -m test && echo "WARNING anon bisa" || echo "OK anon ditolak"
echo "[5] HTTP dashboard..."
curl -I "http://$TARGET/" || true
echo "SELESAI. Sekarang buka Sguil di SOC (.200), filter src=192.168.12.100 dst=$TARGET, screenshot untuk assets/01 + 06."
