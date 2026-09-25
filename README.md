# Proyek PBL Keamanan Siber - Kelompok 12 Kelas B

**Mata Kuliah:** TEK1314 - Keamanan Siber
**Program Studi:** D4 Teknologi Rekayasa Komputer
**Subnet:** 192.168.12.0/24

## Anggota

1. Muhamad Akhdan Ramadhan - J0404241102 - Lead
2. Thevan Erlangga - J0404241073 - Blue Team
3. Fachri Abyasa Tarid - J0404241136 - Red Team

## 1. Skenario

Simulasi jaringan terisolasi di 192.168.12.0/24. Sesuai arahan, satu VM target dianggap sebagai server alat IoT yang dijaga blue team dan diserang red team.

* Red Team: reconnaissance dan eksploitasi web/service di server korban pakai Kali.
* Blue Team: memantau semua trafik pakai Security Onion (Suricata/Zeek, Sguil/Squert).

## 2. File Desain (Minggu 4)

* [ip_plan.md](docs/design/ip_plan.md)
* [topology.jpeg](docs/design/topology.jpeg)
* Bukti VM: `docs/Laptop Backup/` dan `docs/Laptop Utama/`

## 3. File Baseline (Minggu 5-7)

* [baseline-report.md](docs/phase-1-baseline/baseline-report.md)
* Bukti screenshot: `docs/phase-1-baseline/assets/`
* [LOGBOOK.md](LOGBOOK.md)

Struktur folder mengikuti panduan: `/docs/phase-1-baseline`, `/docs/phase-2-va`, `/docs/phase-3-incident`, `/scripts`, `LOGBOOK.md`, `README.md`.

## 4. Pembagian Tugas

* Lead: memastikan topologi dan IP final, upload ke GitHub.
* Red Team: riset port yang dibuka (80, 21, 22, 1883) dan usulan OS target.
* Blue Team: gambar topologi, susun IP, atur penempatan Security Onion, hardening.

## 5. Demo Minggu 7

1. Jelaskan topologi.
2. Tunjukkan config hardening (`ufw status`, `cat /etc/ufw/user.rules`).
3. Tunjukkan live logging di Security Onion (ping dari attacker tercatat).
4. Q&A.

Serangan hanya ke 192.168.12.5. Tidak ke jaringan kampus atau kelompok lain.
