# Logbook Purple Team - Kelompok 12

Logbook ini mengikuti siklus lima tahap evaluasi keamanan pada Bagian X Panduan PBL. Prinsip utamanya: skenario yang berhasil menembus sistem pada Tahap 1 (sebelum pengamanan) harus dapat dicegah atau dimitigasi secara terverifikasi pada Tahap 5 (sesudah hardening).

Status per 12 November 2026: keempat skenario memiliki bukti tangkapan layar dan log. RT-02 diuji ulang melalui jendela demonstrasi terkontrol (kata sandi diaktifkan sementara lalu dipulihkan pada hari yang sama). RT-04 diuji ulang dengan membandingkan broker sebelum dan sesudah anti-replay stempel waktu. Alert kustom Sguil tercatat sebagai CID 6125 dan 6127 (26 Oktober 2026) serta CID 6352 dan 6356 (12 November 2026).

*Catatan stempel waktu:* basis data Sguil menyimpan waktu kejadian dalam GMT (UTC), sedangkan catatan aktivitas kelompok memakai WIB (UTC+7). Selisihnya 7 jam; contohnya rekaman 06:30 GMT setara 13:30 WIB.

**Konvensi bukti pada tabel:** bukti Red Team ditulis relatif terhadap `docs/redteam/evidence/`, bukti Blue Team relatif terhadap `docs/blueteam/evidence/`, dan bukti kontrol memakai singkatan `kontrol <ID>/...`. Berkas kode mengacu pada `scripts/smartcow-lab/`.

Peta folder kontrol: A1 `kontrol A1 - Menolak login root langsung`, A2 `kontrol A2 - Login SSH berbasis kunci`, A3 `kontrol A3 - Pembatasan percobaan login`, B1 `kontrol B1 - Firewall whitelist dan persisten`, B2 `kontrol B2 - API hanya mendengarkan di loopback`, B3 `kontrol B3 - Menyembunyikan versi Nginx`, C1 `kontrol C1 - Validasi input API dan ACL topik MQTT`, C2 `kontrol C2 - Kredensial tidak hardcoded`, C3 `kontrol C3 - Logging aktivitas dan backup data`.

## Daftar Isi

