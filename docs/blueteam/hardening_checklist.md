# Checklist Pengamanan (Hardening) - Target Node

**Kelompok 12 | TEK1314 - Praktik Keamanan Siber Terapan | Fase 2 (Minggu 9 - 11)**

## 1. Tujuan dan Ruang Lingkup

Dokumen ini menyajikan implementasi sembilan kontrol pengamanan (*hardening*) pada Target Node yang menjalankan replika backend sistem SmartCow (sistem sprinkler kandang sapi perah). Seluruh kontrol dikelompokkan secara terstruktur ke dalam tiga kategori utama sesuai standar Bagian VIII Panduan PBL: *Access and Authentication*, *Service and Attack Surface*, serta *Data and Application*.

- **Target Node:** `SRV-IOT-KEL12-B`, sistem operasi Arch Linux Security Workstation, alamat IP laboratorium `192.168.12.5`.
- **Perangkat Penguji:** `ATTACKER-KEL12-B` (`192.168.12.100`) dan host administrasi (`192.168.12.1`).
- **Monitoring Node:** `SOC-KEL12-B`, Security Onion, alamat IP `192.168.12.200`.
- **Layanan Aktif:** OpenSSH (port 22), web server Nginx (port 80), broker MQTT (port 1883), dan REST API internal (port 9000).
- **Replika Backend:** Modul aplikasi `smartcow-lab` pada `/home/smartcow-lab`, dijalankan di bawah akun sistem `smartcow` melalui unit layanan systemd.
- **Identitas Perangkat IoT:** `cow-sprinkler-01`, seluruh data yang diproses merupakan data sintetis (dummy).
- **Dokumentasi Bukti:** Tangkapan layar terminal asli tersimpan pada direktori `docs/blueteam/evidence/` dan ditautkan pada masing-masing kontrol terkait.

Seluruh pengujian dijalankan di dalam jaringan virtual lokal bertipe Host-Only. Ruang lingkup evaluasi laboratorium ini tidak melibatkan infrastruktur cloud Firebase produksi, sensor fisik, maupun pengendalian perangkat relay tegangan tinggi.

### Kriteria Status Verifikasi

- **Done:** Kontrol telah diterapkan secara penuh dan diverifikasi melalui bukti konfigurasi teknis maupun hasil pengujian operasional.
- **Partial:** Penerapan atau verifikasi kontrol baru terpenuhi pada sebagian aspek.
- **Not Yet:** Kontrol belum diterapkan atau belum dilengkapi dengan bukti verifikasi teknis.

## 2. Ringkasan Hasil Implementasi Kontrol

| ID | Kategori Pengamanan | Rincian Kontrol | Hasil Verifikasi Teknis | Status |
| :--- | :--- | :--- | :--- | :--- |
| **A1** | Access & Authentication | Penolakan login langsung akun root melalui SSH | Parameter konfigurasi efektif `PermitRootLogin no`; seluruh upaya autentikasi user root ditolak sistem. | Done |
| **A2** | Access & Authentication | Autentikasi SSH berbasis kunci kriptografis dan penonaktifan kata sandi | Login menggunakan pasangan kunci Ed25519 berhasil; percobaan login berbasis kata sandi ditolak dengan respon `Permission denied (publickey)`. | Done |
| **A3** | Access & Authentication | Pembatasan sesi login konkuren dan pembatasan laju koneksi | Parameter `MaxStartups 3:50:10` aktif dan aturan rate limit iptables diterapkan; koneksi paralel berlebih berhasil diredam. | Done |
| **B1** | Service & Attack Surface | Konfigurasi firewall iptables whitelist yang persisten | Kebijakan default INPUT DROP; hanya port 22, 80, dan 1883 yang diizinkan dari subnet lab; aturan tersimpan permanen pada disk. | Done |
| **B2** | Service & Attack Surface | Isolasi REST API internal pada antarmuka loopback | Konfigurasi listener berubah dari `0.0.0.0:9000` menjadi `127.0.0.1:9000`; port 9000 tidak dapat dijangkau dari luar Target Node. | Done |
| **B3** | Service & Attack Surface | Penyembunyian identitas dan nomor versi web server Nginx | Header HTTP berubah dari `nginx/1.18.0` menjadi `Server: nginx`; web dashboard tetap dapat diakses dengan kode HTTP 200. | Done |
| **C1** | Data & Application | Validasi batasan input REST API dan pembatasan hak topik MQTT (*ACL*) | Nilai kelembapan 150% ditolak dengan respon HTTP 400; publikasi pesan ke topik kontrol ditolak broker; data sah tetap diterima. | Done |
| **C2** | Data & Application | Pengelolaan kredensial aman, izin berkas ketat, dan rotasi token | Berkas kredensial disetel ke mode 600; token akses dipindahkan ke environment variable; token lama berhasil dinonaktifkan. | Done |
| **C3** | Data & Application | Pencatatan log aktivitas, prosedur backup, dan uji pemulihan data | Berkas log akses aplikasi dan broker aktif; skrip backup otomatis dan verifikasi pemulihan data berhasil diuji. | Done |

