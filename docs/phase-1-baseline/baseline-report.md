# Baseline Report Fase 1 (Minggu 7) - Kelompok 12 Kelas B

Subnet 192.168.12.0/24. Kondisi before attack, sistem sudah di-hardening sebelum diserang.

## 1. Aset

| Hostname | IP | OS | Service |
| :--- | :--- | :--- | :--- |
| SRV-IOT-KEL12-B | 192.168.12.5 | Ubuntu Server 22.04 CLI | SSH 22, Web 80, MQTT 1883 |
| ATTACKER-KEL12-B | 192.168.12.100 | Kali Linux | - |
| SOC-KEL12-B | 192.168.12.200 | Security Onion | Sguil, Squert, Zeek |

Detail IP ada di `../design/ip_plan.md`. Gambar ada di `../design/topology.jpeg`.

## 2. Hardening

Network:
* UFW default deny incoming, allow outgoing.
* Buka 22, 80, 1883 saja.
* Cek pakai `sudo ufw status verbose` dan `cat /etc/ufw/user.rules`.

System:
* Buat user biasa (non-root) untuk login, matikan login root SSH.
* `apt update && apt upgrade`.
* Matikan service yang tidak dipakai, cek pakai `ss -tulpn`.
* MQTT diset tidak boleh anonymous, pakai username/password.

Identitas:
* Hostname: SRV-IOT-KEL12-B, ATTACKER-KEL12-B, SOC-KEL12-B.
* IP: .5, .100, .200 di segmen 192.168.12.0/24.
* Cek pakai `hostnamectl` dan `ip addr`.

## 3. Logging Check Minggu 5

Security Onion sudah jalan dan merekam ping dari attacker ke target.

Cara uji:
* Dari attacker: `ping 192.168.12.5`
* Dari SOC: buka Sguil/Squert, filter IP 192.168.12.100 ke 192.168.12.5, pastikan ada timestamp, IP asal dan tujuan.

Bukti disimpan di `assets/`:
* screenshot Sguil merekam ping
* screenshot terminal ping
* screenshot `ip addr` dan `ufw status`

Kalau Onion tidak kuat di laptop, cadangan pakai Wireshark + log manual.

## 4. Demo Minggu 7

1. Jelaskan topologi.
2. Tunjukkan file hardening.
3. Tunjukkan live ping tercatat di Onion.
4. Q&A alasan pilih hardening tersebut.
