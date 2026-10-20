# LOGBOOK - Kelompok 12 Kelas B

Anggota:

1. Thevan Erlangga (J0404241073) - Lead, Purple Team
2. Muhamad Akhdan Ramadhan (J0404241102) - Red Team
3. Fachri Abyasa Tarid (J0404241136) - Blue Team

## Minggu 2

- Bentuk kelompok dan bagi peran.
- Install VirtualBox, download ISO Ubuntu, Kali, Security Onion.
- Buat repo GitHub. Repo jadi tempat single source of truth sampai demo.

## Minggu 3

- Latihan dasar Linux: perintah file, user, dan jaringan.
- Red team cek port yang perlu dibuka: 80 HTTP, 21 FTP, 22 SSH, 1883 MQTT. Port ini dipakai lagi di skenario IoT.

Dasar Linux tidak boleh goyang. Kalau dasarnya goyang, troubleshooting IDS yang
berlapis itu makan waktu dua kali lipat.

## Minggu 4

- Blue team gambar topologi tiga node: attacker, target, monitoring.
- Subnet 192.168.12.0/24. Target .5, attacker .100, Onion .200.
- Lead upload `docs/design/ip_plan.md` dan gambar topologi.
- OS target di lab ternyata Arch Linux Security Workstation, bukan Ubuntu Server seperti rencana awal. Perannya tetap sama, yaitu dianggap server IoT.

## Minggu 5 (26 Sep 2026)

- Host adapter diset 192.168.12.1, semua VM pindah ke Host-Only.
- Attacker (LabVM): 192.168.12.100, hostname ATTACKER-KEL12-B, user analyst.
- Target (Workstation): password sec_admin direset ke kel12admin lewat GRUB init=/bin/bash, display diperbaiki (VMSVGA ke VBoxVGA, VRAM 64), IP 192.168.12.5, hostname SRV-IOT-KEL12-B.
- Onion: 192.168.12.200 di eth0, hostname SOC-KEL12-B, user analyst.
- Ping attacker ke target dan ke Onion: 0% loss. Bukti `ping-attacker.log` ada di folder belajar PBL kelompok (Fase 1/bukti).
- tcpdump di Onion menangkap ICMP, 12 paket, 0 dropped. Bukti `assets/tcpdump-icmp.png`.
- Sguil dibuka tapi RealTime Events kosong. Dua penyebabnya: `IDS_ENGINE_ENABLED=no` dan NIC monitoring promiscuous deny. Kami ubah keduanya lalu sensor direstart resmi dengan `nsm_sensor_ps-start`. Sesudah itu database sguild mencatat ping (GPL ICMP_INFO PING) dan SSH scan (ET SCAN Potential SSH Scan) dari .100 ke .5. Bukti `assets/sguil-db-events.log`.
- Capture Wireshark di attacker, 45 paket. Bukti `assets/wireshark-icmp.png` dan `assets/kel12-demo.pcap`.
- Screenshot jendela Sguil, sensor seconion-import. Bukti `assets/sguil-alert.png`.

Pelajarannya: capture mentah dan event sensor itu dua lapis yang berbeda. tcpdump
bisa penuh sementara Sguil tetap kosong. Begitu engine dinyalakan dan interface
dibuka dengan mode yang benar, rantai dari snort sampai database langsung hidup.

## Minggu 6 (26 Sep 2026)

- Target SRV-IOT-KEL12-B: service berbahaya dimatikan (vsftpd, telnet.socket, pox, ovs-vswitchd). Tersisa sshd, networkd, lightdm. Dicek ulang dengan `systemctl list-unit-files --state=enabled`.
- Firewall iptables: default INPUT DROP, buka ICMP dan TCP 22/80/1883 hanya dari 192.168.12.0/24. Ping attacker ke target tetap 0% loss, jadi aturan tidak memotong uji konektivitas.
- User sec_admin (uid 1001, non-root). IP dibuat statis permanen di 192.168.12.5/24.
- Patch tidak bisa jalan karena segmen isolasi tanpa internet. Dicatat sebagai keterbatasan, bukan dipaksakan.
- Bukti: `assets/hardening-services.png`, `assets/hardening-firewall.png`, `assets/target-ip-statis.png`.

## Minggu 7

- Baseline report difinalkan. Isinya tersimpan di folder belajar PBL kelompok (Fase 1/dokumen), bukan di repo karena struktur repo dibatasi Panduan PBL.
- Demo disiapkan: topologi, hardening, live logging. Urutannya topologi dulu supaya penonton bisa ngikutin alur dari desain sampai bukti.

## Minggu 8 dan 9 (checkpoint Fase 2)

Skenario resmi ditetapkan: No 10, IoT Protocol Guardian. Proyek IoT asli kelompok
adalah SmartCow, sistem sprinkler kandang sapi. Rinciannya masuk ke
`docs/presentation-minggu9/tech_stack_declaration.md`. Data kandang asli tidak pernah
masuk ke lab, semuanya dummy.

### Perbaikan lingkungan

- LabVM ternyata nyasar lagi ke 192.168.18.6 lewat DHCP. Dikembalikan statis ke
  192.168.12.100 dengan netplan. Ping .100 ke .5: 0% loss.
- Aturan iptables Fase 1 hilang lagi setelah reboot, tabel kosong dan policy
  ACCEPT. Diterapkan ulang, disimpan ke `/etc/iptables/iptables.rules`, dan
  `iptables.service` di-enable.
- Storage journald diset persistent. Akun `analyst` di target dikunci.

### Replika backend IoT di Target Node

Target harus meniru stack backend proyek asli, jadi kami membangun replika sendiri
karena lab tidak punya akses internet untuk memasang Firebase Emulator. Semuanya
pakai Python 3.9 standar dari Arch, tidak ada dependensi baru.