**Rekapitulasi: 9 Kontrol Berstatus Done (0 Partial, 0 Not Yet).** Komposisi kontrol terdiri dari 3 kontrol Kategori A, 3 kontrol Kategori B, dan 3 kontrol Kategori C. Jumlah ini memenuhi ketentuan minimal delapan kontrol dengan sedikitnya dua kontrol pada tiap kategori sesuai standar evaluasi Bagian VIII Panduan PBL. Status dievaluasi berdasarkan bukti pengujian langsung di laboratorium dan dibatasi oleh ruang lingkup simulasi.

---

## 3. Kategori A - Access and Authentication

### A1. Penolakan Login Langsung Akun Root Melalui SSH - Done

- **Tujuan Pengamanan:** Mencegah upaya pengambilalihan hak akses tertinggi secara langsung via SSH serta memastikan seluruh aktivitas administratif dilakukan melalui akun pengguna khusus yang terdaftar.
- **Kondisi Awal (Before):** Berkas konfigurasi baseline Minggu 6 (`sshd_config.bak-kel12`) memuat konfigurasi `PermitRootLogin without-password` dan batas percobaan login default yang longgar.
- **Implementasi:** Parameter `PermitRootLogin no` dan `AllowUsers sec_admin` diterapkan pada konfigurasi sshd, divalidasi sintaksnya menggunakan perintah `sshd -t`, dan diverifikasi efektivitasnya melalui simulasi login dari Attacker Node.
- **Hasil Verifikasi (After):** Keluaran konfigurasi efektif `sshd -T` mengonfirmasi nilai `permitrootlogin no` dan `allowusers sec_admin`. Empat variasi percobaan login langsung dengan akun root dari penyerang seluruhnya ditolak oleh sistem.
- **Cakupan dan Batasan:** Kontrol ini berfokus pada proteksi akses SSH remote. Hak administratif di dalam server tetap dapat diakses oleh user `sec_admin` melalui perintah `sudo`.
- **Tautan Bukti:** [Konfigurasi sebelum](<evidence/kontrol A1 - Menolak login root langsung/sshd-efektif-sebelum.png>), [Konfigurasi setelah](<evidence/kontrol A1 - Menolak login root langsung/sshd-efektif-setelah.png>), [Percobaan login ditolak](<evidence/kontrol A1 - Menolak login root langsung/percobaan-login-root-ditolak.png>).

### A2. Autentikasi SSH Berbasis Kunci dan Penonaktifan Kata Sandi - Done

- **Tujuan Pengamanan:** Memastikan akses terminal ke Target Node hanya dapat dilakukan menggunakan kunci kriptografis yang valid, sehingga kebocoran kata sandi tidak dapat dimanfaatkan penyerang untuk memperoleh shell interaktif.
- **Kondisi Awal (Before):** Pengujian `sshd -T` awal menampilkan `passwordauthentication yes` dan direktori `.ssh` pada akun pengguna belum memiliki berkas `authorized_keys`. Pada tahap ini, user `sec_admin` berhasil login menggunakan kata sandi sederhana.
- **Implementasi:** Pasangan kunci Ed25519 dibangkitkan pada host administrasi, kunci publik dipasang pada `/home/sec_admin/.ssh/authorized_keys` dengan mode izin 600 dan kepemilikan `sec_admin`, kemudian direktif `PasswordAuthentication no` diaktifkan pada berkas konfigurasi SSH.
- **Hasil Verifikasi (After):** Autentikasi SSH menggunakan kunci privat berhasil menghubungkan sesi ke hostname `SRV-IOT-KEL12-B`. Sementara itu, seluruh upaya login berbasis kata sandi langsung digagalkan dengan pesan error `Permission denied (publickey)`.
- **Cakupan dan Batasan:** Implementasi menggunakan satu pasangan kunci untuk akun administratif lab. Akses langsung melalui konsol virtual tetap dapat digunakan sebagai jalur pemulihan darurat jika diperlukan.
- **Tautan Bukti:** [Pemasangan kunci publik](<evidence/kontrol A2 - Login SSH berbasis kunci/kunci-publik-terpasang.png>), [Penolakan login kata sandi](<evidence/kontrol A2 - Login SSH berbasis kunci/percobaan-login-password-ditolak.png>).

