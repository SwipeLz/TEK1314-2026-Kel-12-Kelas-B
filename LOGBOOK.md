# LOGBOOK - Kelompok 12 Kelas B

Anggota:
1. Muhamad Akhdan Ramadhan (J0404241102) - Lead
2. Thevan Erlangga (J0404241073) - Blue Team
3. Fachri Abyasa Tarid (J0404241136) - Red Team

## Minggu 2

* Bentuk kelompok dan bagi peran.
* Install VirtualBox, download ISO Ubuntu, Kali, Security Onion.
* Buat repo GitHub.

## Minggu 3

* Latihan dasar Linux.
* Red Team cek port yang perlu dibuka (80, 21, 22, 1883).

## Minggu 4

* Blue Team gambar topologi 3 node (attacker, target, monitoring).
* Tentukan subnet 192.168.12.0/24. Target .5, attacker .100, Onion .200.
* Lead upload `docs/design/topology.jpeg` dan `docs/design/ip_plan.md`.
* OS target: Ubuntu Server CLI (ringan). Cadangan Metasploitable 2.

## Minggu 5 (rencana)

* Set IP statis, tes ping antar VM.
* Pastikan Security Onion merekam ping di Sguil.
* Simpan screenshot ke `docs/phase-1-baseline/assets/`.

## Minggu 6 (rencana)

* Hardening target SRV-IOT-KEL12-B: UFW, user non-root, update patch, matikan service tidak perlu, MQTT tanpa anonymous.
* Simpan bukti `ufw status` dan config.

## Minggu 7 (rencana)

* Finalkan baseline-report.md.
* Siapkan demo: topologi, hardening, live logging.
