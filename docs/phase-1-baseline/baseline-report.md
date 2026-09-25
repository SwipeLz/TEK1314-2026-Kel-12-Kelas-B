# Baseline Report — Fase 1 Hardening Review (Minggu 7)
**Kelompok 12 Kelas B — Smart Greenhouse Monitoring (IoT)**
**Subnet:** 192.168.12.0/24 | **Tanggal:** 2026-10-13 (demo)

## 1. Ringkasan Infrastruktur
Target: 1 VM Ubuntu Server 22.04 CLI (`SRV-IOT-KEL12-G`, 192.168.12.5) sebagai Server Alat IoT (Mosquitto MQTT + Web Dashboard + SSH). Attacker Kali (192.168.12.100) mensimulasikan ESP32 normal + penyerang. Monitoring Security Onion (192.168.12.200) merekam seluruh trafik. Kondisi ini adalah "Before Attack" — sistem sudah di-harden sebelum simulasi serangan Fase 2.

## 2. Inventaris Aset
| Hostname | IP | OS | Service | PIC |
|----------|----|----|---------|-----|
| SRV-IOT-KEL12-G | 192.168.12.5 | Ubuntu Server 22.04 CLI | sshd:22, Flask/Node-RED:80, mosquitto:1883 | Blue Team |
| ATTACKER-KEL12 | 192.168.12.100 | Kali / CyberOps | mosquitto-clients, nmap, curl, hydra | Red Team |
| SOC-KEL12 | 192.168.12.200 | Security Onion 2.4 | Sguil, Squert, Zeek, Suricata | Blue Team |

Lihat detail: `../design/ip_plan.md`, gambar: `../design/topology.png`.

## 3. Audit Before → After Hardening

### 3.1 Network Hardening (UFW)
**Before:** UFW inactive, semua port terbuka, `ss -tulpn` menunjukkan 22, 80, 1883 + service bawaan lain.
**After (dijalankan via `scripts/hardening-iot-server.sh`):**
```
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.12.0/24 to any port 22 proto tcp
sudo ufw allow 80/tcp
sudo ufw allow 1883/tcp
sudo ufw enable
sudo ufw status verbose
```
Bukti: screenshot `assets/04-ufw-status.png` + file `/etc/ufw/user.rules` (`cat /etc/ufw/user.rules` saat demo).
Alasan: default-deny + allowlist minimal (prinsip least exposure). SSH dibatasi segmen sendiri, MQTT/Web hanya yang dibutuhkan IoT.

### 3.2 System Hardening
* Buat user `iotadmin` (non-root, sudo), disable `PermitRootLogin no` + `PasswordAuthentication` direncanakan ke key-only di Fase 3:
  ```
  sudo adduser iotadmin
  sudo usermod -aG sudo iotadmin
  sudo grep -E "PermitRoot|PasswordAuth" /etc/ssh/sshd_config
  ```
* Update patch: `sudo apt update && sudo apt upgrade -y` (bukti `assets/05-apt-upgrade.png`).
* Matikan service tak perlu: cek `systemctl list-unit-files --state=enabled`, disable `cups`, `avahi-daemon`, `telnet` jika ada. Verifikasi `ss -tulpn` hanya 22/80/1883.
* Hak akses MQTT: `allow_anonymous false`, `password_file /etc/mosquitto/passwd`, ACL:
  ```
  user sensor1
  topic readwrite greenhouse/#
  ```
  Uji anon harus ditolak: `mosquitto_pub -h 192.168.12.5 -t greenhouse/suhu -m test` → `Connection Refused: not authorised`.

### 3.3 Identitas Standar
```
hostnamectl set-hostname SRV-IOT-KEL12-G  # di .5
hostnamectl set-hostname ATTACKER-KEL12   # di .100
hostnamectl set-hostname SOC-KEL12        # di .200
ip addr show  # pastikan .5 / .100 / .200 di 192.168.12.0/24
```
Bukti: `assets/03-ip-addr.png`.

## 4. Logging Check Minggu 5 (Security Onion merekam ping + MQTT)
Kriteria lulus: Sguil/Squert menampilkan ICMP dari .100 ke .5 dengan timestamp + IP benar, plus TCP MQTT 1883 saat publish normal.

Langkah verifikasi (`scripts/verify-logging.sh`):
```bash
# dari Attacker:
ping -c 10 192.168.12.5
mosquitto_pub -h 192.168.12.5 -u sensor1 -P '***' -t greenhouse/suhu -m '{"t":27.1}'
# dari SOC:
# buka Sguil → filter src=192.168.12.100 dst=192.168.12.5
# buka Squert → cari event ICMP + MQTT
```
Bukti wajib di `assets/`:
* `01-sguil-ping.png` — dashboard Sguil/Squert merekam ICMP (timestamp, src, dst terlihat)
* `02-ping-terminal.png` — terminal attacker ping sukses
* `03-ip-addr.png` — `ip addr` ketiga VM
* `06-sguil-mqtt.png` — event MQTT publish normal (opsional tapi nilai plus untuk skenario IoT)
* Jika Onion gagal (RAM): lampirkan `wireshark-ping.pcap` + `mosquitto.log` sebagai Plan B (diperbolehkan panduan).

## 5. Baseline Traffic Normal (untuk pembanding Fase 2/3)
* Ping rata-rata <1ms (host-only), 0% loss.
* `mosquitto_sub` menerima 1 msg/detik dari simulasi ESP32 tanpa error auth.
* Dashboard `http://192.168.12.5/` terbuka <500ms, menampilkan suhu terakhir.
* `sudo journalctl -u mosquitto --since "1 hour ago"` bersih dari `denied` kecuali uji anon yang memang harus ditolak.

## 6. Rencana Serangan Fase 2 (belum dieksekusi — hanya rencana Red Team)
Hanya ke 192.168.12.5: Nmap scan, MQTT anon-probe + replay `greenhouse/pompa/cmd`, Web traversal `/dashboard?file=../../etc/passwd`, SSH brute ringan dengan wordlist kecil. Semua akan direkam Onion untuk laporan VA.

## 7. Checklist Demo Minggu 7
* [ ] VM running, IP + hostname benar
* [ ] `sudo ufw status verbose` = active, 3 rule saja
* [ ] `cat /etc/ufw/user.rules` bisa ditunjukkan
* [ ] Anon MQTT ditolak, auth sukses
* [ ] Sguil live menampilkan ping + MQTT saat demo
* [ ] Repo rapi, LOGBOOK update

## 8. Lampiran
* `assets/` — semua screenshot + pcap
* `../../scripts/hardening-iot-server.sh` — skrip hardening yang dijalankan
* `../../scripts/verify-logging.sh` — skrip verifikasi logging