### A3. Pembatasan Percobaan Login dan Laju Koneksi SSH - Done

- **Tujuan Pengamanan:** Membatasi frekuensi percobaan otentikasi bertubi-tubi dan meredam laju koneksi jaringan baru yang berasal dari alamat IP penyerang.
- **Kondisi Awal (Before):** Parameter koneksi awal menggunakan nilai bawaan `MaxStartups 10:30:100` dan firewall belum dilengkapi aturan pembatasan laju paket pada port 22.
- **Implementasi:** Parameter `MaxStartups` diperketat menjadi `3:50:10`, lalu ditambahkan aturan modul `hashlimit` pada iptables: membatasi maksimal 3 koneksi baru per detik dari host `192.168.12.100` dengan toleransi *burst* 6 paket, serta mengembalikan respon TCP RST untuk paket selebihnya. Aturan disimpan permanen ke berkas `/etc/iptables/iptables.rules`.
- **Hasil Verifikasi (After):** Saat penyerang meluncurkan 8 sesi koneksi SSH paralel secara serentak, sebagian besar koneksi langsung digagalkan oleh firewall. Seluruh percobaan tercatat secara terperinci pada log sistem berkat opsi `LogLevel VERBOSE`.
- **Cakupan dan Batasan:** Pembatasan laju koneksi iptables difokuskan pada alamat IP penyerang lab, sedangkan parameter `MaxStartups` berlaku untuk seluruh sesi yang belum terotentikasi.
- **Tautan Bukti:** [Konfigurasi sshd dan iptables](<evidence/kontrol A3 - Pembatasan percobaan login/sshd-maxstartups-dan-rate-limit.png>), [Hasil uji koneksi paralel](<evidence/kontrol A3 - Pembatasan percobaan login/uji-koneksi-paralel-dari-penyerang.png>).

---

## 4. Kategori B - Service and Attack Surface

### B1. Konfigurasi Firewall Whitelist yang Persisten - Done

- **Tujuan Pengamanan:** Membatasi seluruh lalu lintas paket masuk hanya untuk layanan yang benar-benar dibutuhkan serta membatasi sumber akses pada subnet laboratorium.
- **Kondisi Awal (Before):** Pada tahap awal pengujian, tabel iptables sempat ditemukan dalam kondisi kosong dengan kebijakan default ACCEPT akibat konfigurasi yang belum tersimpan ke media penyimpanan permanen setelah mesin virtual direstart.
- **Implementasi:** Kebijakan default INPUT disetel ke DROP. Diberikan izin untuk antarmuka loopback, paket berstatus RELATED/ESTABLISHED, protokol ICMP dari subnet lab, serta port layanan 22 (SSH), 80 (HTTP), dan 1883 (MQTT). Konfigurasi diekspor menggunakan `iptables-save` ke `/etc/iptables/iptables.rules` dan layanan `iptables.service` diaktifkan saat boot.
- **Hasil Verifikasi (After):** Perintah `iptables -S` menampilkan seluruh rantai aturan aktif. Pemindaian port Nmap dari Attacker Node mengonfirmasi bahwa port 22, 80, dan 1883 berstatus terbuka (*open*), sedangkan port 9000, 21, 23, dan 3306 berstatus tertutup/difilter (*filtered*). Status `iptables.service` terkonfirmasi `enabled`.
- **Cakupan dan Batasan:** Konfigurasi firewall memprioritaskan penyaringan pada paket masuk (INPUT). Penyimpanan permanen ke dalam berkas konfigurasi menjamin aturan keamanan tetap aktif setelah sistem dinyalakan ulang.
- **Tautan Bukti:** [Aturan firewall sebelum](<evidence/kontrol B1 - Firewall whitelist dan persisten/iptables-sebelum.png>), [Aturan firewall setelah](<evidence/kontrol B1 - Firewall whitelist dan persisten/iptables-setelah.png>), [Pemindaian port sebelum](<evidence/kontrol B1 - Firewall whitelist dan persisten/pemindaian-port-sebelum.png>), [Pemindaian port setelah](<evidence/kontrol B1 - Firewall whitelist dan persisten/pemindaian-port-setelah.png>).

