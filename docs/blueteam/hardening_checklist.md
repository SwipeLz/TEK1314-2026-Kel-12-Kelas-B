# Checklist hardening keamanan - Target Node

**Kelompok 12 | TEK1314 - PBL Keamanan Siber | Checkpoint Minggu 9**

## 1. Tujuan dan ruang lingkup

Dokumen ini menyajikan sembilan kontrol hardening pada replika backend sistem
sprinkler kandang sapi. Kontrol dikelompokkan ke Access and Authentication,
Service and Attack Surface, serta Data and Application.

- Target: `SRV-IOT-KEL12-B`, Arch Linux, IP lab `192.168.12.5`.
- Perangkat penguji: `ATTACKER-KEL12-B` (`192.168.12.100`) dan host administrasi (`192.168.12.1`).
- Monitoring: `SOC-KEL12-B`, Security Onion, `192.168.12.200`.
- Layanan: SSH `22`, dashboard Nginx `80`, broker MQTT `1883`, API replika `9000`.
- Replika backend: aplikasi `smartcow-lab` di `/home/smartcow-lab`, dijalankan sebagai akun aplikasi `smartcow` lewat systemd.
- Device: `cow-sprinkler-01`, data sepenuhnya dummy.
- Dokumentasi bukti: tangkapan layar terminal asli di `docs/blueteam/evidence/`, ditautkan pada setiap kontrol.

Seluruh pengujian memakai data dummy di jaringan Host-Only. Ruang lingkup tidak
mencakup Firebase produksi, sensor fisik, maupun pengendalian pompa nyata.

### Kriteria status

- **Done**: kontrol diterapkan dan didukung bukti konfigurasi atau hasil pengujian sesuai lingkup verifikasi yang dijelaskan.
- **Partial**: implementasi atau verifikasi kontrol baru terpenuhi sebagian.
- **Not Yet**: kontrol belum diterapkan atau belum memiliki bukti verifikasi.

## 2. Ringkasan implementasi

| ID | Kategori | Kontrol | Hasil verifikasi |
| --- | --- | --- | --- |
| A1 | Access and Authentication | Menolak login root langsung melalui SSH | Konfigurasi efektif `permitrootlogin no`; seluruh percobaan login `root` ditolak. |
| A2 | Access and Authentication | Login berbasis kunci, autentikasi password dimatikan | Login kunci berhasil; login password ditolak dengan `Permission denied (publickey)`. |
| A3 | Access and Authentication | Membatasi percobaan login dan laju koneksi | `MaxStartups 3:50:10` plus aturan rate limit iptables; delapan koneksi paralel sebagian ditolak. |
| B1 | Service and Attack Surface | Firewall whitelist yang persisten | INPUT DROP; hanya 22, 80, dan 1883 dari segmen lab; aturan tersimpan dan termuat saat boot. |
| B2 | Service and Attack Surface | API replika hanya mendengarkan di loopback | Listener berubah dari `0.0.0.0:9000` menjadi `127.0.0.1:9000`; port 9000 tidak terjangkau dari jaringan. |
| B3 | Service and Attack Surface | Menyembunyikan versi Nginx | Header berubah dari `nginx/1.18.0` menjadi `nginx`; dashboard tetap HTTP 200. |
| C1 | Data and Application | Validasi input endpoint REST dan ACL topik MQTT | Kelembapan 150 ditolak HTTP 400; publish ke topik `control` ditolak; data sah tetap diterima. |
| C2 | Data and Application | Kredensial tidak hardcoded, permission ketat, rotasi | Berkas kredensial mode 600; literal token hilang dari kode; token lama ditolak. |
| C3 | Data and Application | Logging aktivitas, backup, dan uji pemulihan | Log akses dan log broker aktif; backup dan pemulihan data terverifikasi. |

**Rekapitulasi: 9 kontrol Done, 0 Partial, 0 Not Yet.** Komposisinya 3 kontrol kategori A,
3 kontrol kategori B, dan 3 kontrol kategori C, sehingga memenuhi minimal
delapan kontrol dengan sedikitnya dua pada setiap kategori. Status dinilai
berdasarkan bukti yang tersedia dan dibatasi oleh cakupan verifikasi masing-masing
kontrol. Status tersebut tidak menyatakan sistem aman untuk penggunaan produksi.

