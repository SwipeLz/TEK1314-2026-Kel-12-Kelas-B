# Fase 3 — Incident Response (Template NIST, Minggu 12-15)

Isi setelah Fase 2 selesai, berdasarkan log Security Onion + Wireshark.

## Bab I: Ringkasan Eksekutif
* Infra: Smart Greenhouse (diagram + IP), insiden yang disimulasikan (misal: replay MQTT pompa + brute dashboard).

## Bab II: Deteksi & Analisis
1. Metode Deteksi: alert Sguil/Squert (ID, timestamp).
2. Analisis Log: screenshot dashboard + Zeek conn.log (src/dst/port).
3. Deep Packet Inspection: screenshot Wireshark payload `greenhouse/pompa/cmd = ON`.
4. Kategori: Unauthorized Access / IoT Replay Attack.

## Bab III: Containment, Eradication, Recovery
1. Containment: block IP attacker via UFW / cabut NIC VM (`sudo ufw deny from 192.168.12.100`), stop mosquitto sementara.
2. Eradication: ganti password MQTT, tutup anon, patch Flask, disable password SSH → key-only.
3. Recovery: restart service, verifikasi publish normal + dashboard pulih, monitor 1x24 jam.

## Bab IV: Post-Incident
* Lesson learned + rekomendasi: MQTT-TLS 8883, WAF, fail2ban, ACL topik ketat, audit berkala.
