# LOGBOOK - Kelompok 12 Kelas B

Anggota:
1. Thevan Erlangga (J0404241073) - Lead
2. Muhamad Akhdan Ramadhan (J0404241102) - Red Team
3. Fachri Abyasa Tarid (J0404241136) - Blue Team

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

## Minggu 5 (26 Sep 2026)

* Host adapter diset 192.168.12.1. Semua VM pindah ke Host-Only.
* Attacker (LabVM): IP 192.168.12.100, hostname ATTACKER-KEL12-B. User analyst, password cyberops.
* Target (Workstation): password sec_admin direset ke kel12admin via GRUB init=/bin/bash. Display diperbaiki (VMSVGA ke VBoxVGA, VRAM 64). IP 192.168.12.5, hostname SRV-IOT-KEL12-B.
* Onion: IP 192.168.12.200 di eth0 (diset arp on karena NOARP), hostname SOC-KEL12-B. User analyst, password cyberops.
* Tes ping attacker ke target dan ke Onion: 0% loss. Bukti di `docs/phase-1-baseline/assets/ping-attacker.log`.
* tcpdump di Onion menangkap ICMP (12 packets, 0 dropped). Bukti `assets/tcpdump-icmp.png`.
* Kurang: screenshot Sguil (belum dibuka), hardening target (Minggu 6).

## Minggu 6 (rencana)

* Hardening target SRV-IOT-KEL12-B: UFW, user non-root, update patch, matikan service tidak perlu, MQTT tanpa anonymous.
* Simpan bukti `ufw status` dan config.

## Minggu 7 (rencana)

* Finalkan baseline-report.md.
* Siapkan demo: topologi, hardening, live logging.
