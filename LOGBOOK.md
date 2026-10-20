# LOGBOOK - Kelompok 12 Kelas B

Anggota:

1. Thevan Erlangga (J0404241073) - Lead, Purple Team
2. Muhamad Akhdan Ramadhan (J0404241102) - Red Team
3. Fachri Abyasa Tarid (J0404241136) - Blue Team

## Minggu 2

- Bentuk kelompok dan bagi peran.
- VirtualBox dipasang dan image Ubuntu, Kali, serta Security Onion diunduh.
- Repository GitHub dibuat sebagai tempat pengumpulan bukti hingga sesi presentasi.

## Minggu 3

- Latihan dasar Linux: perintah file, user, dan jaringan.
- Tim Red Team memeriksa port yang berpotensi digunakan: 80 (HTTP), 21 (FTP), 22 (SSH), dan 1883 (MQTT). Port tersebut kembali digunakan dalam skenario IoT.

Penguasaan dasar Linux perlu dikuasai. Tanpa dasar yang baik, proses pencarian
kesalahan pada IDS yang berlapis memerlukan waktu yang jauh lebih lama.

## Minggu 4

- Tim Blue Team menyusun topologi tiga node, yaitu attacker, target, dan monitoring.
- Subnet yang digunakan adalah 192.168.12.0/24, dengan target pada .5, attacker pada .100, dan Onion pada .200.
- Lead mengunggah `docs/design/ip_plan.md` beserta gambar topologi.
- OS target di lab ternyata Arch Linux Security Workstation, bukan Ubuntu Server seperti rencana awal. Perannya tetap sama, yaitu dianggap server IoT.

## Minggu 5 (26 Sep 2026)

- Adapter host dikonfigurasi pada 192.168.12.1 dan seluruh VM dipindahkan ke mode Host-Only.
- Attacker (LabVM): 192.168.12.100, hostname ATTACKER-KEL12-B, user analyst.
- Target (Workstation): password sec_admin direset ke kel12admin lewat GRUB init=/bin/bash, display diperbaiki (VMSVGA ke VBoxVGA, VRAM 64), IP 192.168.12.5, hostname SRV-IOT-KEL12-B.
- Onion dikonfigurasi pada 192.168.12.200 di eth0, dengan hostname SOC-KEL12-B dan user analyst.
- Uji ping dari attacker ke target dan ke Onion menghasilkan 0% packet loss. Bukti `ping-attacker.log` tersimpan di folder belajar PBL kelompok (Fase 1/bukti).
- Rekaman tcpdump di Onion menangkap 12 paket ICMP tanpa kehilangan paket. Bukti `assets/tcpdump-icmp.png`.
- Sguil berhasil dibuka, namun tabel RealTime Events tidak menampilkan data. Dua penyebabnya: `IDS_ENGINE_ENABLED=no` dan NIC monitoring promiscuous deny. Kami ubah keduanya lalu sensor direstart resmi dengan `nsm_sensor_ps-start`. Sesudah itu database sguild mencatat ping (GPL ICMP_INFO PING) dan SSH scan (ET SCAN Potential SSH Scan) dari .100 ke .5. Bukti `assets/sguil-db-events.log`.
- Perekaman Wireshark di attacker memperoleh 45 paket. Bukti `assets/wireshark-icmp.png` dan `assets/kel12-demo.pcap`.
- Tangkapan layar jendela Sguil pada sensor seconion-import. Bukti `assets/sguil-alert.png`.

Pelajaran yang diperoleh: perekaman paket mentah dan event sensor merupakan dua
lapisan yang berbeda. tcpdump dapat menampilkan paket secara lengkap,
sedangkan Sguil tetap kosong. Setelah mesin deteksi diaktifkan dan antarmuka
pemonitoran dibuka dengan mode yang sesuai, rantai pemrosesan dari snort
hingga basis data langsung berjalan.

## Minggu 6 (26 Sep 2026)

- Target SRV-IOT-KEL12-B: service berbahaya dimatikan (vsftpd, telnet.socket, pox, ovs-vswitchd). Tersisa sshd, networkd, lightdm. Dicek ulang dengan `systemctl list-unit-files --state=enabled`.
- Firewall iptables: default INPUT DROP, buka ICMP dan TCP 22/80/1883 hanya dari 192.168.12.0/24. Ping attacker ke target tetap 0% loss, jadi aturan tidak memotong uji konektivitas.
- User sec_admin (uid 1001, non-root). IP dibuat statis permanen di 192.168.12.5/24.
- Pembaruan paket tidak dapat dijalankan karena segmen isolasi tidak memiliki akses internet. Kondisi ini dicatat sebagai keterbatasan dan tidak dipaksakan.
- Bukti: `assets/hardening-services.png`, `assets/hardening-firewall.png`, `assets/target-ip-statis.png`.

## Minggu 7

- Baseline report difinalkan. Isinya tersimpan di folder belajar PBL kelompok (Fase 1/dokumen), bukan di repo karena struktur repo dibatasi Panduan PBL.
- Demo disiapkan dalam urutan topologi, hardening, dan live logging, sehingga penonton dapat mengikuti alur dari perancangan hingga bukti.

## Minggu 8 dan 9 (checkpoint Fase 2)