## 3. Kategori A - Access and Authentication

### A1. Menolak login root langsung melalui SSH - Done

- **Tujuan:** mencegah autentikasi SSH langsung memakai akun root, dan mempertahankan administrasi lewat akun pengguna berwenang.
- **Kondisi awal (Before):** file konfigurasi baseline Minggu 6 (`sshd_config.bak-kel12`) menunjukkan `PermitRootLogin without-password` dan `MaxAuthTries 6`. Fase 1 sudah mengubahnya menjadi `permitrootlogin no`, dan bukti sebelum untuk checkpoint ini adalah konfigurasi efektif serta file baseline itu.
- **Implementasi:** `PermitRootLogin no` dan `AllowUsers sec_admin` dipertahankan, lalu diverifikasi ulang dengan `sshd -T` dan percobaan login dari mesin penyerang.
- **Hasil verifikasi (After):** konfigurasi efektif menunjukkan `permitrootlogin no` dan `allowusers sec_admin`. Empat kombinasi login dari penyerang ditolak, termasuk dua percobaan dengan akun `root`.
- **Cakupan dan batasan:** kontrol ini menahan login langsung. Jalur `sudo` dari `sec_admin` tetap utuh, dan pematahan autentikasi password dilakukan pada A2.
- **Bukti:** [Konfigurasi efektif sebelum](<evidence/kontrol A1 - Menolak login root langsung/sshd-efektif-sebelum.png>), [konfigurasi efektif setelah](<evidence/kontrol A1 - Menolak login root langsung/sshd-efektif-setelah.png>), [percobaan login ditolak](<evidence/kontrol A1 - Menolak login root langsung/percobaan-login-root-ditolak.png>).

### A2. Login SSH berbasis kunci dan autentikasi password dimatikan - Done

- **Tujuan:** memastikan masuk ke Target Node hanya bisa lewat kunci publik, sehingga kata sandi yang bocor tidak langsung berarti akses.
- **Kondisi awal (Before):** `sshd -T` menunjukkan `passwordauthentication yes`, dan direktori `.ssh` belum berisi `authorized_keys`. Pada kondisi itu, `sec_admin` berhasil masuk dengan kata sandi lab.
- **Implementasi:** kunci ed25519 dibuat di host, kunci publik dipasang di `/home/sec_admin/.ssh/authorized_keys` dengan mode 600 dan pemilik `sec_admin`, lalu `PasswordAuthentication no` ditambahkan ke `sshd_config`. Konfigurasi diperiksa dengan `sshd -t` sebelum layanan dimuat ulang.
- **Hasil verifikasi (After):** login dengan kunci berhasil dan mengembalikan `SRV-IOT-KEL12-B`. Login memakai kata sandi ditolak dengan pesan `Permission denied (publickey)`.
- **Cakupan dan batasan:** satu kunci untuk satu akun lab, tanpa daftar pencabutan. Akses lewat konsol tetap tersedia sebagai jalur pemulihan.
- **Bukti:** [kunci publik terpasang](<evidence/kontrol A2 - Login SSH berbasis kunci/kunci-publik-terpasang.png>), [percobaan login password ditolak](<evidence/kontrol A2 - Login SSH berbasis kunci/percobaan-login-password-ditolak.png>).

### A3. Membatasi percobaan login dan laju koneksi - Done

- **Tujuan:** membatasi percobaan autentikasi berulang dan menekan laju koneksi baru dari mesin penyerang.
- **Kondisi awal (Before):** `MaxStartups 10:30:100` memakai nilai bawaan, dan firewall tidak punya aturan pembatas laju untuk port 22.
- **Implementasi:** `MaxStartups` diubah menjadi `3:50:10`, lalu satu aturan `hashlimit` dipasang di awal rantai INPUT: maksimal 3 koneksi baru per detik dari `192.168.12.100` dengan burst 6, sisanya ditolak dengan reset TCP. Aturan disimpan ke `/etc/iptables/iptables.rules` supaya tetap berlaku setelah reboot.
- **Hasil verifikasi (After):** delapan koneksi SSH paralel dari penyerang sebagian ditolak, dan `iptables -S` menampilkan aturan hashlimit tersebut. Setiap percobaan login tercatat di log sshd dengan `LogLevel VERBOSE`.
- **Cakupan dan batasan:** rate limit hanya berlaku untuk alamat penyerang. `MaxStartups` berlaku global, dan fail2ban tidak bisa dipasang karena lab tidak punya akses internet.
- **Bukti:** [aturan sshd dan firewall](<evidence/kontrol A3 - Pembatasan percobaan login/sshd-maxstartups-dan-rate-limit.png>), [uji koneksi paralel](<evidence/kontrol A3 - Pembatasan percobaan login/uji-koneksi-paralel-dari-penyerang.png>).

