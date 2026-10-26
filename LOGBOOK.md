# LOGBOOK - Kelompok 12 Kelas B

**Anggota Kelompok:**
1. Thevan Erlangga (J0404241073) - Lead, Purple Team
2. Muhamad Akhdan Ramadhan (J0404241102) - Red Team
3. Fachri Abyasa Tarid (J0404241136) - Blue Team

---

## Minggu 2

- Pembentukan tim kerja kelompok dan pembagian peran fungsional (Lead/Purple Team, Red Team, dan Blue Team).
- Pemasangan perangkat lunak virtualisasi VirtualBox pada host serta pengunduhan berkas citra mesin virtual Ubuntu, Kali Linux, dan Security Onion.
- Inisialisasi repositori Git dan GitHub sebagai media sentral dokumentasi progres, pengelolaan berkas konfigurasi, serta penyimpanan artefak pengujian hingga tahap presentasi.

## Minggu 3

- Pendalaman perintah dasar administrasi sistem Linux: manajemen berkas, pengelolaan hak akses pengguna, serta konfigurasi antarmuka jaringan.
- Red Team melakukan peninjauan awal terhadap port-port standar yang relevan dengan arsitektur sistem IoT: Port 80 (HTTP), Port 21 (FTP), Port 22 (SSH), dan Port 1883 (MQTT).
- Evaluasi teknis: Pemahaman mendalam mengenai administrasi Linux dan analisis jaringan menjadi pondasi penting. Tanpa penguasaan dasar yang memadai, proses pelacakan kendala (troubleshooting) pada sensor IDS berlapis membutuhkan waktu yang signifikan.

## Minggu 4

- Blue Team merancang arsitektur topologi jaringan laboratorium tiga node: Attacker Node, Target Node, dan Monitoring Node.
- Penentuan skema pengalamatan IP pada subnet `192.168.12.0/24`: Target Node pada `.5`, Attacker Node pada `.100`, dan Security Onion pada `.200`.
- Lead menyusun dan mengunggah dokumen rancangan skema IP (`docs/design/ip_plan.md`) beserta diagram topologi jaringan ke repositori.
- Identifikasi sistem operasi Target Node: citra laboratorium yang tersedia menggunakan Arch Linux Security Workstation (berbeda dari rancangan awal Ubuntu Server). Peran operasional tetap dipertahankan sebagai server replika backend IoT.

## Minggu 5 (26 September 2026)

- Konfigurasi antarmuka Host-Only adapter pada laptop host disetel ke alamat `192.168.12.1` dan seluruh mesin virtual dipindahkan ke mode jaringan Host-Only guna menjamin isolasi lingkungan pengujian.
- Attacker Node (LabVM): dikonfigurasi pada IP `192.168.12.100`, hostname `ATTACKER-KEL12-B`, akun pengguna `analyst`.
- Target Node (Arch Linux Workstation): kata sandi akun `sec_admin` dipulihkan melalui menu GRUB (`init=/bin/bash`), driver grafis VirtualBox disesuaikan (VBoxVGA, VRAM 64MB), IP statis disetel ke `192.168.12.5`, dan hostname disetel ke `SRV-IOT-KEL12-B`.
- Security Onion dikonfigurasi pada IP `192.168.12.200` pada antarmuka eth0, hostname `SOC-KEL12-B`, akun pengguna `analyst`.
- Pengujian konektivitas dasar: uji ping dari Attacker Node menuju Target Node dan Security Onion menghasilkan 0% packet loss.
- Rekaman tcpdump pada antarmuka sensor Security Onion berhasil menangkap 12 paket ICMP tanpa kehilangan data (`assets/tcpdump-icmp.png`).
- Pengujian visualisasi Sguil: jendela Sguil berhasil dibuka, namun tabel RealTime Events awalnya belum menampilkan rekaman alert. Investigasi menemukan dua penyebab: parameter `IDS_ENGINE_ENABLED=no` dan izin mode promiscuous pada adapter virtual belum disetel ke allow. Setelah kedua parameter diperbaiki dan sensor dijalankan ulang melalui perintah `nsm_sensor_ps-start`, basis data sguild berhasil mencatat alert ICMP ping (`GPL ICMP_INFO PING`) dan pemindaian SSH (`ET SCAN Potential SSH Scan`) dari `.100` ke `.5` (`assets/sguil-db-events.log`).
- Analisis lalu lintas jaringan menggunakan Wireshark pada Attacker Node merekam 45 paket pengujian (`assets/wireshark-icmp.png` dan `assets/kel12-demo.pcap`).
- Tangkapan layar antarmuka Sguil pada sensor seconion-import didokumentasikan pada `assets/sguil-alert.png`.
- Evaluasi teknis: penangkapan lalu lintas paket mentah dan pemrosesan alert pada sensor IDS merupakan dua lapisan yang berbeda. Perekaman melalui tcpdump dapat menangkap paket secara utuh meskipun basis data Sguil belum menampilkan rekaman alert. Setelah mesin deteksi Snort diaktifkan dan antarmuka sensor disetel ke mode promiscuous, alur korelasi dari sensor Snort melalui barnyard2 menuju basis data sguild dapat berjalan normal.

