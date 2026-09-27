# LOGBOOK - Kelompok 12 Kelas B

Anggota:
1. Thevan Erlangga (J0404241073) - Lead
2. Muhamad Akhdan Ramadhan (J0404241102) - Red Team
3. Fachri Abyasa Tarid (J0404241136) - Blue Team

## Minggu 2

* Bentuk kelompok dan bagi peran.
* Install VirtualBox, download ISO Ubuntu, Kali, Security Onion.
* Buat repo GitHub. Repo jadi tempat single source of truth sampai demo.

Semua bukti masuk repo.

## Minggu 3

* Latihan dasar Linux.
* Red team cek port yang perlu dibuka (80, 21, 22, 1883). Port ini yang nanti dipakai di skenario IoT.

Latihannya belum dalam, baru perintah file, user, dan network biar pas megang VM target dan sensor tidak kagok, karena kalau dasarnya goyang, troubleshooting IDS yang lumayan berlapis itu bakal makan waktu dua kali lipat.

## Minggu 4

* Blue team gambar topologi 3 node (attacker, target, monitoring).
* Tentukan subnet 192.168.12.0/24. Target .5, attacker .100, Onion .200.
* Lead upload `docs/design/topology.jpeg` dan `docs/design/ip_plan.md`.
* OS target: Arch Linux Security Workstation (VM yang dikasih lab). Beda dari rencana awal di `ip_plan.md`, tapi peran tetap sama sebagai server IoT.

Beda OS, peran sama.

## Minggu 5 (26 Sep 2026)

* Host adapter diset 192.168.12.1. Semua VM pindah ke Host-Only. Isolasi dulu, baru uji.
* Attacker (LabVM): IP 192.168.12.100, hostname ATTACKER-KEL12-B. User analyst, password cyberops.
* Target (Workstation): password sec_admin direset ke kel12admin via GRUB init=/bin/bash. Display diperbaiki (VMSVGA ke VBoxVGA, VRAM 64). IP 192.168.12.5, hostname SRV-IOT-KEL12-B.
* Onion: IP 192.168.12.200 di eth0 (diset arp on karena NOARP), hostname SOC-KEL12-B. User analyst, password cyberops.
* Tes ping attacker ke target dan ke Onion: 0% loss. Bukti di `docs/phase-1-baseline/assets/ping-attacker.log`.
* tcpdump di Onion menangkap ICMP (12 packets, 0 dropped). Bukti `assets/tcpdump-icmp.png`.
* Sguil dibuka tapi RealTime Events kosong. Ketemu dua penyebab: IDS_ENGINE_ENABLED=no dan NIC monitoring promiscuous deny. Kami ubah ke yes dan promiscuous allow-all, lalu sensor direstart resmi pakai nsm_sensor_ps-start. Sesudah itu DB sguild mencatat ping (GPL ICMP_INFO PING) dan SSH scan (ET SCAN Potential SSH Scan) dari .100 ke .5. Bukti `assets/sguil-db-events.log`.
* Capture Wireshark di attacker (45 paket). Bukti `assets/wireshark-icmp.png` + `assets/kel12-demo.pcap`.
* Screenshot jendela Sguil (sensor seconion-import, baris .100 ke .5). Bukti `assets/sguil-alert.png`.

Sempat bingung karena tcpdump dapat paket tapi Sguil kosong. Ternyata beda lapis: tcpdump lihat interface, Sguil nunggu alur sensor sampai DB. Begitu alur itu dibetulkan, event langsung masuk.

Pelajaran minggu ini sederhana tapi nempel lama, yaitu capture mentah dan event sensor itu dua lapis yang beda sehingga tcpdump bisa penuh padahal Sguil tetap kosong, dan begitu engine dinyalakan plus interface dibuka dengan mode yang benar, rantai dari snort sampai database langsung hidup dan semua jejak attacker tercatat rapi tanpa perlu ngulang pengujian dari awal, dan pola pikir lapis ini yang kami bawa ke hardening minggu berikutnya.

## Minggu 6 (26 Sep 2026)

* Target SRV-IOT-KEL12-B: matikan service berbahaya (vsftpd, telnet.socket, pox, ovs-vswitchd). Sisa sshd, networkd, lightdm. Cek ulang pakai `systemctl list-unit-files --state=enabled`.
* Firewall iptables: default INPUT DROP, buka ICMP + TCP 22/80/1883 hanya dari 192.168.12.0/24. Ping attacker ke target tetap 0% loss. Jadi aturan tidak motong uji konektivitas.
* User sec_admin (uid 1001, non-root). IP dibuat statis permanen via /etc/systemd/network/10-static.network (192.168.12.5/24).
* Patch: segmen isolasi tanpa internet, jadi pacman -Syu tidak jalan. Dicatat sebagai keterbatasan.
* Bukti: `assets/hardening-services.png`, `assets/hardening-firewall.png`, `assets/target-ip-statis.png`.

Rapi dan gampang dicek.

## Minggu 7 (rencana)

* Finalkan baseline-report.md.
* Siapkan demo: topologi, hardening, live logging. Urutannya itu, biar penonton ngikutin alur dari desain sampai bukti.
