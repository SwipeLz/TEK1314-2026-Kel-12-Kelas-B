# Proyek PBL Keamanan Siber - Kelompok 12 Kelas B

**Mata Kuliah:** TEK1314 - Keamanan Siber
**Program Studi:** D4 Teknologi Rekayasa Komputer
**Fase Proyek:** Minggu ke-4 (Design) + Minggu 5-7 (Baseline & Hardening Review)
**Subnet:** `192.168.12.0/24`
**Repo:** https://github.com/SwipeLz/TEK1314-2026-Kel-12-Kelas-B

> Ralat: Panduan General (id=81433, skenario 01–10 tahun lalu) OUTDATED dan tidak dipakai. Yang dikerjakan: Panduan Minggu ke-4 / Pertemuan ke-4 Design (id=84570) + Panduan Minggu ke-6 (id=87547), dengan skenario diadaptasi dari projek IoT kelompok.

## Anggota & Peran (Lead / Blue / Red — Panduan Minggu ke-4 v2)

| Nama | NIM | Peran |
|------|-----|-------|
| Muhamad Akhdan Ramadhan | J0404241102 | Lead — finalisasi topologi + IP, GitHub, LOGBOOK, baseline-report |
| Thevan Erlangga | J0404241073 | Blue Team — topologi, IP, penempatan Onion, hardening |
| Fachri Abyasa Tarid | J0404241136 | Red Team — riset port/celah, OS target, attack Fase 2 (hanya ke .5) |

## 1. Deskripsi Skenario Proyek (gabungan desain awal + adaptasi IoT)

Simulasi lingkungan pentest terisolasi di `192.168.12.0/24`:

* **Penyerangan (Red Team):** Kali (`192.168.12.100`) reconnaissance + eksploitasi web/service rentan di server korban (`.5`) — Nmap, MQTT probe, HTTP traversal, SSH brute ringan.
* **Pertahanan & Analisis (Blue Team):** Security Onion (`.200` + sniff promiscuous) dengan Suricata/Zeek + Sguil/Squert merekam real-time untuk deteksi + forensik.
* **Adaptasi IoT (sesuai ralat):** 1 VM Target berperan sebagai **Server Alat IoT Smart Greenhouse** — ESP32 + DHT22 + relay disimulasikan via `mosquitto_pub` dari Attacker. Target menjalankan Mosquitto MQTT (`1883`, topik `greenhouse/#`) + Web Dashboard (`80`) + SSH (`22`). OS Target: **Ubuntu Server 22.04 CLI ringan** (opsi Metasploitable 2 tetap dicatat sebagai alternatif rentan jika RAM cukup — lihat `ip_plan.md`). Alur normal: ESP32-SIM → MQTT `.5:1883` → Dashboard `.5:80` → user, semua dimonitor Onion.

## 2. Struktur Deliverables

Design (Minggu 4):
* [Dokumen Perencanaan IP (ip_plan.md)](docs/design/ip_plan.md)
* [Diagram Topologi — versi tim (jpeg)](docs/design/topology.jpeg)
* [Diagram Topologi — versi generate + penjelasan (png/md)](docs/design/topology.png) + [topology.md](docs/design/topology.md)

Baseline Fase 1 (Minggu 5-7):
* [Baseline Report (Before Attack)](docs/phase-1-baseline/baseline-report.md)
* [Bukti logging & hardening](docs/phase-1-baseline/assets/README.md)
* [LOGBOOK](LOGBOOK.md)
* [Skrip hardening + verifikasi](scripts/README.md)

Fase lanjutan (template):
* `docs/phase-2-va/` — VA Report (Minggu 9-11)
* `docs/phase-3-incident/` — Incident Response NIST (Minggu 12-15)

Bukti VM fisik:
* `docs/Laptop Backup/` + `docs/Laptop Utama/` — screenshot CyberOps VM & Security Onion jalan di laptop anggota.

## 3. Pembagian Peran Tim (detail)

* **Project Lead:** koordinasi desain, tinjauan arsitektur, manajemen repo, pastikan `topology` + `ip_plan` final disepakati Red & Blue.
* **Red Team:** riset celah (port 80, 21, 22, 3306 versi awal + tambahan 1883 MQTT untuk IoT), masukan OS target rentan, serahkan daftar port ke Blue.
* **Blue Team:** model topologi logis (Attacker, Target IoT, Monitoring), segmentasi IP `192.168.12.0/24`, penempatan sensor NIDS agar pantau seluruh segmen, hardening UFW/user/patch.

## 4. Demo Minggu 7 (10-15 menit)

1. Topologi: tunjukkan `topology.jpeg/png`, jelaskan ESP32 → MQTT → Web + posisi Onion span.
2. Hardening: `cat /etc/ufw/user.rules`, `sudo ufw status verbose`, `cat /etc/mosquitto/mosquitto.conf`.
3. Logging live: dari `.100` → `ping 192.168.12.5` + `mosquitto_pub`, lihat di Sguil (timestamp, src `.100`, dst `.5`).
4. Q&A: kenapa Ubuntu CLI (ringan), kenapa buka 22/80/1883 saja, kenapa matikan anon MQTT.

Semua attack HANYA ke `192.168.12.5`. Jangan ke Wi-Fi kampus / IP kelompok lain. Mode VirtualBox: Host-Only / Internal `kel12-net`, bukan Bridged.