## 4. Kategori B - Service and Attack Surface

### B1. Firewall whitelist yang persisten - Done

- **Tujuan:** membatasi koneksi masuk hanya ke layanan dan sumber yang memang dipakai di lab.
- **Kondisi awal (Before):** pada pemeriksaan awal checkpoint ini, aturan sudah terpasang dari Fase 1, tetapi cara menyimpannya baru diperbaiki setelah kami menemukan tabel iptables kosong karena aturannya hilang setelah reboot. Bukti kondisi kosong itu ada di `docs/phase-1-baseline/evidence/iptables-before.log`.
- **Implementasi:** aturan INPUT diverifikasi ulang, lalu disimpan dengan `iptables-save` ke `/etc/iptables/iptables.rules`. Service `iptables.service` dipastikan aktif dan enabled. Aturan rate limit dari A3 ditambahkan di awal rantai.
- **Hasil verifikasi (After):** `iptables -S` menunjukkan policy INPUT DROP, izin untuk loopback, koneksi berstatus RELATED atau ESTABLISHED, ICMP dari `192.168.12.0/24`, dan TCP 22, 80, 1883 dari segmen yang sama. Pemindaian dari penyerang menemukan 22, 80, dan 1883 terbuka, sedangkan 9000, 21, 23, dan 3306 filtered. `systemctl is-enabled iptables.service` mengembalikan enabled.
- **Cakupan dan batasan:** firewall tidak mengatur lalu lintas keluar. Aturan yang hanya hidup di memori akan hilang setelah restart, dan kejadian itu pernah terjadi, sehingga penyimpanan permanen adalah bagian dari kontrol ini.
- **Bukti:** [aturan sebelum](<evidence/kontrol B1 - Firewall whitelist dan persisten/iptables-sebelum.png>), [aturan setelah](<evidence/kontrol B1 - Firewall whitelist dan persisten/iptables-setelah.png>), [pemindaian sebelum](<evidence/kontrol B1 - Firewall whitelist dan persisten/pemindaian-port-sebelum.png>), [pemindaian setelah](<evidence/kontrol B1 - Firewall whitelist dan persisten/pemindaian-port-setelah.png>).

### B2. API replika hanya mendengarkan di loopback - Done

- **Tujuan:** mengurangi paparan langsung penyimpanan data dari antarmuka jaringan Target Node.
- **Kondisi awal (Before):** `ss -lntp` menunjukkan API replika mendengarkan di `0.0.0.0:9000`, jadi bisa dijangkau dari mana saja selama firewall mengizinkan.
- **Implementasi:** variabel `SMARTCOW_BIND` diubah menjadi `127.0.0.1` di berkas `.env`, lalu service `smartcow-api` dimuat ulang. Nginx tetap menjadi satu-satunya pintu masuk dari jaringan.
- **Hasil verifikasi (After):** `ss -lntp` menunjukkan `127.0.0.1:9000`. Pemindaian dari penyerang tetap membaca port 9000 sebagai filtered, dan dashboard lewat Nginx tetap menjawab HTTP 200.
- **Cakupan dan batasan:** port 9000 terbaca filtered pada pemindaian sebelum dan sesudah, karena firewall memang tidak pernah mengizinkannya. Efek kontrol ini terlihat pada level listener, bukan dari hasil scan. Pembatasan loopback juga tidak menyentuh proses lokal yang sudah punya akses ke berkas data.
- **Bukti:** [listener sebelum](<evidence/kontrol B2 - API hanya mendengarkan di loopback/listener-sebelum.png>), [listener setelah](<evidence/kontrol B2 - API hanya mendengarkan di loopback/listener-setelah.png>), [pemindaian setelah](<evidence/kontrol B2 - API hanya mendengarkan di loopback/pemindaian-port-setelah.png>).

### B3. Menyembunyikan versi Nginx - Done

