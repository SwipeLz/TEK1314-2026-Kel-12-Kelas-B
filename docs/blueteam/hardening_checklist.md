# Checklist Pengamanan (Hardening) - Target Node

**Kelompok 12 | TEK1314 Praktik Keamanan Siber Terapan | Fase 2 (Minggu 9-11)**

## Daftar Isi

- [1. Tujuan dan Ruang Lingkup](#1-tujuan-dan-ruang-lingkup)
- [2. Ringkasan Hasil Implementasi Kontrol](#2-ringkasan-hasil-implementasi-kontrol)
- [3. Kategori A - Access and Authentication](#3-kategori-a---access-and-authentication)
- [4. Kategori B - Service and Attack Surface](#4-kategori-b---service-and-attack-surface)
- [5. Kategori C - Data and Application](#5-kategori-c---data-and-application)
- [6. Rencana Peningkatan dan Batasan Kontrol](#6-rencana-peningkatan-dan-batasan-kontrol)
- [7. Referensi Dokumen Terkait](#7-referensi-dokumen-terkait)

## 1. Tujuan dan Ruang Lingkup

Dokumen ini menyajikan implementasi sepuluh kontrol pengamanan (*hardening*) pada Target Node yang menjalankan replika backend SmartCow, sistem pengendali sprinkler kandang sapi perah. Kontrol dikelompokkan ke tiga kategori sesuai Bagian VIII Panduan PBL: Access and Authentication (3 kontrol), Service and Attack Surface (4 kontrol), dan Data and Application (3 kontrol).

- **Target Node:** `SRV-IOT-KEL12-B`, Arch Linux Security Workstation, `192.168.12.5`.
- **Attacker Node:** `ATTACKER-KEL12-B`, `192.168.12.100`, dipakai sebagai mesin penguji.
- **Monitoring Node:** `SOC-KEL12-B`, Security Onion, `192.168.12.200`.
- **Host administrasi:** `192.168.12.1`.
- **Layanan aktif:** OpenSSH 22 dan Nginx 80 bagi segmen lab; broker MQTT 1883 dan REST API 9000 hanya melayani loopback setelah B2 dan B4.
- **Replika backend:** kode `smartcow-lab` pada `/home/smartcow-lab`, dijalankan sebagai akun sistem `smartcow` melalui unit systemd.
- **Identitas perangkat IoT:** `cow-sprinkler-01`; seluruh data yang diproses bersifat sintetis (dummy).
- **Bukti:** tangkapan layar terminal dan log asli pada `docs/blueteam/evidence/`, ditautkan pada tiap kontrol.

Seluruh pengujian berjalan di jaringan virtual Host-Only. Ruang lingkup tidak mencakup infrastruktur Firebase produksi, sensor fisik, maupun pengendalian relay tegangan tinggi.

### Kriteria Status Verifikasi

- **Done:** kontrol diterapkan penuh dan diverifikasi melalui bukti konfigurasi maupun hasil pengujian operasional.
- **Partial:** kontrol baru terpenuhi pada sebagian aspek.
- **Not Yet:** kontrol belum diterapkan atau belum memiliki bukti teknis.

## 2. Ringkasan Hasil Implementasi Kontrol

| ID | Kategori | Rincian Kontrol | Hasil Verifikasi | Status |
| :--- | :--- | :--- | :--- | :--- |
| **A1** | Access & Authentication | Penolakan login root langsung via SSH | `PermitRootLogin no` efektif; seluruh upaya login root ditolak | Done |
| **A2** | Access & Authentication | Autentikasi kunci dan penonaktifan kata sandi | Login kunci Ed25519 berhasil; login kata sandi ditolak `Permission denied (publickey)` | Done |
| **A3** | Access & Authentication | Pembatasan sesi konkuren dan laju koneksi | `MaxStartups 3:50:10` aktif; hashlimit iptables meredam koneksi paralel | Done |
| **B1** | Service & Attack Surface | Firewall iptables whitelist persisten | INPUT DROP; whitelist 22, 80, 1883 untuk subnet lab saat penerapan; aturan tersimpan permanen | Done |
| **B2** | Service & Attack Surface | Isolasi REST API pada loopback | Listener berubah dari `0.0.0.0:9000` ke `127.0.0.1:9000`; port tidak terjangkau dari luar | Done |
| **B3** | Service & Attack Surface | Penyembunyian versi web server | Header berubah dari `nginx/1.18.0` menjadi `Server: nginx`; dashboard tetap 200 | Done |
| **B4** | Service & Attack Surface | Penutupan akses jaringan ke broker MQTT | Aturan ACCEPT 1883 dihapus; scan mencatat 22 dan 80 terbuka, 1883 dan 9000 filtered | Done |
| **C1** | Data & Application | Validasi input REST API dan ACL topik MQTT | Kelembapan 150% ditolak `HTTP 400`; publish ke topik kontrol ditolak broker | Done |
| **C2** | Data & Application | Manajemen kredensial, izin berkas, dan rotasi token | Berkas rahasia mode 600; token di environment; token lama ditolak | Done |
| **C3** | Data & Application | Logging aktivitas, backup, dan uji pemulihan | Log akses dan broker aktif; backup otomatis serta pemulihan terverifikasi | Done |

**Rekapitulasi: 10 kontrol Done, 0 Partial, 0 Not Yet.** Komposisinya 3 kontrol kategori A, 4 kategori B, dan 3 kategori C. Jumlah tersebut memenuhi ketentuan minimal delapan kontrol dengan sedikitnya dua kontrol per kategori pada Bagian VIII Panduan PBL. Status dinilai berdasarkan bukti pengujian langsung di laboratorium dan dibatasi oleh ruang lingkup simulasi.

---

## 3. Kategori A - Access and Authentication

### A1. Penolakan Login Langsung Akun Root Melalui SSH - Done

- **Tujuan Pengamanan:** Mencegah pengambilalihan hak akses tertinggi melalui SSH dan memastikan aktivitas administratif memakai akun pengguna terdaftar.
- **Kondisi Awal (Before):** Berkas `sshd_config.bak-kel12` (salinan konfigurasi sebelum hardening Minggu 6) masih memakai nilai bawaan tanpa direktif eksplisit. Nilai efektif berkas itu `permitrootlogin without-password` (setara `prohibit-password`) dan `maxstartups 10:30:100`, diukur dengan `sshd -T -f` pada verifikasi ulang. Konfigurasi aktif sendiri sudah memakai `PermitRootLogin no` sejak hardening Minggu 6 (`evidence/baseline/sshd-after.log`), sehingga A1 pada Fase 2 berfokus pada verifikasi ulang nilai tersebut.
- **Implementasi:** `PermitRootLogin no` dan `AllowUsers sec_admin` dipertahankan pada konfigurasi sshd, divalidasi dengan `sshd -t`, lalu diuji melalui simulasi login dari Attacker Node.
- **Hasil Verifikasi (After):** `sshd -T` mengonfirmasi `permitrootlogin no` dan `allowusers sec_admin`. Empat variasi percobaan login root dari penyerang seluruhnya ditolak.
- **Cakupan dan Batasan:** Kontrol ini melindungi akses SSH jarak jauh. Hak administratif di dalam server tetap dapat dipakai `sec_admin` melalui `sudo`.
- **Tautan Bukti:** [Konfigurasi sebelum](<evidence/kontrol A1 - Menolak login root langsung/sshd-efektif-sebelum.png>), [Konfigurasi setelah](<evidence/kontrol A1 - Menolak login root langsung/sshd-efektif-setelah.png>), [Login root ditolak](<evidence/kontrol A1 - Menolak login root langsung/login-root-ditolak.png>).

### A2. Autentikasi SSH Berbasis Kunci dan Penonaktifan Kata Sandi - Done

- **Tujuan Pengamanan:** Memastikan akses terminal hanya memakai kunci kriptografis yang valid, sehingga kebocoran kata sandi tidak dapat menghasilkan shell interaktif.
- **Kondisi Awal (Before):** `sshd -T` awal menampilkan `passwordauthentication yes`, dan direktori `.ssh` pengguna belum memiliki `authorized_keys`. Akun `sec_admin` saat itu dapat login dengan kata sandi sederhana.
- **Implementasi:** Pasangan kunci Ed25519 dibangkitkan pada host administrasi; kunci publik dipasang di `/home/sec_admin/.ssh/authorized_keys` dengan mode 600 dan kepemilikan `sec_admin`; direktif `PasswordAuthentication no` diaktifkan.
- **Hasil Verifikasi (After):** Sesi dengan kunci privat berhasil masuk ke `SRV-IOT-KEL12-B`, sedangkan seluruh login kata sandi gagal dengan `Permission denied (publickey)`.
- **Cakupan dan Batasan:** Satu pasangan kunci dipakai untuk akun administratif lab. Konsol virtual tetap tersedia sebagai jalur pemulihan darurat.
- **Tautan Bukti:** [Konfigurasi sebelum](<evidence/kontrol A2 - Login SSH berbasis kunci/sshd-config-sebelum.png>), [Konfigurasi setelah](<evidence/kontrol A2 - Login SSH berbasis kunci/sshd-config-setelah.png>), [Login kunci berhasil](<evidence/kontrol A2 - Login SSH berbasis kunci/login-kunci-berhasil.png>), [Pemasangan kunci publik](<evidence/kontrol A2 - Login SSH berbasis kunci/kunci-publik-terpasang.png>), penolakan kata sandi pada [log penolakan kata sandi](evidence/verifikasi-ulang/08-password-login-rejected.log) dan `redteam/evidence/04-percobaan-login-setelah.png`.

### A3. Pembatasan Percobaan Login dan Laju Koneksi SSH - Done

- **Tujuan Pengamanan:** Membatasi frekuensi percobaan autentikasi berulang dan meredam laju koneksi baru dari alamat penyerang.
- **Kondisi Awal (Before):** Nilai bawaan `MaxStartups 10:30:100`, dan firewall belum memiliki aturan pembatas laju pada port 22.
- **Implementasi:** `MaxStartups` diperketat menjadi `3:50:10`. Modul `hashlimit` iptables membatasi maksimal 3 koneksi baru per detik dari `192.168.12.100` dengan toleransi burst 6 paket, dan paket selebihnya dijawab TCP RST. Aturan disimpan ke `/etc/iptables/iptables.rules`.
- **Hasil Verifikasi (After):** Saat penyerang membuka 8 sesi SSH paralel, sebagian besar koneksi langsung digagalkan firewall. Seluruh percobaan tercatat pada log sistem melalui `LogLevel VERBOSE`.
- **Cakupan dan Batasan:** Pembatasan laju iptables difokuskan pada IP penyerang lab, sedangkan `MaxStartups` berlaku untuk semua sesi yang belum terotentikasi.
- **Tautan Bukti:** [Konfigurasi sshd dan iptables](<evidence/kontrol A3 - Pembatasan percobaan login/sshd-maxstartups-dan-rate-limit.png>), [Uji koneksi paralel](<evidence/kontrol A3 - Pembatasan percobaan login/uji-koneksi-paralel-dari-penyerang.png>).

---

## 4. Kategori B - Service and Attack Surface

### B1. Konfigurasi Firewall Whitelist yang Persisten - Done

- **Tujuan Pengamanan:** Membatasi lalu lintas masuk hanya untuk layanan yang dibutuhkan dan membatasi sumber akses pada subnet laboratorium.
- **Kondisi Awal (Before):** Tabel iptables sempat kosong dengan kebijakan default ACCEPT karena konfigurasi belum tersimpan permanen dan hilang setelah VM restart.
- **Implementasi:** Kebijakan INPUT DROP. Izin diberikan untuk loopback, paket RELATED/ESTABLISHED, ICMP dari subnet lab, serta TCP 22, 80, dan 1883. Konfigurasi diekspor dengan `iptables-save` ke `/etc/iptables/iptables.rules`, dan `iptables.service` diaktifkan saat boot.
- **Hasil Verifikasi (After):** `iptables -S` menampilkan seluruh rantai aturan dan `iptables.service` berstatus `enabled`. Pada tahap ini whitelist masih meloloskan 22, 80, dan 1883 sehingga Nmap mencatat tiga port terbuka. Jumlahnya turun setelah B4 diterapkan (`pemindaian-port-mqtt-sebelum.png` dan `pemindaian-port-mqtt-setelah.png`).
- **Cakupan dan Batasan:** Penyaringan difokuskan pada paket masuk (INPUT). Penyimpanan permanen memastikan aturan tetap aktif setelah sistem dinyalakan ulang.
- **Tautan Bukti:** [Aturan sebelum](<evidence/kontrol B1 - Firewall whitelist dan persisten/iptables-sebelum.png>), [Aturan setelah](<evidence/kontrol B1 - Firewall whitelist dan persisten/iptables-setelah.png>), [Pemindaian port sebelum](<evidence/kontrol B1 - Firewall whitelist dan persisten/pemindaian-port-sebelum.png>), [Pemindaian port setelah](<evidence/kontrol B1 - Firewall whitelist dan persisten/pemindaian-port-setelah.png>), [Aturan setelah B4](<evidence/kontrol B1 - Firewall whitelist dan persisten/iptables-verifikasi-ulang.png>), [Pemindaian sebelum penutupan 1883](<evidence/kontrol B1 - Firewall whitelist dan persisten/pemindaian-port-mqtt-sebelum.png>), [Pemindaian sesudah penutupan 1883](<evidence/kontrol B1 - Firewall whitelist dan persisten/pemindaian-port-mqtt-setelah.png>).

### B2. Isolasi REST API Internal pada Antarmuka Loopback - Done

- **Tujuan Pengamanan:** Menghilangkan eksposur langsung antarmuka backend dari segmen jaringan eksternal.
- **Kondisi Awal (Before):** `ss -lntp` menunjukkan REST API mendengarkan pada `0.0.0.0:9000`, yaitu seluruh antarmuka. Port 9000 tidak diloloskan firewall, sehingga layanan hanya bergantung pada satu lapis penyaringan.
- **Implementasi:** `SMARTCOW_BIND` pada `.env` diubah menjadi `127.0.0.1`, lalu `smartcow-api` dimuat ulang. Akses eksternal diarahkan melalui reverse proxy Nginx.
- **Hasil Verifikasi (After):** `ss -lntp` menunjukkan listener terikat eksklusif pada `127.0.0.1:9000`. Pemindaian dari mesin penyerang memastikan port 9000 tidak dapat dihubungi dari jaringan, sementara dashboard tetap berkomunikasi melalui proxy lokal.
- **Cakupan dan Batasan:** Kontrol ini menguatkan pertahanan berlapis pada tingkat soket aplikasi, melengkapi penyaringan paket firewall.
- **Tautan Bukti:** [Listener sebelum](<evidence/kontrol B2 - API hanya mendengarkan di loopback/listener-sebelum.png>), [Listener setelah](<evidence/kontrol B2 - API hanya mendengarkan di loopback/listener-setelah.png>), [Hasil pemindaian Nmap](<evidence/kontrol B2 - API hanya mendengarkan di loopback/pemindaian-port-setelah.png>).

### B3. Penyembunyian Identitas dan Versi Web Server Nginx - Done

- **Tujuan Pengamanan:** Mengurangi informasi teknis web server agar pencarian kerentanan spesifik versi (*fingerprinting*) lebih sulit.
- **Kondisi Awal (Before):** `curl -I http://127.0.0.1/` menghasilkan `Server: nginx/1.18.0`, dan direktif `server_tokens` belum didefinisikan.
- **Implementasi:** `server_tokens off;` ditambahkan pada blok `http` di `/etc/nginx/nginx.conf`, diverifikasi dengan `nginx -t`, lalu konfigurasi dimuat ulang.
- **Hasil Verifikasi (After):** Header respons menjadi `Server: nginx` tanpa nomor versi. Nmap dengan deteksi versi tidak lagi menampilkan rilis perangkat lunak, dan dashboard tetap berjalan (HTTP 200).
- **Cakupan dan Batasan:** Kontrol ini hanya menyembunyikan informasi versi dan tidak menggantikan kewajiban pembaruan keamanan berkala.
- **Tautan Bukti:** [Header sebelum](<evidence/kontrol B3 - Menyembunyikan versi Nginx/header-http-sebelum.png>), [Header setelah](<evidence/kontrol B3 - Menyembunyikan versi Nginx/header-http-setelah.png>).

### B4. Penutupan Akses Jaringan ke Broker MQTT - Done

- **Tujuan Pengamanan:** Menghapus permukaan serangan broker MQTT dari segmen lab. Broker hanya melayani konsumen lokal, yaitu simulator dan pemeriksaan di Target Node.
- **Kondisi Awal (Before):** Whitelist firewall masih meloloskan `tcp/1883` dari `192.168.12.0/24`. Nmap dari Attacker Node mencatat tiga port terbuka: 22, 80, dan 1883 (`redteam/evidence/13-pemindaian-port-mqtt-sebelum.png`).
- **Implementasi:** Aturan `-A INPUT -s 192.168.12.0/24 -p tcp --dport 1883 -j ACCEPT` dihapus, lalu tabel disimpan ulang ke `/etc/iptables/iptables.rules`. Kebijakan INPUT DROP dan `-A INPUT -i lo -j ACCEPT` dipertahankan sehingga broker tetap menerima koneksi loopback.
- **Hasil Verifikasi (After):** Nmap mencatat dua port terbuka, yaitu 22 dan 80; port 1883 dan 9000 berstatus filtered (`redteam/evidence/14-pemindaian-port-mqtt-setelah.png`). Pemindaian penuh `-p-` juga hanya menemukan 22 dan 80 (`redteam/evidence/11-pemindaian-port-lengkap.png`). Koneksi `127.0.0.1:1883` tetap berhasil, `/health` melalui Nginx membalas 200, dan unit `smartcow-broker`, `smartcow-api`, `smartcow-sim`, serta `nginx` tetap `active`.
- **Cakupan dan Batasan:** Penutupan bersifat jaringan, bukan penghapusan layanan. Untuk demonstrasi terkontrol, aturan ACCEPT 1883 dapat ditambahkan kembali sementara; prosedur rollback dicatat pada LOGBOOK. Setelah perubahan ini, pengujian publish MQTT dari Attacker Node tidak dapat dilakukan lagi pada lapisan TCP.
- **Tautan Bukti:** [Pemindaian sebelum](<evidence/kontrol B1 - Firewall whitelist dan persisten/pemindaian-port-mqtt-sebelum.png>), [Pemindaian sesudah](<evidence/kontrol B1 - Firewall whitelist dan persisten/pemindaian-port-mqtt-setelah.png>), [Aturan iptables setelah verifikasi ulang](<evidence/kontrol B1 - Firewall whitelist dan persisten/iptables-verifikasi-ulang.png>).

---

## 5. Kategori C - Data and Application

### C1. Validasi Batasan Input REST API dan Pembatasan Hak Topik MQTT (ACL) - Done

- **Tujuan Pengamanan:** Mencegah manipulasi telemetri yang tidak logis dan membatasi hak publish pada kanal topik yang sah bagi tiap perangkat.
- **Kondisi Awal (Before):** Validasi backend belum aktif, sehingga `PUT` dengan kelembapan 150% tetap diterima (HTTP 200). Broker menerima koneksi anonim dan meneruskan pesan ke topik kontrol `cow-sprinkler-01/control`.
- **Implementasi:** `SMARTCOW_VALIDATE` diaktifkan dengan rentang suhu -20 sampai 70 °C, kelembapan 0 sampai 100%, THI 0 sampai 130, dan kewajiban seluruh field telemetri dasar. Pada broker, `SMARTCOW_MQTT_AUTH` dan `SMARTCOW_MQTT_ACL` diaktifkan sehingga kredensial sensor hanya boleh menulis ke `cow-sprinkler-01/telemetry/latest`.
- **Hasil Verifikasi (After):** Diuji ulang di Target Node yang hidup dengan hasil 6 dari 6 lulus: publish anonim ditolak (`CONNACK return code 5`), akun `esp32` berhasil menulis ke topik telemetri, publish ke topik kontrol diputus broker, `PUT` valid dibalas `HTTP 200`, kelembapan 150% dibalas `HTTP 400`, dan `PUT` tanpa token dibalas `HTTP 401`.
- **Cakupan dan Batasan:** Pengujian berfokus pada logika validasi data dan otorisasi kanal IoT dalam simulasi laboratorium. Tangkapan layar `mqtt-acl-terverifikasi.png` dari 20 Oktober 2026 tidak dipakai sebagai bukti utama karena isinya menampilkan kegagalan `Permission denied` saat skrip dijalankan, sehingga pengujiannya tidak pernah tereksekusi.
- **Tautan Bukti:** [Verifikasi langsung C1](evidence/verifikasi-ulang/01-c1-live-verification.log), [Pemeriksaan dari Attacker Node](evidence/verifikasi-ulang/11-external-port-check.log), [Validasi sebelum](<evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/validasi-input-sebelum.png>), [Validasi setelah](<evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/validasi-input-setelah.png>), [Publish MQTT sebelum](<evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/mqtt-publish-sebelum.png>), [Koneksi tanpa kredensial ditolak](<evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/mqtt-tanpa-kredensial-ditolak.png>), [Akses topik kendali ditolak](<evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/mqtt-topik-terlarang-ditolak.png>), [Injeksi REST ditolak](<evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/suntik-data-rest-ditolak.png>).

### C2. Pengelolaan Kredensial Aman, Hak Akses Berkas Ketat, dan Rotasi Token - Done

- **Tujuan Pengamanan:** Mencegah kebocoran rahasia sistem dan memastikan berkas konfigurasi sensitif tidak terbaca pengguna non-privilese.
- **Kondisi Awal (Before):** `.env`, `mqtt.env`, dan `secrets/mqtt_users.json` bermode 644 sehingga terbaca pengguna lain. Token otentikasi default juga tertanam literal pada `app.py`.
- **Implementasi:** Konstanta token dihapus dari kode sumber dan dialihkan ke variabel lingkungan. Izin berkas konfigurasi diubah menjadi mode 600 dengan pemilik `smartcow`. Token API dan kredensial MQTT dirotasi memakai `openssl rand -hex 16`.
- **Hasil Verifikasi (After):** `ls -l` mengonfirmasi mode 600 pada seluruh berkas kredensial. Pencarian teks token pada kode program tidak menemukan nilai. Pembacaan berkas oleh pengguna `nobody` gagal. Permintaan dengan token lama ditolak `HTTP 401 Unauthorized`, sedangkan token baru dipakai sah oleh simulator.
- **Cakupan dan Batasan:** Kredensial operasional hanya berada di memori proses dan berkas konfigurasi lokal berizin ketat milik akun `smartcow`.
- **Tautan Bukti:** [Izin berkas sebelum dan sesudah](<evidence/kontrol C2 - Kredensial tidak hardcoded/izin-berkas-verifikasi-ulang.png>), [Status berkas dan izin setelah](<evidence/kontrol C2 - Kredensial tidak hardcoded/kredensial-setelah.png>). Tangkapan layar lama yang memuat nilai kredensial tidak dipakai.

### C3. Pencatatan Log Aktivitas, Prosedur Backup, dan Verifikasi Pemulihan Data - Done

- **Tujuan Pengamanan:** Menyimpan riwayat permintaan mencurigakan untuk audit dan memastikan integritas telemetri dapat dipulihkan setelah manipulasi data.
- **Kondisi Awal (Before):** Aplikasi dan broker belum mengonfigurasi berkas log akses khusus, dan belum tersedia skrip pencadangan maupun pemulihan lokal.
- **Implementasi:**
  - `SMARTCOW_LOG` diarahkan ke `logs/access.log` dan `SMARTCOW_MQTT_LOG` ke `logs/broker.log`. Parameter `auth` pada query string disanitasi menjadi `auth=REDACTED` sebelum ditulis.
  - `/usr/local/bin/smartcow-backup` dimiliki `root:root` mode 750 dan dijalankan unit systemd sebagai root, sehingga tidak dapat ditimpa proses tanpa privilese.
  - Skrip membekukan `data/` dengan `cp -a`, membuat arsip dan manifest sha256 dari salinan beku, menulis keluaran dengan akhiran `.part`, lalu mengganti nama setelah lengkap. Retensi tujuh arsip.
  - Arsip disimpan di `/var/lib/smartcow/backup` milik `root:root` mode 700, di luar `/home/smartcow-lab`, karena direktori di dalam home layanan dapat dihapus pengguna layanan. Hanya nama berpola `state-*.tar.gz` yang boleh dihapus, sehingga pengguna layanan tidak dapat memalsukan arsip atau menyisipkan nama berkas.
  - Penjadwalan memakai `smartcow-backup.timer` dengan `OnCalendar=daily` dan `Persistent=true`.
  - `/usr/local/bin/smartcow-restore` menjalankan urutan: verifikasi checksum arsip, penolakan arsip bersymlink, verifikasi manifest, hentikan `smartcow-api`/`smartcow-sim`, simpan `data.prev-<stempel>`, ekstrak data, perbaiki kepemilikan dan mode (berkas 600 karena `users.json` dan `state.json` memuat hash sandi serta token sesi), lalu nyalakan layanan. Kegagalan pada salah satu langkah memicu rollback otomatis.
- **Hasil Verifikasi (After):** Dijalankan ulang pada sesi verifikasi ulang. `smartcow-backup.service` selesai `Succeeded` dan menghasilkan `state-<stempel>-<pid>.tar.gz`; pemeriksaan pemulihan mencocokkan checksum arsip dan 4 dari 4 berkas pada manifest. Uji gerbang keamanan dengan manifest yang sengaja dirusak ditolak (exit 1, `isi arsip tidak cocok dengan manifest`) tanpa menyentuh `data/` dan tanpa menghentikan layanan. Pemulihan normal berhasil, menyisakan `data.prev-<stempel>`, dan `/health` membalas 200. Setelah skrip versi repositori dipasang, arsip lama dipindahkan ke `/var/lib/smartcow/backup`, pencadangan berikutnya `Succeeded`, dan `smartcow-restore-check` melaporkan `PASS archive-checksum` serta 4 dari 4 berkas cocok dengan manifest. Pengguna `smartcow` gagal menulis, membaca, maupun menghapus direktori arsip (`13-backup-relocation-and-deploy.log`).
- **Cakupan dan Batasan:** Log dikelola lokal pada Target Node; pengiriman terpusat ke SIEM dijadwalkan pada evaluasi tahap berikutnya. Skrip versi repositori memuat penguatan tambahan (arsip di luar home layanan, penolakan arsip bersymlink, berkas hasil pemulihan mode 600) yang sudah dipasang dan diuji pada sesi verifikasi ulang, sedangkan bukti `02` dan `07` berasal dari skrip yang berjalan lebih awal pada sesi yang sama. Berkas `backup-dan-pemulihan-data.png` sudah diganti tangkapan layar eksekusi nyata (unit backup `Succeeded`, `PASS archive-checksum`, `PASS manifest 4/4`); salinan lama yang menampilkan kegagalan `tar` tidak dipakai lagi.
- **Tautan Bukti:** [Backup dan restore C3](evidence/verifikasi-ulang/02-c3-backup-restore.log), [Status unit backup](evidence/verifikasi-ulang/07-backup-units-after.log), [Pemasangan dan pemindahan arsip](evidence/verifikasi-ulang/13-backup-relocation-and-deploy.log), [Redaksi log akses](evidence/verifikasi-ulang/12-target-redaction-and-env.log), [Backup dan pemulihan](<evidence/kontrol C3 - Logging aktivitas dan backup data/backup-dan-pemulihan-data.png>), [Baseline telemetri awal](<evidence/kontrol C3 - Logging aktivitas dan backup data/baseline-telemetry-simulator.png>).

---

## 6. Rencana Peningkatan dan Batasan Kontrol

- **Pembaruan paket sistem operasi:** `pacman -Syu` tidak dapat dijalankan karena isolasi jaringan tanpa internet. Sistem berjalan stabil dengan kernel Linux `5.10.14` bawaan citra laboratorium.
- **Fail2ban:** pemasangan paket memerlukan repositori daring; perannya digantikan aturan hashlimit iptables dan `MaxStartups` pada OpenSSH.
- **TLS:** komunikasi REST API dan MQTT pada segmen terisolasi memakai HTTP dan MQTT plaintext, merefleksikan arsitektur firmware asli yang mematikan verifikasi sertifikat.
- **Alert otomatis SIEM:** pengambilan bukti peringatan IDS dilakukan melalui antarmuka Sguil karena segmen antarmuka manajemen terisolasi.

## 7. Referensi Dokumen Terkait

- [Deklarasi Tech Stack Sistem IoT](../presentation-minggu9/tech_stack_declaration.md)
- [Rencana Pengujian Serangan Red Team](../redteam/attack_plan.md)
- [Logbook Purple Team Loop](../purple-team-log.md)
- [Skema Alokasi Pengalamatan IP](../design/ip_plan.md)
- [Vulnerability Assessment Report](../vulnerability-assessment-report.md)
- [Kronologi Logbook Proyek](../../LOGBOOK.md)