### B2. Isolasi REST API Internal pada Antarmuka Loopback - Done

- **Tujuan Pengamanan:** Menghilangkan eksposur langsung antarmuka penyimpanan data backend dari segmen jaringan eksternal.
- **Kondisi Awal (Before):** Pemeriksaan `ss -lntp` awal menunjukkan REST API mendengarkan pada alamat wildcard `0.0.0.0:9000`, sehingga dapat diakses langsung oleh perangkat lain di jaringan apabila aturan firewall tidak aktif.
- **Implementasi:** Parameter konfigurasi `SMARTCOW_BIND` pada berkas `.env` diubah menjadi `127.0.0.1`, kemudian layanan systemd `smartcow-api` dimuat ulang. Akses eksternal diarahkan secara terpusat melalui Nginx reverse proxy.
- **Hasil Verifikasi (After):** Status listener pada `ss -lntp` terbukti terikat secara eksklusif pada `127.0.0.1:9000`. Hasil pemindaian dari mesin penyerang memastikan port 9000 tidak dapat dihubungi dari jaringan luar, sementara dashboard web tetap dapat berkomunikasi dengan API melalui proxy lokal.
- **Cakupan dan Batasan:** Penerapan kontrol ini memperkuat arsitektur pertahanan berlapis pada tingkat soket aplikasi, melengkapi aturan penyaringan port pada tingkat paket firewall.
- **Tautan Bukti:** [Status listener sebelum](<evidence/kontrol B2 - API hanya mendengarkan di loopback/listener-sebelum.png>), [Status listener setelah](<evidence/kontrol B2 - API hanya mendengarkan di loopback/listener-setelah.png>), [Hasil pemindaian Nmap](<evidence/kontrol B2 - API hanya mendengarkan di loopback/pemindaian-port-setelah.png>).

### B3. Penyembunyian Identitas dan Versi Web Server Nginx - Done

- **Tujuan Pengamanan:** Mengurangi visibilitas informasi teknis perangkat lunak web server guna mempersempit peluang pencarian celah kerentanan spesifik versi (*fingerprinting*).
- **Kondisi Awal (Before):** Permintaan HTTP `curl -I http://127.0.0.1/` menghasilkan header respon `Server: nginx/1.18.0`. Direktif `server_tokens` belum didefinisikan pada konfigurasi Nginx.
- **Implementasi:** Parameter `server_tokens off;` ditambahkan ke dalam blok `http` pada berkas `/etc/nginx/nginx.conf`, diverifikasi dengan `nginx -t`, dan konfigurasi web server dimuat ulang.
- **Hasil Verifikasi (After):** Header HTTP respon Nginx berhasil disederhanakan menjadi `Server: nginx` tanpa menyertakan nomor versi. Pemindaian Nmap dengan opsi deteksi versi juga tidak lagi menampilkan rilis perangkat lunak, sementara antarmuka dashboard tetap beroperasi normal (HTTP 200).
- **Cakupan dan Batasan:** Kontrol ini bertujuan untuk menyembunyikan informasi versi publik dan tidak menggantikan kewajiban pembaruan keamanan perangkat lunak secara berkala.
- **Tautan Bukti:** [Header HTTP sebelum](<evidence/kontrol B3 - Menyembunyikan versi Nginx/header-http-sebelum.png>), [Header HTTP setelah](<evidence/kontrol B3 - Menyembunyikan versi Nginx/header-http-setelah.png>).

---

## 5. Kategori C - Data and Application

### C1. Validasi Batasan Input REST API dan Pembatasan Hak Topik MQTT (ACL) - Done

