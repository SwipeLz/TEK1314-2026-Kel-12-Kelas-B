# Proyek PBL Keamanan Siber - Kelompok 12 Kelas B

**Mata Kuliah:** TEK1314 - Keamanan Siber
**Program Studi:** Teknologi Rekayasa Komputer
**Subnet:** 192.168.12.0/24
**Skenario:** No 10 — IoT Protocol Guardian (MQTT replay & publish tanpa izin).
Replika backend sistem penyemprotan sapi otomatis (ESP32 + DS18B20 → Firebase
Realtime Database → relay → solenoid valve). Detail di
[tech_stack_declaration.md](docs/presentation-minggu9/tech_stack_declaration.md).

## Anggota

1. Thevan Erlangga - J0404241073 - Lead
2. Muhamad Akhdan Ramadhan - J0404241102 - Red Team
3. Fachri Abyasa Tarid - J0404241136 - Blue Team

## 1. Skenario

Kami jalan di jaringan terisolasi 192.168.12.0/24. Satu VM target diposisikan sebagai server alat IoT. Blue team yang jaga, red team yang serang.

* Red team: reconnaissance dan eksploitasi web/service di server korban pakai Kali.
* Blue team: memantau semua trafik pakai Security Onion (Suricata/Zeek, Sguil/Squert).

Fokusnya sempit. Cuma satu target, jadi alur serang dan catatannya gampang dilacak.

Kalau ada yang aneh, langsung kelihatan.

## 2. File desain (minggu 4)

* [ip_plan.md](docs/design/ip_plan.md)
* [topology.jpeg](docs/design/topology.jpeg)
* Bukti VM: `docs/Laptop Backup/` dan `docs/Laptop Utama/`

Ini acuan IP dan topologi yang dipakai sampai fase baseline.

## 3. File baseline (minggu 5-7)

* [baseline-report.md](docs/phase-1-baseline/baseline-report.md)
* Bukti screenshot: `docs/phase-1-baseline/assets/`
* [LOGBOOK.md](LOGBOOK.md)

Struktur folder ikut panduan: `/docs/phase-1-baseline`, `/docs/phase-2-va`, `/docs/phase-3-incident`, `/scripts`, `LOGBOOK.md`, `README.md`.

Alurnya nyambung dari desain ke baseline. Desain minggu 4 mengunci alamat target, attacker, dan monitoring di satu subnet terisolasi supaya tidak ada trafik liar yang masuk atau keluar selama pengujian, kemudian baseline minggu 5 sampai 7 membuktikan konektivitas lewat ping tanpa loss dari attacker ke target dan ke Onion, hardening lewat iptables default INPUT DROP yang cuma buka ICMP dan beberapa port TCP dari segmen sendiri, dan logging lewat Sguil yang mencatat ping serta scan SSH dari attacker ke target. Pas demo minggu 7 tinggal nunjukin ulang apa yang sudah dicatat.

## 4. Pembagian tugas

* Lead: pastikan topologi dan IP final, upload ke GitHub.
* Red team: riset port yang dibuka (80, 21, 22, 1883) dan usulan OS target.
* Blue team: gambar topologi, susun IP, atur penempatan Security Onion, hardening.

Tugas dibagi biar demo minggu 7 tidak saling tunggu.

Catat semua. Jangan keluar segmen.

## 5. Demo minggu 7

1. Jelaskan topologi.
2. Tunjukkan config hardening (`ufw status`, `cat /etc/ufw/user.rules`).
3. Tunjukkan live logging di Security Onion (ping dari attacker tercatat).
4. Q&A.

Serangan hanya ke 192.168.12.5. Tidak ke jaringan kampus atau kelompok lain.

Itu aturan mainnya.
