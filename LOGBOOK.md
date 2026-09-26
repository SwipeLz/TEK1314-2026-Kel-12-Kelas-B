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
* Sguil dibuka (user analyst, sensor seconion-import) tapi RealTime Events kosong. Dicek: proses snort IDS tidak jalan, container so-suricata/so-zeek tidak ada (hanya pipeline so-elastic/kibana/logstash yang Up). Jadi dipakai Plan B sesuai panduan: capture Wireshark di attacker (45 paket ICMP/ARP antar .100 dan .5). Bukti `assets/wireshark-icmp.png` + `assets/kel12-demo.pcap`.
* Kurang: hardening target (Minggu 6).

## Minggu 6 (26 Sep 2026)

* Target SRV-IOT-KEL12-B: matikan service berbahaya (vsftpd, telnet.socket, pox, ovs-vswitchd). Sisa sshd, networkd, lightdm.
* Firewall iptables: default INPUT DROP, buka ICMP + TCP 22/80/1883 hanya dari 192.168.12.0/24. Ping attacker ke target tetap 0% loss.
* User sec_admin (uid 1001, non-root). IP dibuat statis permanen via /etc/systemd/network/10-static.network (192.168.12.5/24).
* Patch: segmen isolasi tanpa internet, jadi pacman -Syu tidak jalan. Dicatat sebagai keterbatasan.
* Bukti: `assets/hardening-services.png`, `assets/hardening-firewall.png`, `assets/target-ip-statis.png`.

## Minggu 7 (rencana)

* Finalkan baseline-report.md.
* Siapkan demo: topologi, hardening, live logging.