- **Tujuan Pengamanan:** Mencegah manipulasi data telemetri yang tidak logis serta membatasi izin publikasi pesan hanya pada kanal topik yang sah bagi masing-masing perangkat.
- **Kondisi Awal (Before):** Fitur validasi backend belum aktif sehingga request `PUT` dengan kelembapan 150% tetap diterima (HTTP 200). Broker MQTT juga menerima koneksi dari klien anonim serta meneruskan pesan ke topik kendali pompa (`cow-sprinkler-01/control`).
- **Implementasi:** Opsi `SMARTCOW_VALIDATE` diaktifkan pada backend: parameter suhu dibatasi pada rentang -20 hingga 70 derajat Celcius, kelembapan 0 hingga 100%, THI 0 hingga 130, serta mewajibkan seluruh field telemetri dasar. Pada broker MQTT, otentikasi wajib diaktifkan (`SMARTCOW_MQTT_AUTH`) dan pembatasan hak topik (`SMARTCOW_MQTT_ACL`) diterapkan sehingga kredensial sensor hanya memiliki hak tulis pada topik telemetri (`cow-sprinkler-01/telemetry/latest`).
- **Hasil Verifikasi (After):** Pengujian operasional memvalidasi skenario positif dan negatif: akun sensor (`esp32`) berhasil mengirim data ke `cow-sprinkler-01/telemetry/latest` (`CONNACK rc=0`), namun saat mengirim ke topik kendali `cow-sprinkler-01/control`, koneksi langsung diputus oleh broker sesuai aturan ACL dan tercatat pada `logs/broker.log`. Klien anonim ditolak dengan `CONNACK return code 5`, dan injeksi nilai kelembapan 150% pada REST API ditolak dengan respons `HTTP 400 Bad Request`.
- **Cakupan dan Batasan:** Pengujian difokuskan pada aturan verifikasi logika data dan otorisasi kanal komunikasi IoT pada lingkungan simulasi laboratorium.
- **Tautan Bukti:** [Validasi sebelum](<evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/validasi-input-sebelum.png>), [Validasi setelah](<evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/validasi-input-setelah.png>), [Publish MQTT sebelum](<evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/mqtt-publish-sebelum.png>), [Penolakan koneksi tanpa kredensial](<evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/mqtt-tanpa-kredensial-ditolak.png>), [Penolakan akses topik kendali](<evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/mqtt-topik-terlarang-ditolak.png>), [Penolakan injeksi REST](<evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/suntik-data-rest-ditolak.png>).

### C2. Pengelolaan Kredensial Aman, Hak Akses Berkas Ketat, dan Rotasi Token - Done

- **Tujuan Pengamanan:** Mencegah kebocoran rahasia sistem (*secrets*) dan memastikan berkas konfigurasi sensitif tidak dapat dibaca oleh pengguna non-privilese.
- **Kondisi Awal (Before):** Berkas `.env`, `mqtt.env`, dan `secrets/mqtt_users.json` memiliki hak akses mode 644 sehingga dapat dibaca oleh user lain di dalam sistem operasi. Token otentikasi default juga sempat tertanam secara literal di dalam kode program `app.py`.
- **Implementasi:** Seluruh konstanta token dihapus dari kode sumber `app.py` dan dialihkan ke pembacaan variabel lingkungan (*environment variables*). Hak akses berkas konfigurasi diubah menjadi mode 600 di bawah kepemilikan user sistem `smartcow`. Token otentikasi API dan kredensial akun MQTT dirotasi menggunakan pembangkit nilai acak kriptografis `openssl rand -hex 16`.
- **Hasil Verifikasi (After):** Perintah `ls -l` mengonfirmasi izin berkas 600 untuk seluruh berkas kredensial. Pencarian teks token di dalam kode program menghasilkan nilai nihil. Percobaan pembacaan berkas kredensial oleh pengguna non-privilese (`nobody`) digagalkan sistem. Permintaan API yang menyertakan token lama ditolak dengan pesan `HTTP 401 Unauthorized`, sementara token baru digunakan secara sah oleh simulator telemetri.
- **Cakupan dan Batasan:** Kredensial operasional tersimpan secara aman pada memori proses dan berkas konfigurasi lokal berizin ketat milik akun layanan `smartcow`.
- **Tautan Bukti:** [Status berkas sebelum](<evidence/kontrol C2 - Kredensial tidak hardcoded/kredensial-sebelum.png>), [Status berkas dan izin setelah](<evidence/kontrol C2 - Kredensial tidak hardcoded/kredensial-setelah.png>).