- [Skenario 1 - RT-01 Pemetaan Layanan dan Banner Jaringan](#skenario-1---rt-01-pemetaan-layanan-dan-banner-jaringan)
- [Skenario 2 - RT-02 Pengujian Autentikasi dan Pembatasan Sesi SSH](#skenario-2---rt-02-pengujian-autentikasi-dan-pembatasan-sesi-ssh)
- [Skenario 3 - RT-03 Injeksi Data REST dan Publish Ilegal MQTT](#skenario-3---rt-03-injeksi-data-rest-dan-publish-ilegal-mqtt)
- [Skenario 4 - RT-04 Pengujian Serangan Pengulangan Pesan Kendali](#skenario-4---rt-04-pengujian-serangan-pengulangan-pesan-kendali)
- [Catatan Validitas Artefak](#catatan-validitas-artefak)
- [Catatan Evaluasi dan Temuan Monitoring](#catatan-evaluasi-dan-temuan-monitoring)

## Skenario 1 - RT-01 Pemetaan Layanan dan Banner Jaringan

| Tahap | Aktivitas Red Team | Aktivitas Blue Team | Bukti | Hasil Pengamatan |
| :--- | :--- | :--- | :--- | :--- |
| **1. Serang** | Menjalankan `nmap -sS -sV -O` ke `192.168.12.5` untuk seluruh port TCP | Memantau lonjakan paket pada antarmuka sensor | `01-pemindaian-port-sebelum.png` | Port 22, 80, dan 1883 terbuka; port 9000 filtered |
| **2. Deteksi** | Mempersiapkan tahap eksploitasi | Membandingkan hasil pemindaian dengan listener aktif dan alert Sguil | `01-pemindaian-port-sebelum.png`, `12-alert-sguil-terdeteksi.png`, `verifikasi-2026-11-12/09-sguil-alerts.log` | Alert `ET SCAN Nmap` (SID 2009358 dan 2024364) tercatat dari `.100` ke port 80; CID diverifikasi lewat query |
| **3. Analisis** | Memetakan port aktif, versi layanan, dan sistem operasi untuk target lanjutan | Mengidentifikasi API backend yang mendengarkan di `0.0.0.0` dan hanya dilindungi satu lapis firewall | Catatan evaluasi internal | Pertahanan perimeter tunggal berisiko bila aturan firewall gagal |
| **4. Respons** | Tidak ada tindakan ofensif | Mengikat REST API ke `127.0.0.1` dan menambahkan `server_tokens off` | `kontrol B2/listener-setelah.png` | Listener berubah dari `0.0.0.0:9000` ke `127.0.0.1:9000` |
| **5. Verifikasi** | Mengulang pemindaian menyeluruh | Memastikan port 9000 tetap tidak terjangkau dan mempersempit whitelist MQTT ke loopback | `02-pemindaian-port-setelah.png`, `11-pemindaian-port-lengkap.png`, `13-pemindaian-port-mqtt-sebelum.png`, `14-pemindaian-port-mqtt-setelah.png` | Scan `-p-` 12 November 2026 hanya menemukan 22 dan 80 terbuka (65533 port lain filtered) |

Catatan bukti:

- Rilis yang terdeteksi pada kondisi awal: OpenSSH 8.4 dan Nginx 1.18.0.
- Keterhubungan Attacker Node ke Target Node sebelum pengujian dicatat pada `ping-attacker-target.log` (0% packet loss).
- Port 9000 terdeteksi filtered karena firewall memblokir paket masuk.
- Tangkapan Sguil menampilkan antrean alert yang sama-sama aktif, yaitu SMARTCOW-HTTP, SMARTCOW-MQTT, dan `ET SCAN Potential SSH Scan`. Nomor CID alert Nmap tidak terlihat pada layar, sehingga dibuktikan melalui query basis data.
- Sebelum penutupan 1883, Attacker Node mencatat tiga port terbuka (22, 80, 1883); sesudah B4 tinggal dua.
- Nginx tetap membalas tanpa nomor versi.

## Skenario 2 - RT-02 Pengujian Autentikasi dan Pembatasan Sesi SSH

| Tahap | Aktivitas Red Team | Aktivitas Blue Team | Bukti | Hasil Pengamatan |
| :--- | :--- | :--- | :--- | :--- |
| **1. Serang** | Menjalankan `ssh_try.py` dengan kombinasi akun `root` dan `sec_admin` | Memantau log autentikasi pada Target Node | `03-percobaan-login-sebelum.png` | `sec_admin` BERHASIL, `root` GAGAL karena `PermitRootLogin no` |
| **2. Deteksi** | Melanjutkan percobaan login berkala | Memeriksa log sshd dengan `LogLevel VERBOSE` dan alert Sguil | `kontrol A1/sshd-efektif-sebelum.png`, `sguil-alert-minggu9.png` | Percobaan login tercatat pada log; Snort membangkitkan `ET SCAN Potential SSH Scan` pada port 22 |
| **3. Analisis** | Memvalidasi dampak kebocoran kata sandi administratif | Menemukan akar masalah: autentikasi kata sandi aktif, batas percobaan longgar, belum ada pembatasan laju | Catatan evaluasi internal | Kebocoran kata sandi langsung dapat dieksploitasi tanpa kontrol tambahan |
| **4. Respons** | Tidak ada tindakan ofensif | Memasang kunci Ed25519, mematikan `PasswordAuthentication`, memperketat `MaxStartups`, memasang hashlimit iptables | `kontrol A2/kunci-publik-terpasang.png`, `kontrol A3/sshd-maxstartups-dan-rate-limit.png` | `PasswordAuthentication no` dan `MaxStartups 3:50:10` aktif; maksimal 3 koneksi baru per detik dari host penyerang |
| **5. Verifikasi** | Mengulang percobaan login dan membuka 8 koneksi SSH paralel | Memverifikasi konfigurasi pulih dan seluruh login kata sandi ditolak | `04-percobaan-login-setelah.png`, `10-uji-rate-limit-koneksi.png`, `verifikasi-2026-11-12/08-password-login-rejected.log`, `kontrol A2/login-kunci-berhasil.png` | Kedua akun dibalas `Permission denied (publickey)`; login kunci berhasil; sebagian koneksi paralel dibatalkan firewall |

Catatan bukti:

- Pada jendela demonstrasi terkontrol, `PasswordAuthentication` dikembalikan sementara ke nilai bawaan setelah cadangan dibuat. Kata sandi disamarkan skrip (`***`) agar tidak tercetak pada tangkapan layar.
- Konfigurasi dipulihkan pada hari yang sama dan diverifikasi dengan `sshd -T`: `PasswordAuthentication no`, `PermitRootLogin no`, `MaxStartups 3:50:10`.

## Skenario 3 - RT-03 Injeksi Data REST dan Publish Ilegal MQTT

| Tahap | Aktivitas Red Team | Aktivitas Blue Team | Bukti | Hasil Pengamatan |
| :--- | :--- | :--- | :--- | :--- |
| **1. Serang** | Mempublikasikan payload ke `cow-sprinkler-01/control` tanpa kredensial dan mengirim `PUT` telemetri kelembapan 150% | Memeriksa log aplikasi dan broker | `05-publish-mqtt-sebelum.png`, `08-suntik-telemetri-rest-sebelum.png` | Pesan MQTT diterima broker, telemetri palsu tersimpan, perintah sprinkler manual diterima |
| **2. Deteksi** | Melanjutkan pengujian transmisi data | Memantau `logs/access.log`, `logs/broker.log`, dan peringatan IDS | `verifikasi-2026-11-12/12-target-redaction-and-env.log`, `sguil-alert-minggu9.png` | Request HTTP tercatat pada log akses; Snort mencatat `ET POLICY curl User-Agent` dari `.100` ke port 80 pukul 06:32 GMT |
| **3. Analisis** | Menilai dampak: publish tanpa otorisasi dapat menyalakan relay tanpa operator | Mengidentifikasi broker yang menerima klien anonim tanpa ACL dan API tanpa validasi rentang | Catatan evaluasi internal | Pola ini mencerminkan kelemahan firmware asli yang menanamkan kredensial di kode sumber |
| **4. Respons** | Tidak ada tindakan ofensif | Mengaktifkan validasi input, mewajibkan otentikasi broker, menerapkan ACL topik, memperketat izin berkas, merotasi token | `kontrol C1/validasi-input-setelah.png`, `kontrol C1/mqtt-topik-terlarang-ditolak.png`, `07-publish-mqtt-topik-terlarang-setelah.png`, `kontrol C2/kredensial-setelah.png` | Validasi aktif, otentikasi MQTT wajib, hak publish topik kontrol dicabut, kredensial lama ditolak, token lama dinonaktifkan |
| **5. Verifikasi** | Mengulang publish kontrol dan injeksi telemetri | Memastikan manipulasi ditolak dan alur data sah tetap berjalan | `06-publish-mqtt-tanpa-kredensial-setelah.png`, `09-suntik-telemetri-rest-setelah.png`, `verifikasi-2026-11-12/01-c1-live-verification.log` | `CONNACK 5`, `HTTP 400 Bad Request`, dan `HTTP 401 Unauthorized`; data sah tetap diproses |

## Skenario 4 - RT-04 Pengujian Serangan Pengulangan Pesan Kendali

| Tahap | Aktivitas Red Team | Aktivitas Blue Team | Bukti | Hasil Pengamatan |
| :--- | :--- | :--- | :--- | :--- |
| **1. Serang** | Merekam satu payload telemetri sah, lalu mengirim byte yang sama dua kali ke `telemetry/latest` | Memantau sensor dan log broker | `15-replay-sebelum-diterima.png` | Kedua pengiriman diterima (`rc=0`); payload 60 byte identik termasuk `ts` yang sama |
| **2. Deteksi** | Mengulang muatan kendali untuk memvalidasi pola trafik | Mengandalkan SID 1000002 dan SID 1000003, lalu memeriksa Sguil | `12-alert-sguil-terdeteksi.png`, `verifikasi-2026-11-12/09-sguil-alerts.log` | Sguil menampilkan CID 6127 dan 6125; uji ulang 12 November 2026 menghasilkan CID 6356 dan 6352 |
| **3. Analisis** | Menilai risiko: replay telemetri memicu keputusan penyiraman salah, replay kendali menyalakan pompa di luar jadwal | Menemukan akar masalah: ACL membatasi kanal tulis, tetapi belum ada validasi kesegaran pesan | Evaluasi tim pertahanan | Otorisasi topik saja tidak menutup CWE-294 |
| **4. Respons** | Tidak ada tindakan ofensif | Menambahkan anti-replay pada `broker.py`: `SMARTCOW_MQTT_ANTIREPLAY=1` dan `SMARTCOW_MQTT_TS_WINDOW=120` | `broker.py`, `test_broker_antireplay.py`, `/home/smartcow-lab/mqtt.env` | Uji unit 8 dari 8 lulus; broker dipasang ulang dan seluruh layanan tetap `active` |
| **5. Verifikasi** | Mengirim payload baru lalu memutar ulang byte yang sama | Memastikan replay ditolak dan layanan lain tidak terganggu | `16-replay-sesudah-ditolak.png`, `17-catatan-broker-replay.png` | Pengiriman pertama `rc=0`; replay ditolak (`rc=4`, koneksi diputus); `broker.log` mencatat `replay ditolak ... stempel waktu mundur atau duplikat` |

Catatan bukti:

- Payload tulis wajib memuat `ts` (detik atau milidetik), tidak boleh lebih tua dari jendela 120 detik, dan harus lebih besar dari `ts` terakhir per topik. ACL topik dan pencabutan token REST tetap berlaku.
- Unit test mencakup payload tanpa `ts`, `ts` kedaluwarsa, `ts` mundur atau duplikat, `ts` dalam detik, dan penghitung per topik.
- Replay pada topik telemetri tidak memicu signature MQTT khusus; jejaknya tercatat pada `broker.log`.
- Status sprinkler tidak berubah dan `/health` tetap 200.

## Catatan Validitas Artefak

Tiga berkas bukti diperiksa ulang pada 12 November 2026 dan statusnya dicatat apa adanya. Dua tangkapan layar sudah diganti dengan tangkapan layar eksekusi nyata, sedangkan satu log Nmap dipertahankan sebagai arsip.

- `redteam/evidence/11-pemindaian-port-lengkap.png` kini memuat keluaran `nmap -sT -Pn -p-` dari Attacker Node (65,73 detik, 65533 port filtered, 22 dan 80 terbuka). Gambar lama yang kosong tidak dipakai.
- `redteam/evidence/03-percobaan-login-sebelum.png` kini memuat eksekusi `ssh_try.py` pada jendela demonstrasi terkontrol (`sec_admin` BERHASIL, `root` GAGAL) dengan kata sandi disamarkan. Berkas `04-percobaan-login-setelah.png` memuat pengujian ulang setelah konfigurasi dipulihkan (`DITOLAK` untuk kedua akun). Gambar NSE yang gagal dan gambar lama yang mencetak kata sandi tidak dipakai.
- `redteam/evidence/nmap-target-after.log` dipertahankan sebagai arsip, tetapi tidak dipakai sebagai bukti status akhir karena diambil saat layanan belum berjalan. Status akhir dibuktikan oleh `01` dan `02`, `11`, `13` dan `14`, serta `blueteam/evidence/verifikasi-2026-11-12/06-target-state-recon.log`.

Catatan RT-04: dua lapis pertahanan berlaku. Topik kontrol tetap ditolak ACL broker (semua akun hanya boleh menulis ke topik telemetri), dan kanal tulis yang diizinkan memakai anti-replay stempel waktu (`SMARTCOW_MQTT_ANTIREPLAY=1`, jendela 120 detik, urutan naik per topik). Replay request REST dengan token lama ditolak melalui pencabutan token (`HTTP 401`), bukan melalui mekanisme tantangan (*challenge-response*).

## Catatan Evaluasi dan Temuan Monitoring

- **Bukti alert Sguil:** rekaman deteksi tersimpan di `docs/blueteam/evidence/sguil-alert-minggu9.png`. Pada Fase 2, Snort diperluas dengan signature kustom pada `/etc/nsm/rules/local.rules`:
  - SID 1000001: `LOCAL-TEST-ICMP` untuk verifikasi keterhubungan.
  - SID 1000002: `SMARTCOW-MQTT Unauthorized Control Topic Access`, terekam sebagai CID 6127.
  - SID 1000003: `SMARTCOW-HTTP Telemetry Attack Injection`, terekam sebagai CID 6125.
  - Alert bawaan `ET POLICY curl User-Agent Outbound` tercatat sebagai CID 6126.
  - Verifikasi 12 November 2026: query basis data `securityonion_db` mengonfirmasi CID 6125 (SID 1000003, 26 Oktober 2026 pukul 10:40:29 GMT) dan CID 6127 (SID 1000002, pukul 10:40:47 GMT), keduanya dari `192.168.12.100` ke `192.168.12.5`.
- **Kolom SID pada basis data:** kolom `event.sid` berisi ID sensor (5 = seconion-import), sedangkan SID Snort ada pada kolom `signature_id`. Kekeliruan membaca kolom ini sempat membuat nomor CID diragukan. Bukti: `blueteam/evidence/verifikasi-2026-11-12/09-sguil-alerts.log`.
- **Cakupan tangkapan Sguil:** `sguil-alert-minggu9.png` menampilkan event ICMP dan ET SCAN, bukan alert MQTT. Alert MQTT dibuktikan melalui query basis data.
- **False positive akses administratif:** koneksi SSH sah dari host administrasi `192.168.12.1` sempat memicu `ET SCAN Potential SSH Scan`. Signature bawaan belum mengecualikan IP manajemen, sehingga penyesuaian whitelist direncanakan pada fase berikutnya.
- **Status siklus:** RT-01 sampai RT-04 memiliki bukti tangkapan layar dan log. RT-03 diuji ulang 12 November 2026 dengan hasil 6 dari 6 lulus (`verifikasi-2026-11-12/01-c1-live-verification.log`). RT-04 diuji ulang pada hari yang sama dengan perbandingan sebelum dan sesudah anti-replay (`15`, `16`, dan `17`). Alert kustom Sguil tercatat sebagai CID 6356 dan 6352 (`verifikasi-2026-11-12/09-sguil-alerts.log`).