- **Tujuan:** mengurangi informasi versi perangkat lunak yang bocor lewat respons HTTP.
- **Kondisi awal (Before):** `curl -I http://127.0.0.1/` menjawab HTTP 200 dengan header `Server: nginx/1.18.0`. Direktif `server_tokens` tidak ada di `nginx.conf`.
- **Implementasi:** `server_tokens off;` ditambahkan di blok http pada `/etc/nginx/nginx.conf`, diperiksa dengan `nginx -t`, lalu Nginx dimuat ulang.
- **Hasil verifikasi (After):** header berubah menjadi `Server: nginx` tanpa nomor versi. Pemindaian dengan deteksi versi juga berhenti menyebut angka versi, dan halaman dashboard tetap menjawab HTTP 200.
- **Cakupan dan batasan:** nama produk Nginx masih terlihat. Halaman error dan tampilan peramban tidak diuji. Kontrol ini tidak menggantikan pembaruan keamanan.
- **Bukti:** [header sebelum](<evidence/kontrol B3 - Menyembunyikan versi Nginx/header-http-sebelum.png>), [header setelah](<evidence/kontrol B3 - Menyembunyikan versi Nginx/header-http-setelah.png>).

## 5. Kategori C - Data and Application

### C1. Validasi input endpoint REST dan ACL topik MQTT - Done

- **Tujuan:** membatasi nilai sensor yang boleh masuk dan topik yang boleh ditulis perangkat.
- **Kondisi awal (Before):** validasi dimatikan, sehingga `PUT` telemetri dengan kelembapan 150 dijawab HTTP 200 dan nilainya tersimpan. Broker menerima publish anonim ke topik `cow-sprinkler-01/control` dan meneruskannya.
- **Implementasi:** `SMARTCOW_VALIDATE` diaktifkan. Suhu dibatasi -20 sampai 70 derajat Celsius, kelembapan 0 sampai 100 persen, THI 0 sampai 130, seluruh field wajib harus ada, dan field asing ditolak. Pada broker, autentikasi diwajibkan lewat `SMARTCOW_MQTT_AUTH` dan ACL topik lewat `SMARTCOW_MQTT_ACL`, sehingga hanya `cow-sprinkler-01/telemetry/latest` yang boleh ditulis.
- **Hasil verifikasi (After):** kelembapan 150 dijawab HTTP 400 dengan pesan `h1 di luar rentang 0.0..100.0`. Penulisan tanpa token dijawab HTTP 401. Publish tanpa kredensial ditolak dengan CONNACK return code 5, dan publish ke topik `control` memakai kredensial sensor yang sah tetap ditolak. Penolakan tercatat di `broker.log`.
- **Cakupan dan batasan:** yang diuji adalah pola validasi replika, bukan rules Firebase RTDB asli. Panjang payload, wildcard topic, dan retained message belum diuji.
- **Bukti:** [validasi sebelum](<evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/validasi-input-sebelum.png>), [validasi setelah](<evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/validasi-input-setelah.png>), [publish sebelum](<evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/mqtt-publish-sebelum.png>), [publish tanpa kredensial ditolak](<evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/mqtt-tanpa-kredensial-ditolak.png>), [topik terlarang ditolak](<evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/mqtt-topik-terlarang-ditolak.png>), [suntik data ditolak](<evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/suntik-data-rest-ditolak.png>).

### C2. Kredensial tidak hardcoded, permission ketat, dan rotasi - Done

- **Tujuan:** mencegah kebocoran token dan memastikan berkas secret tidak bisa dibaca user lain.
- **Kondisi awal (Before):** berkas `.env`, `mqtt.env`, dan `secrets/mqtt_users.json` ber-mode 644, sehingga bisa dibaca user lain. Token API juga masih ada sebagai literal di dalam `app.py` pada baris `DEFAULT_TOKEN`, dan token itu bocor ke mesin penyerang saat fase sebelum hardening.
- **Implementasi:** literal token dihapus dari `app.py`, pembacaannya dipindah ke environment. Tiga berkas kredensial diubah ke mode 600 dengan pemilik `smartcow`. Token API dan sandi broker dirotasi dengan `openssl rand`, lalu service dimuat ulang.
- **Hasil verifikasi (After):** `ls -l` menunjukkan mode 600 untuk ketiga berkas, dan `grep` literal token di `app.py` mengembalikan nol. Percobaan membaca `.env` sebagai user `nobody` ditolak. Token lama yang bocor dijawab HTTP 401 dengan pesan `tulis butuh token valid`, sedangkan token baru dipakai simulator dan telemetri tetap mengalir.
- **Cakupan dan batasan:** secret masih tersimpan di environment file milik akun aplikasi dan di memori proses. Pada proyek asli, Database Secret tertanam di dalam sketch firmware, dan hal itu tidak bisa diperbaiki dari lab karena sistem mitra tidak boleh disentuh.
- **Bukti:** [kredensial sebelum](<evidence/kontrol C2 - Kredensial tidak hardcoded/kredensial-sebelum.png>), [kredensial setelah](<evidence/kontrol C2 - Kredensial tidak hardcoded/kredensial-setelah.png>).

