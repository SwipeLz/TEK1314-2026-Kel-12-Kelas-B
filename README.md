# PBL TEK1314 Keamanan Siber — Kelompok 12 Kelas B

**Skenario (adaptasi IoT, sesuai ralat terbaru):** Smart Greenhouse Monitoring — ESP32 + MQTT + Web Dashboard
**Subnet kelompok:** `192.168.12.0/24`
**Repo:** https://github.com/SwipeLz/TEK1314-2026-Kel-12-Kelas-B
**Folder lokal:** `F:\apaelah\TUGAS\smt5\Cyber\Tugas PBL`

> Catatan ralat: Panduan di bagian General class (id=81433, Strategi PBL tahun lalu dengan skenario 01–10) sudah dinyatakan OUTDATED dan TIDAK dipakai. Panduan yang benar dan dikerjakan adalah Panduan Minggu ke-4 / Pertemuan ke-4 (Design: topologi + IP plan, id=84570) dan Panduan Minggu ke-6 (id=87547), plus adaptasi skenario dari projek IoT kelompok.

## Anggota & Peran (mengikuti Panduan Minggu ke-4 v2: Lead / Blue / Red)

| Nama | NIM | Peran | Tanggung jawab |
|------|-----|-------|----------------|
| Muhamad Akhdan Ramadhan | J0404241102 | **Lead** | Finalisasi topologi + IP plan, upload GitHub, koordinasi OS target, LOGBOOK, baseline-report |
| Thevan Erlangga | J0404241073 | **Blue Team (Defender/Network)** | Gambar topologi, skema IP + routing, penempatan Security Onion, hardening (UFW, user, patch) |
| Fachri Abyasa Tarid | J0404241136 | **Red Team (Attacker)** | Riset port & celah, masukan OS target rentan, simulasi attack Fase 2 (ping, scan, MQTT/Web test, hanya ke IP kelompok sendiri) |

## Deskripsi Skenario IoT (dibuat kelompok, bukan perorangan)

Judul: **Smart Greenhouse Monitoring System**

Sistem greenhouse pintar untuk memantau suhu/kelembaban dan mengontrol pompa/relay secara remote:

* **Edge:** ESP32 + sensor DHT22 + relay pompa (simulasi, tidak perlu hardware fisik untuk PBL siber — cukup disimulasikan publish MQTT dari script/laptop).
* **Server IoT (Target Node / Korban):** 1 VM Ubuntu Server 22.04 CLI ringan yang menjalankan:
  * Mosquitto MQTT Broker port `1883` (topik `greenhouse/suhu`, `greenhouse/pompa/cmd`)
  * Web Dashboard (Node-RED / Flask sederhana) port `80` (dan `443` jika sempat) untuk grafik + tombol kontrol pompa
  * SSH port `22` untuk manajemen (akan di-harden)
* **Alur data normal:** ESP32 --publish--> MQTT (`192.168.12.5:1883`) --subscribe--> Dashboard Web (`192.168.12.5:80`) dibaca user via browser dari segmen yang sama. Semua trafik dilewatkan / dimonitor oleh Security Onion.
* **Fokus serangan Fase 2 (rencana Red Team):** Unauthorized Publish / Replay ke topik `greenhouse/pompa/cmd` (nyalakan pompa tanpa izin), MQTT brute-force / anon access jika salah config, Web Directory Traversal / brute-force login dashboard, dan SSH brute-force ringan. Semua HANYA ke `192.168.12.5`.
* **Fokus defense (Blue Team):** UFW ketat hanya buka 22/80/1883 dari segmen sendiri, disable anon MQTT, non-root user, update patch, Security Onion merekam ICMP + MQTT + HTTP.

Kenapa ini dipilih: mencakup 2 permukaan serangan (Web + IoT MQTT) tapi tetap ringan di laptop (1 VM target CLI saja), dan sangat cocok untuk demo logging (ping + publish MQTT langsung kelihatan di Sguil/Squert).

## Topologi Logis (ringkas)

```
[ESP32 Sim] --MQTT:1883--> [SRV-IOT-KEL12G 192.168.12.5 Ubuntu+Mosquitto+Web] <--monitor-- [SOC-KEL12 192.168.12.200 Security Onion]
        |                                                                                          ^
        +---------------------- HTTP:80 dashboard --------------------------------------------------+
[ATTACKER-KEL12 192.168.12.100 Kali/CyberOps] --ping/scan/MQTT-test--> [Target .5] (span/mirror ke .200)
```

* File gambar: `docs/design/topology.png`
* Detail IP: `docs/design/ip_plan.md`
* Laporan hardening + logging: `docs/phase-1-baseline/baseline-report.md`
* Bukti screenshot: `docs/phase-1-baseline/assets/`

Semua VM pakai Host-Only / Internal Network yang sama agar tidak bocor ke Wi-Fi kampus. Jangan serang IP di luar `192.168.12.0/24`.

## Struktur Repo (gabungan Panduan Design Minggu 4 + Demo Fase 1 Minggu 7)

```
/docs
  /design/                  <- Output Minggu 4: topology.png + ip_plan.md
  /phase-1-baseline/        <- Output Minggu 7: baseline-report.md + /assets/
  /phase-2-va/              <- Template Fase 2 (akan diisi Minggu 9-11)
  /phase-3-incident/        <- Template Fase 3 (akan diisi Minggu 12-15)
/scripts/                   <- hardening-iot-server.sh, verify-logging.sh
LOGBOOK.md
README.md
```

## Cara Demo Minggu 7 (10-15 menit)

1. **Topologi Review (3 mnt):** tunjukkan `topology.png`, jelaskan alur ESP32 -> MQTT -> Dashboard, dan posisi Security Onion sebagai passive monitor.
2. **Hardening Walkthrough (5 mnt):** `cat /etc/ufw/user.rules`, `sudo ufw status verbose`, `cat /etc/mosquitto/mosquitto.conf | grep -v ^#`, `id iotadmin`, tunjukkan SSH hanya key/non-root.
3. **Logging Verification (5 mnt):** dari Attacker `ping 192.168.12.5` + `mosquitto_pub -h 192.168.12.5 -t greenhouse/suhu -m "test"`, lalu tunjukkan live di Sguil/Squert: timestamp, src `192.168.12.100`, dst `192.168.12.5`, proto ICMP/MQTT.
4. **Q&A:** kenapa pilih Ubuntu CLI (ringan), kenapa hanya buka 22/80/1883, kenapa matikan anonymous MQTT.

## Checklist Sebelum Demo

* [ ] 3 VM running, IP statis benar, bisa saling ping
* [ ] `topology.png` + `ip_plan.md` sudah di-push
* [ ] UFW aktif, rule minimal
* [ ] Mosquitto tanpa anonymous, user + password
* [ ] Security Onion menangkap ping + MQTT publish (screenshot di `assets/`)
* [ ] LOGBOOK.md update Minggu 4-7
* [ ] Hostname: `SRV-IOT-KEL12-G`, `ATTACKER-KEL12`, `SOC-KEL12`