- `app.py`: endpoint REST ala Realtime Database pada path
  `devices/cow-sprinkler-01/{telemetry/latest,telemetry/log,control,status,events}`,
  autentikasi token, validasi rentang sensor, dan log akses.
- `broker.py`: broker MQTT minimal dengan autentikasi username/password dan ACL
  topik. Topik `cow-sprinkler-01/control` hanya boleh dibaca.
- `simulator.py`: meniru firmware ESP32 yang menulis telemetri dummy setiap dua
  detik. Trafik ini yang jadi baseline untuk sensor Security Onion.
- Nginx 1.18.0 melayani dashboard di port 80 dan meneruskan `/api` ke API di
  loopback.
- Semua unit dijalankan lewat systemd dengan akun aplikasi `smartcow`.

Sumbernya ada di folder belajar PBL kelompok (Fase 2/config/smartcow-lab).

### Hardening Target Node

Sembilan kontrol, tiga di tiap kategori. Rinciannya di
`docs/blueteam/hardening_checklist.md`.

- A1: login root SSH ditolak. A2: login berbasis kunci, autentikasi password
  dimatikan. A3: sshd `MaxStartups 3:50:10` plus rate limit iptables untuk
  penyerang.
- B1: firewall whitelist yang persisten. B2: API hanya mendengarkan di loopback.
  B3: versi Nginx disembunyikan lewat `server_tokens off`.
- C1: validasi input pada endpoint REST dan ACL topik MQTT. C2: kredensial tidak
  hardcoded, permission 600, dan token yang bocor dirotasi. C3: log aktivitas dan
  backup data dengan uji pemulihan.

### Serangan ringan yang dieksekusi

Untuk memastikan kontrol bekerja, tiga skenario dijalankan sungguhan dengan data
dummy dan tanpa merusak layanan.

- Sebelum hardening: nmap menemukan 22, 80, 1883, dan 9000 terbuka. Login
  `sec_admin` dengan kata sandi lab berhasil. Publish MQTT ke topik `control`
  diterima tanpa kredensial. Suntik telemetri dengan kelembapan 150 dan perintah
  sprinkler manual diterima.
- Sesudah hardening: seluruh login ditolak dengan `Permission denied (publickey)`,
  publish MQTT ditolak dengan CONNACK 5, suntik data ditolak dengan HTTP 400 atau
  401, dan port 9000 berubah jadi filtered karena API pindah ke loopback.
- Bukti 24 tangkapan layar terminal asli di dalam VM, tersimpan di
  `docs/blueteam/evidence/` dan `docs/redteam/evidence/`.

### Temuan di sisi monitoring

- **Interface management Security Onion nggak punya IP di 192.168.12.0/24.**
  Di dalam VM Onion, `ip -4 addr` cuma menunjukkan eth1 `192.168.0.1/24`, eth2
  `10.0.2.15/24` (NAT), dan docker0. Karena itu host dan penyerang nggak bisa
  nyentuh management-nya, dan sensor cuma bisa diamati lewat layar di dalam VM.
- **Sensor pakai Snort, bukan Suricata.** Tidak ada `eve.json` maupun
  `unified2.log` di host Onion, log-nya ada di dalam container. Event masuk ke
  Sguil lewat barnyard2 ke database `sguildb`, dan credential-nya ada di
  `/etc/sguil/sguil.conf`.
- Sguil sempat menampilkan baris event hari ini (`ET SCAN Nmap Scripting
  Engine`, `ET POLICY curl User-Agent`, `ET SCAN Potential SSH Scan`), jam
  06:30 sampai 06:47 GMT atau 13:30 sampai 13:47 WIB. Tabelnya nggak
  auto-refresh setelah jendela di-braise ulang, jadi tangkapan layarnya diambil
  manual.

### Perbaikan jaringan lab

- **Akar masalah "IP nyasar" ketemu.** DHCP bawaan VirtualBox untuk host-only
  adapter #2 punya pool `192.168.18.0/24`, sementara adapter-nya
  `192.168.12.1/24`. Makanya VM yang pakai DHCP dapat alamat dari pool yang
  salah dan langsung nggak bisa nyentuh segmen lab. Semua VM sekarang pakai
  IP statis per antarmuka supaya kebal dari masalah ini.
- **Interface management Security Onion (eth2) dikembalikan ke
  `192.168.12.200/24`** dan dibuat permanen lewat NetworkManager
  (`ipv4.method manual`, `ipv4.never-default yes`). Alasannya: di `.vbox` ada
  dua blok `<Network>`, dan blok lama menimpa, sehingga NIC management
  nyantol NAT dan bukan Host-only adapter #2. Akibatnya address `.200` hilang
  tiap VM restart dan tidak pernah bisa dijangkau dari luar VM.
- **Firewall guest Security Onion ditulis ulang oleh service firewall-nya.**
  Aturan `iptables -I INPUT -i eth2 -s 192.168.12.0/24 -j ACCEPT` yang kami
  pasang hilang sendiri dalam hitungan menit. Itu sebabnya bukti Sguil
  diambil dari dalam VM, bukan dari host.

### Kendala yang masih ada

- Security Onion tidak bisa diakses dari host. NIC management-nya tidak menjawab
  ARP dan VM itu tidak punya SSH server maupun Guest Additions, jadi bukti alert
  Sguil diambil manual dari layar Onion.
- Lab tanpa internet. Fail2ban, hydra, sshpass, dan mosquitto tidak bisa dipasang,
  jadi skrip klien sendiri yang dipakai untuk uji.
- RAM host terbatas. Boot tiga VM sekaligus bikin berat.