### C3. Logging aktivitas, backup, dan uji pemulihan - Done

- **Tujuan:** menyimpan jejak permintaan yang mencurigakan, dan memastikan data simulasi bisa dipulihkan.
- **Kondisi awal (Before):** aplikasi tidak menulis log akses, broker tidak mencatat koneksi, dan tidak ada mekanisme backup. Storage journald sudah persistent sejak Fase 1.
- **Implementasi:** `SMARTCOW_LOG` diarahkan ke `logs/access.log` dan `SMARTCOW_MQTT_LOG` ke `logs/broker.log`. Skrip `/usr/local/bin/smartcow-backup` membuat arsip tar.gz mode 600 dari folder data. Uji pemulihan dijalankan dengan mengubah nilai telemetri menjadi 41 derajat dan kelembapan 90, lalu memulihkan arsip terbaru.
- **Hasil verifikasi (After):** `access.log` mencatat setiap permintaan, termasuk penolakan token dan payload di luar rentang. `broker.log` mencatat start broker, kredensial yang ditolak, dan publish yang diterima. Setelah pemulihan, `t1` kembali ke 29,5 dan `h1` ke 66, bukan 41 dan 90.
- **Cakupan dan batasan:** log aplikasi belum dikirim ke SIEM, karena antarmuka management Security Onion tidak bisa dijangkau dari host. Rotasi log belum diatur dan backup belum dijadwalkan. Cadangan masih tersimpan di VM yang sama, jadi belum melindungi dari kerusakan disk.
- **Bukti:** [baseline telemetri simulator](<evidence/kontrol C3 - Logging aktivitas dan backup data/baseline-telemetry-simulator.png>), [log akses aplikasi](<evidence/kontrol C3 - Logging aktivitas dan backup data/log-akses-aplikasi.png>), [backup dan pemulihan](<evidence/kontrol C3 - Logging aktivitas dan backup data/backup-dan-pemulihan-data.png>).

## 6. Yang belum dikerjakan

- **Pembaruan sistem operasi.** `pacman -Syu` tidak bisa jalan karena segmen lab tidak punya akses internet. Kernel yang dipakai masih 5.10.14 dari image lab.
- **Fail2ban.** Paket ini butuh internet untuk dipasang, jadi belum ada. Perannya digantikan rate limit iptables dan `MaxStartups`.
- **TLS.** API replika masih memakai HTTP. Pada proyek asli, firmware masih memakai `setInsecure()` yang mematikan verifikasi sertifikat.
- **Rules Firebase RTDB asli.** Tidak dievaluasi langsung. Yang diuji di lab adalah pola validasi dan aturan aksesnya.
- **Rotasi Database Secret pada firmware asli.** Di luar lingkup lab, karena sistem mitra tidak boleh disentuh.
- **Alert otomatis dari Security Onion.** Antarmuka management VM Onion tidak menjawab ARP dan VM itu tidak punya SSH server maupun Guest Additions, sehingga bukti alert diambil manual dari layar.

## 7. Dokumentasi terkait

- [Deklarasi tech stack](../presentation-minggu9/tech_stack_declaration.md)
- [Rencana serangan Red Team](../redteam/attack_plan.md)
- [Log Purple Team Loop](../purple-team-log.md)
- [Skema alokasi IP](../design/ip_plan.md)
- [Baseline Fase 1](../phase-1-baseline/baseline-report.md)
- [Sumber replika backend](../../scripts/smartcow-lab/README.md)