## Minggu 6 (26 September 2026)

- Target Node (`SRV-IOT-KEL12-B`): penonaktifan layanan yang tidak dibutuhkan dan berisiko tinggi (`vsftpd`, `telnet.socket`, `pox`, `ovs-vswitchd`). Layanan yang dipertahankan hanya `sshd`, `systemd-networkd`, dan `lightdm`. Verifikasi dilakukan melalui perintah `systemctl list-unit-files --state=enabled`.
- Konfigurasi firewall iptables: kebijakan default disetel ke INPUT DROP, memberikan izin paket ICMP serta koneksi TCP pada port 22, 80, dan 1883 khusus dari subnet `192.168.12.0/24`. Uji ping dari Attacker Node ke Target Node tetap menghasilkan 0% loss, membuktikan aturan firewall tidak mengganggu konektivitas sah.
- Pengelolaan hak akses: akun non-root `sec_admin` (UID 1001) ditetapkan sebagai akun operasional. Alamat IP disetel secara permanen pada `192.168.12.5/24`.
- Keterbatasan lingkungan: pembaruan paket sistem operasi (`pacman -Syu`) tidak dapat dilakukan karena isolasi total jaringan lab tanpa koneksi internet. Kondisi ini dicatat sebagai batasan lingkungan uji.
- Bukti pengujian tersimpan pada: `assets/hardening-services.png`, `assets/hardening-firewall.png`, dan `assets/target-ip-statis.png`.

## Minggu 7

- Penyusunan dan finalisasi dokumen Baseline Security Report Fase 1 pada direktori kerja internal kelompok.
- Perancangan skenario demonstrasi bertahap: diawali dari pembuktian topologi dan konektivitas, verifikasi kontrol pengamanan, hingga pembuktian pencatatan log secara langsung.

## Minggu 8 dan 9 (Checkpoint Evaluasi Fase 2)

Penetapan skenario tugas resmi kelompok: **Skenario No. 10 (*IoT Protocol Guardian*)**. Proyek IoT yang dipelajari adalah **SmartCow**, sistem pengendali sprinkler otomatis kandang sapi perah. Rincian arsitektur didokumentasikan pada `docs/presentation-minggu9/tech_stack_declaration.md`. Seluruh pengujian menggunakan data sintetis (dummy) demi menjamin keselamatan sistem mitra.

### Perbaikan Lingkungan Jaringan Laboratorium

- Penanganan kendala DHCP: mesin virtual Attacker sempat memperoleh alamat `192.168.18.6` akibat konfigurasi server DHCP default pada VirtualBox. Alamat dikonfigurasi ulang secara statis ke `192.168.12.100` menggunakan Netplan. Uji konektivitas ke `.5` menghasilkan 0% packet loss.
- Penanganan persistensi firewall: aturan iptables yang sempat tereset setelah restart dimuat ulang, diekspor ke `/etc/iptables/iptables.rules`, dan layanan `iptables.service` diaktifkan agar termuat otomatis saat boot.
- Konfigurasi logging: penyimpanan systemd-journald disetel ke mode persisten dan akun nonaktif `analyst` pada Target Node dikunci.

### Implementasi Replika Backend IoT pada Target Node

Target Node dikonfigurasi untuk mereplikasi arsitektur backend sistem SmartCow. Mengingat ketiadaan akses internet di laboratorium mencegah instalasi Firebase Emulator, kelompok membangun modul replika backend mandiri menggunakan pustaka standar Python 3.9 bawaan sistem operasi tanpa menambah dependensi pihak ketiga:

- `app.py`: modul REST API bergaya Realtime Database pada path `devices/cow-sprinkler-01/{telemetry/latest,telemetry/log,control,status,events}`, dilengkapi otentikasi token bearer, validasi rentang nilai sensor, dan pencatatan log akses.
- `broker.py`: broker MQTT mandiri minimal yang menerapkan otentikasi akun pengguna dan pembatasan hak akses topik (ACL), di mana topik `cow-sprinkler-01/control` dibatasi hak tulisnya.
- `simulator.py`: simulator data telemetri yang meniru mikrokontroler ESP32 dengan mengirimkan nilai acak suhu dan kelembapan dummy setiap dua detik untuk membentuk lalu lintas baseline sensor IDS.
- Web Server Nginx 1.18.0: menyajikan antarmuka web dashboard pada port 80 dan meneruskan rute `/api` ke backend lokal via proxy terbalik.
- Manajemen layanan: seluruh komponen dijalankan sebagai layanan systemd di bawah akun sistem non-privilese `smartcow`.

### Penerapan Sembilan Kontrol Pengamanan (Hardening)

Penerapan sembilan kontrol pengamanan terbagi merata ke dalam tiga kategori (rincian lengkap pada `docs/blueteam/hardening_checklist.md`):

- **Kategori A (Access & Authentication):** A1 (penolakan login root via SSH), A2 (autentikasi SSH berbasis kunci Ed25519 dan penonaktifan kata sandi), A3 (pembatasan koneksi sshd `MaxStartups 3:50:10` dan pembatasan laju koneksi iptables hashlimit).
- **Kategori B (Service & Attack Surface):** B1 (firewall iptables whitelist persisten), B2 (isolasi REST API pada loopback 127.0.0.1:9000), B3 (penyembunyian banner versi Nginx via `server_tokens off`).
- **Kategori C (Data & Application):** C1 (validasi batas nilai telemetri dan ACL topik MQTT), C2 (penghapusan literal token, izin berkas kredensial mode 600, dan rotasi token), C3 (pencatatan log akses tersanitasi dan verifikasi prosedur backup/restore data).

### Hasil Pengujian Serangan Red Team

Seluruh skenario penyerangan diuji secara nyata menggunakan data dummy untuk memverifikasi efektivitas kontrol pengamanan:

- **Kondisi Sebelum Hardening:** Pemindaian Nmap menemukan port 22, 80, 1883, dan 9000 terbuka. Percobaan login SSH akun `sec_admin` berhasil menggunakan kata sandi sederhana. Publikasi pesan MQTT ke topik kontrol diterima broker tanpa kredensial. Injeksi telemetri palsu (kelembapan 150%) dan perintah aktivasi pompa manual diterima oleh REST API.
- **Kondisi Sesudah Hardening:** Seluruh upaya login SSH berbasis kata sandi ditolak sistem (`Permission denied (publickey)`). Publikasi pesan MQTT tanpa otorisasi ditolak broker dengan kode `CONNACK 5`. Injeksi data di luar batas wajar ditolak REST API dengan kode `HTTP 400 Bad Request`. Request tanpa token ditolak dengan `HTTP 401 Unauthorized`. Port 9000 berstatus filtered dari jaringan luar karena API terikat pada loopback.
- Bukti pengujian berupa 24 tangkapan layar terminal asli tersimpan pada direktori `docs/blueteam/evidence/` dan `docs/redteam/evidence/`.

### Hasil Analisis dan Kendala Monitoring Node

- **Konfigurasi Antarmuka Monitoring:** Antarmuka manajemen Security Onion pada citra lab awalnya memiliki alamat default `192.168.0.1/24` (eth1) dan NAT (eth2). Antarmuka manajemen kemudian dikonfigurasi ulang secara statis ke `192.168.12.200/24` menggunakan NetworkManager (`ipv4.method manual`, `ipv4.never-default yes`).
- **Karakteristik Sensor:** Sensor Security Onion menggunakan mesin Snort dengan korelasi basis data via barnyard2 ke `sguildb`.
- **Verifikasi Alert Sguil:** Antarmuka Sguil berhasil memvalidasi rekaman alert lalu lintas penyerangan (`ET SCAN Nmap Scripting Engine`, `ET POLICY curl User-Agent`, dan `ET SCAN Potential SSH Scan`) yang terjadi antara pukul 06:30 hingga 06:47 GMT (13:30 hingga 13:47 WIB). Bukti tangkapan layar didokumentasikan pada repositori (`docs/blueteam/evidence/sguil-alert-minggu9.png`).
- **Identifikasi Kendala Isolasi Lab:** Mengingat lingkungan lab terisolasi dari internet dan memori fisik host terbatas, pengujian dijalankan secara terukur menggunakan skrip pengujian berbasis Python mandiri dengan pemanfaatan sumber daya komputasi yang efisien.