Skenario resmi ditetapkan: No 10, IoT Protocol Guardian. Proyek IoT asli kelompok
adalah SmartCow, sistem sprinkler kandang sapi. Rinciannya masuk ke
`docs/presentation-minggu9/tech_stack_declaration.md`. Data dari kandang asli tidak pernah
dimasukkan ke dalam lab, dan seluruh data yang digunakan bersifat dummy.

### Perbaikan lingkungan

- LabVM kembali memperoleh alamat 192.168.18.6 melalui DHCP. Alamat dikonfigurasi
  secara statis ke 192.168.12.100 dengan netplan. Uji ping dari .100 ke .5
  menghasilkan 0% packet loss.
- Aturan iptables Fase 1 hilang lagi setelah reboot, tabel kosong dan policy
  ACCEPT. Diterapkan ulang, disimpan ke `/etc/iptables/iptables.rules`, dan
  `iptables.service` di-enable.
- Penyimpanan journald dikonfigurasi menjadi persisten. Akun `analyst` pada target dikunci.

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

Untuk memastikan efektivitas kontrol, ketiga skenario dijalankan secara nyata
menggunakan data dummy dan tanpa mengganggu layanan yang berjalan.

- Sebelum hardening: nmap menemukan 22, 80, 1883, dan 9000 terbuka. Login
  `sec_admin` dengan kata sandi lab berhasil. Publish MQTT ke topik `control`
  diterima tanpa kredensial. Suntik telemetri dengan kelembapan 150 dan perintah
  sprinkler manual diterima.
- Sesudah hardening: seluruh login ditolak dengan `Permission denied (publickey)`,
  publish MQTT ditolak dengan CONNACK 5, suntik data ditolak dengan HTTP 400 atau
  401, dan port 9000 berubah jadi filtered karena API pindah ke loopback.
- Bukti berupa 24 tangkapan layar terminal asli di dalam VM tersimpan di
  `docs/blueteam/evidence/` dan `docs/redteam/evidence/`.

### Temuan di sisi monitoring

- **Interface management Security Onion tidak memiliki alamat IP pada
  192.168.12.0/24.** Di dalam VM Onion, `ip -4 addr` hanya menampilkan eth1
  `192.168.0.1/24`, eth2 `10.0.2.15/24` (NAT), dan docker0. Akibatnya host
  maupun penyerang tidak dapat menghubungi antarmuka management, dan sensor
  hanya dapat diamati melalui layar di dalam VM.
- **Sensor pakai Snort, bukan Suricata.** Tidak ada `eve.json` maupun
  `unified2.log` di host Onion, log-nya ada di dalam container. Event masuk ke
  Sguil lewat barnyard2 ke database `sguildb`, dan credential-nya ada di
  `/etc/sguil/sguil.conf`.
- Sguil sempat menampilkan baris event hari ini (`ET SCAN Nmap Scripting
  Engine`, `ET POLICY curl User-Agent`, `ET SCAN Potential SSH Scan`), jam
  06:30 sampai 06:47 GMT atau 13:30 sampai 13:47 WIB. Tabel tersebut tidak
  melakukan refresh otomatis setelah jendela dimunculkan kembali, sehingga
  tangkapan layar diambil secara manual.

### Perbaikan jaringan lab

- **Akar masalah ini berhasil ditemukan.** DHCP bawaan VirtualBox untuk
  host-only adapter #2 memiliki pool `192.168.18.0/24`, sedangkan alamat
  adapter tersebut adalah `192.168.12.1/24`. Akibatnya VM yang menggunakan DHCP
  memperoleh alamat dari pool yang keliru dan langsung kehilangan akses ke
  segmen lab. Seluruh VM kini memakai alamat IP statis pada setiap antarmuka
  agar tidak terkena masalah yang sama.
- **Interface management Security Onion (eth2) dikembalikan ke
  `192.168.12.200/24`** dan dibuat permanen lewat NetworkManager
  (`ipv4.method manual`, `ipv4.never-default yes`). Alasannya: di `.vbox` ada
  dua blok `<Network>`, dan blok lama menimpa, sehingga NIC management terpasang
  pada NAT, bukan Host-only adapter #2. Akibatnya alamat `.200` hilang setiap
  kali VM dinyalakan ulang dan tidak pernah dapat dijangkau dari luar VM.
- **Firewall guest Security Onion ditulis ulang oleh service firewall-nya.**
  Aturan `iptables -I INPUT -i eth2 -s 192.168.12.0/24 -j ACCEPT` yang kami
  pasang hilang sendiri dalam hitungan menit. Itu sebabnya bukti Sguil
  diambil dari dalam VM, bukan dari host.

### Kendala yang masih ada

- Security Onion tidak bisa diakses dari host. NIC management-nya tidak menjawab
  ARP dan VM itu tidak punya SSH server maupun Guest Additions, jadi bukti alert
  Sguil diambil manual dari layar Onion.
- Lingkungan lab tidak memiliki akses internet. Fail2ban, hydra, sshpass, dan
  mosquitto tidak dapat dipasang, sehingga pengujian menggunakan skrip klien
  yang dibuat sendiri.
- Memori host terbatas. Menyalakan ketiga VM secara bersamaan memberikan beban
  yang besar.
