# LOGBOOK PBL Keamanan Siber — Kelompok 12 Kelas B

**Skenario:** Smart Greenhouse Monitoring (ESP32 + MQTT + Web Dashboard)
**Subnet:** 192.168.12.0/24
**Anggota:**
1. Muhamad Akhdan Ramadhan (J0404241102) — Lead
2. Thevan Erlangga (J0404241073) — Blue Team
3. Fachri Abyasa Tarid (J0404241136) — Red Team

---

## Minggu 2 — Pembentukan Tim & Tools Analis
**Tanggal:** 2026-09-08
* Bentuk kelompok 12, bagi peran Lead/Blue/Red.
* Install VirtualBox + download ISO Ubuntu Server 22.04, Kali, Security Onion.
* Buat repo https://github.com/SwipeLz/TEK1314-2026-Kel-12-Kelas-B , push struktur awal `/docs /scripts`.
* Kendala: RAM laptop terbatas → sepakati target pakai Ubuntu CLI ringan, bukan GUI.
* Artefak: repo kosong + struktur folder.

## Minggu 3 — Dasar Linux (Lab)
**Tanggal:** 2026-09-15
* Latihan perintah dasar Linux, user management, `ufw`, `ss -tulpn`, `systemctl`.
* Red Team riset port IoT: 1883 MQTT, 80/443 web, 22 SSH.
* Artefak: catatan lab individu.

## Minggu 4 — Design Phase (Panduan id=84570) ✅ Sudah dilaksanakan
**Tanggal:** 2026-09-22
* **Blue Team:** gambar topologi 3 node (Attacker, Target IoT, Monitoring) di Draw.io, tentukan subnet 192.168.12.0/24.
* **Red Team:** serahkan daftar port yang perlu dibuka/diwaspadai (22, 80, 1883) + usulan OS target (Ubuntu Server CLI + Mosquitto, alternatif DVWA/Metasploitable ditolak karena tidak cocok IoT + berat).
* **Lead:** finalisasi `docs/design/topology.png` + `docs/design/ip_plan.md`, update README skenario IoT.
* Keputusan OS Target: **Ubuntu Server 22.04 CLI (ringan, 1 vCPU / 1-2GB RAM)** + Mosquitto + Python Flask/Node-RED dashboard.
* Artefak: `docs/design/topology.png`, `docs/design/ip_plan.md`.

## Minggu 5 — Logging Check (Target: Security Onion merekam ping)
**Tanggal:** 2026-09-29 (rencana)
* Install & jalankan Security Onion (SOC-KEL12, 192.168.12.200) mode standalone + interface promiscuous.
* Set IP statis ketiga VM dalam satu Host-Only network.
* Uji: dari Attacker `ping 192.168.12.5`, cek di Sguil/Squert muncul ICMP dengan src .100 dst .5 + timestamp benar.
* Jika Onion berat → Plan B: Wireshark + `/var/log/mosquitto/mosquitto.log` + `auth.log`.
* Artefak (wajib masuk `docs/phase-1-baseline/assets/`): `01-sguil-ping.png`, `02-ping-terminal.png`, `03-ip-addr.png`.
* PIC: Blue Team (setup Onion) + Red Team (kirim ping).

## Minggu 6 — Implementasi VM + Hardening Awal (Panduan id=87547)
**Tanggal:** 2026-10-06 (rencana)
* Build VM Target SRV-IOT-KEL12-G (192.168.12.5): install Mosquitto, buat user `iotadmin` (non-root, sudo), disable login root SSH, pasang UFW.
* UFW: default deny incoming, allow hanya `22/tcp` (dari .100/.200 saja jika bisa), `80/tcp`, `1883/tcp`, allow out.
* Mosquitto: `allow_anonymous false`, buat password file, ACL topik greenhouse.
* Update patch: `sudo apt update && sudo apt upgrade -y`.
* Nonaktifkan service tak perlu: `apache2` ganda / `telnet` / `cups` dll (cek `ss -tulpn`).
* Uji simulasi ESP32: `mosquitto_pub/sub` normal harus jalan, anon harus ditolak.
* Artefak: output `scripts/hardening-iot-server.sh`, screenshot `ufw status verbose`, `mosquitto.conf`.
* PIC: Blue Team eksekusi, Lead dokumentasi ke `baseline-report.md`.

## Minggu 7 — Hardening Review + Demo (10-15 menit)
**Tanggal:** 2026-10-13 (Senin depan, waspada review mendadak)
* Finalisasi `docs/phase-1-baseline/baseline-report.md` (Before Attack).
* Siapkan urutan demo: Topologi → Hardening walkthrough (`cat /etc/ufw/user.rules`) → Live logging (ping + MQTT publish terpantau) → Q&A.
* Validasi identitas: hostname + IP sesuai segmen, firewall aktif, Onion merekam.
* Artefak: baseline-report.md final + folder assets penuh + repo rapi.
* PIC: Lead presentasi, Blue dampingi infra, Red jelaskan rencana serangan Fase 2.

---
*Update file ini setiap ada progres. Format: tanggal + apa yang dikerjakan + siapa + kendala + artefak.*