## Minggu 10

- Red Team merancang dan menguji skenario serangan ofensif Fase 2 (RT-01 pemetaan port, RT-02 exploitasi SSH, RT-03 manipulasi MQTT dan injeksi REST, RT-04 replay attack kontrol pompa).
- Blue Team menambahkan aturan signature Snort kustom pada Security Onion (`/etc/nsm/rules/local.rules`) untuk mendeteksi pola lalu lintas serangan spesifik SmartCow:
  - SID 1000001: `LOCAL-TEST-ICMP` untuk verifikasi keterhubungan jaringan.
  - SID 1000002: `SMARTCOW-MQTT Unauthorized Control Topic Access` untuk mendeteksi penulisan tanpa izin ke topik kontrol pompa.
  - SID 1000003: `SMARTCOW-HTTP Telemetry Attack Injection` untuk mendeteksi upaya injeksi telemetri tidak sah.
- Verifikasi rule update pada Security Onion: proses Snort dan Barnyard2 berhasil memuat aturan baru tanpa galat.
- Penyesuaian antarmuka jaringan Attacker Node: alamat IP disetel permanen ke `192.168.12.100/24` melalui konfigurasi Netplan agar komunikasi antar-node berjalan stabil pada segmen Host-Only.

## Minggu 11 (Finalisasi Evaluasi Fase 2)

- Replikasi antarmuka web SmartCow pada Target Node: memindahkan seluruh aset web asli (dashboard Overview, kartu suhu dan kelembapan, status SSR sprinkler, tabel riwayat telemetri, log aktivitas pompa air, dan manajemen akses admin) ke `/usr/share/nginx/html/` dengan adapter JavaScript offline mandiri tanpa dependensi CDN Google Firebase eksternal.
- Penyesuaian performa web: mematikan efek visual berat (animasi CSS, blur, dan bayangan kompleks) serta mengatur interval polling data ke 4 detik untuk menjaga pemakaian CPU Target Node tetap rendah (sekitar 4%).
- Penyelesaian siklus Purple Team 5 tahap untuk skenario RT-01 hingga RT-04 secara menyeluruh:
  - RT-01: pemindaian Nmap dari Attacker Node memastikan port 9000 berstatus filtered dan header web server menyembunyikan nomor versi.
  - RT-02: pengujian brute force kata sandi ditolak seluruhnya oleh autentikasi berbasis kunci Ed25519, serta laju koneksi konkuren diredam firewall.
  - RT-03: pengiriman pesan ke broker tanpa otentikasi ditolak dengan kode CONNACK 5, dan injeksi data sensor ke REST API ditolak dengan respons HTTP 400.
  - RT-04: pengiriman ulang (replay) paket kendali pompa ditolak oleh aturan hak topik broker (ACL drop), token lama ditolak dengan HTTP 401, serta percobaan serangan terdeteksi oleh Snort pada Security Onion (CID 6127).
- Verifikasi prosedur pemulihan data (C3): menguji skrip `/usr/local/bin/smartcow-restore` dengan mensimulasikan berkas data yang rusak (ukuran 0 byte). Hasil pemeriksaan nilai hash SHA256 membuktikan berkas pulih sempurna sesuai kondisi sebelum kerusakan (`d66f76c894af5e76579119d283e05bbc6c006266273e8881b59c285cd8be610f`).
- Penyusunan dokumen Vulnerability Assessment Report (VAR) sebagai laporan formal penyelesaian Fase 2 pada `docs/vulnerability-assessment-report.md`.
- Pemutakhiran repositori GitHub kelompok dengan seluruh artefak hasil pengujian dan dokumentasi lengkap.