### C3. Pencatatan Log Aktivitas, Prosedur Backup, dan Verifikasi Pemulihan Data - Done

- **Tujuan Pengamanan:** Menyimpan riwayat permintaan yang mencurigakan untuk keperluan audit forensik serta memastikan integritas data telemetri dapat dipulihkan jika terjadi manipulasi data.
- **Kondisi Awal (Before):** Layanan aplikasi backend dan broker MQTT belum mengonfigurasi berkas log akses khusus, serta belum tersedia skrip pencadangan dan pemulihan data lokal.
- **Implementasi:** Parameter `SMARTCOW_LOG` diarahkan ke berkas `logs/access.log` dan `SMARTCOW_MQTT_LOG` ke `logs/broker.log`. Nilai parameter otentikasi `auth` pada query string disanitasi secara otomatis menjadi `auth=REDACTED` pada log akses guna mencegah kebocoran token pada berkas log. Dibuat skrip pencadangan `/usr/local/bin/smartcow-backup` dan skrip pemulihan `/usr/local/bin/smartcow-restore` berizin 750 milik `smartcow`.
- **Hasil Verifikasi (After):** Berkas `access.log` merekam riwayat request HTTP dengan token tersensor. Berkas `broker.log` mencatat inisialisasi broker dan penolakan koneksi ilegal. Prosedur pemulihan diverifikasi melalui simulasi kerusakan basis data: berkas data sengaja dikosongkan (hash sha256 berubah menjadi `e3b0c442...`), kemudian skrip restore dijalankan. Hash sha256 berkas setelah pemulihan terbukti cocok 100% dengan kondisi sebelum manipulasi (`d66f76c894af5e76579119d283e05bbc6c006266273e8881b59c285cd8be610f`).
- **Cakupan dan Batasan:** Berkas log dikelola secara lokal pada Target Node. Pengiriman log terpusat ke SIEM dijadwalkan pada evaluasi arsitektur tahap berikutnya.
- **Tautan Bukti:** [Baseline telemetri awal](<evidence/kontrol C3 - Logging aktivitas dan backup data/baseline-telemetry-simulator.png>), [Catatan log akses aplikasi](<evidence/kontrol C3 - Logging aktivitas dan backup data/log-akses-aplikasi.png>), [Hasil pengujian backup dan restore](<evidence/kontrol C3 - Logging aktivitas dan backup data/backup-dan-pemulihan-data.png>).

---

## 6. Rencana Peningkatan dan Batasan Kontrol

- **Pembaruan Paket Sistem Operasi:** Perintah `pacman -Syu` tidak dapat dieksekusi pada lingkungan lab karena isolasi jaringan tanpa akses internet publik. Sistem beroperasi stabil menggunakan kernel Linux 5.10.14 bawaan citra laboratorium.
- **Implementasi Layanan Fail2ban:** Pemasangan paket fail2ban memerlukan repositori daring; peran perlindungan terhadap serangan brute force digantikan secara efektif oleh aturan *hashlimit* iptables dan direktif `MaxStartups` pada OpenSSH.
- **Enkripsi Transmisi Transport Layer Security (TLS):** Komunikasi REST API dan MQTT pada segmen lab terisolasi beroperasi menggunakan protokol standar (HTTP dan MQTT plaintext), merefleksikan arsitektur firmware asli yang mematikan verifikasi sertifikat.
- **Integrasi Alert Otomatis SIEM:** Pengambilan bukti peringatan IDS dilakukan melalui antarmuka visual Sguil pada Security Onion karena isolasi segmen antarmuka manajemen.

## 7. Referensi Dokumen Terkait

- [Deklarasi Tech Stack Sistem IoT](../presentation-minggu9/tech_stack_declaration.md)
- [Rencana Pengujian Serangan Red Team](../redteam/attack_plan.md)
- [Logbook Purple Team Loop](../purple-team-log.md)
- [Skema Alokasi Pengalamatan IP](../design/ip_plan.md)
- [Kronologi Logbook Proyek](../../LOGBOOK.md)
