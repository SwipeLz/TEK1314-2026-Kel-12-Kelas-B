# Deklarasi Tech Stack - Kelompok 12

**Proyek IoT yang Dilindungi:** SmartCow, sistem pengendali sprinkler otomatis kandang sapi perah. Sistem terpasang menggunakan enam sensor suhu DS18B20 dan empat sensor kelembapan DHT22 pada dua modul ESP32, backend Firebase Realtime Database, web dashboard pada Firebase Hosting, serta aktuator solenoid 220V yang digerakkan melalui Solid State Relay (SSR).

Sesuai ketentuan keselamatan dan etika pengujian, seluruh pengujian keamanan dilakukan pada lingkungan replika di laboratorium. Seluruh data telemetri yang diproses merupakan data sintetis (dummy) tanpa menyentuh database produksi Firebase maupun perangkat kandang mitra.

## Pemetaan Komponen Teknologi

| Komponen Arsitektur | Teknologi Sistem Produksi | Replika pada Target Node Lab |
| :--- | :--- | :--- |
| **Sistem Operasi Backend** | Infrastruktur serverless terkelola Google Firebase | Arch Linux Security Workstation pada `SRV-IOT-KEL12-B` (192.168.12.5) |
| **Database & Penyimpanan Data** | Firebase Realtime Database, struktur path `devices/cow-sprinkler-01/{telemetry,control,status,events}` | Penyimpanan berkas JSON lokal dengan antarmuka REST ala RTDB pada `127.0.0.1:9000` (`app.py`) |
| **Protokol Telemetri Sensor** | HTTPS REST menggunakan Database Secret, ESP32 mengirim data tiap 2 detik | HTTP REST dengan token otentikasi bearer, simulator mengirim data dummy tiap 2 detik (`simulator.py`) |
| **Protokol Komunikasi IoT** | Evaluasi protokol MQTT disiapkan sebagai opsi pengembangan (`PRODUCT.md`) | Broker MQTT mandiri pada port 1883 dengan autentikasi akun dan pembatasan hak topik (`broker.py`) |
| **Komunikasi Antar Node IoT** | Protokol nirkabel ESP-NOW 2.4 GHz tanpa enkripsi antar modul ESP32 | Jaringan TCP/IP virtual terisolasi pada segmen Host-Only 192.168.12.0/24 |
| **Antarmuka Monitoring** | Firebase Hosting, aplikasi web statis HTML/CSS/JavaScript | Nginx 1.18.0 menyajikan berkas antarmuka yang sama dan meneruskan rute `/api` ke backend lokal |
| **Otentikasi & Otorisasi** | Firebase Auth berbasis email/kata sandi dan security rules RTDB berbasis peran (`/access/<uid>`) | Token otentikasi pada REST API, kredensial akun broker MQTT, serta kontrol akses topik (*topic ACL*) |
| **Modul Sensor** | 6x DS18B20 pada bus OneWire dan 4x DHT22 pada dua mikrokontroler ESP32 | Skrip simulator Python yang membangkitkan nilai acak dalam rentang biologis suhu dan kelembapan sapi |
| **Aktuator Fisik** | Modul SSR pada GPIO23 yang mengendalikan katup solenoid 220V | Parameter status kontrol pada REST API dan topik MQTT tanpa sambungan tegangan fisik |
| **Pencatatan Log** | Pencatatan peristiwa pada Firebase node `events` dan `status` | Logging persisten melalui systemd-journald, `logs/access.log` pada aplikasi, dan `logs/broker.log` |
| **Monitoring Keamanan** | Belum tersedia pada rancangan awal sistem produksi | Monitoring berbasis Security Onion pada 192.168.12.200 dengan sensor Snort mode promiscuous |

## Dasar Pemilihan dan Arsitektur Replika

Ketentuan Bagian III Panduan PBL mewajibkan penggunaan replika lingkungan uji untuk mencegah risiko operasional pada sistem produksi mitra. Dua karakteristik mendasar yang direplikasi secara presisi meliputi mekanisme REST API berbasis otentikasi token serta hierarki path Firebase Realtime Database (`devices/cow-sprinkler-01/...`). Seluruh penamaan rute, nama field telemetri (`t1` s.d. `t6`, `h1` s.d. `h4`, `avg`, `thi`, `validMask`), serta struktur data diselaraskan dengan spesifikasi produksi.

Karena jaringan laboratorium tidak memiliki akses internet untuk mengunduh Firebase Emulator, kelompok membangun replika backend mandiri menggunakan modul standar Python 3.9 bawaan Arch Linux tanpa menambah dependensi eksternal, dengan struktur berkas JSON lokal yang menyerupai cara kerja Realtime Database.

Protokol MQTT diimplementasikan sebagai lapisan komunikasi sekunder untuk melengkapi REST API. Pada dokumen rancangan proyek SmartCow, implementasi broker disiapkan sebagai jalur alternatif kendali aktuator, sehingga replika broker MQTT mandiri dibangun di port 1883 agar skenario pengujian protokol IoT dapat diuji secara objektif pada Fase 2.

## Analisis Kerentanan Asli sebagai Dasar Skenario

Analisis keamanan pada kode sumber sistem SmartCow asli menemukan beberapa potensi celah keamanan yang menjadi landasan perancangan skenario penyerangan:

1. **Penyimpanan Database Secret di Dalam Firmware:** Berkas `esp32/src/main.cpp` menyusun URL permintaan data dengan menyematkan query parameter `?auth=` secara eksplisit. Secret ini memberikan akses administratif penuh ke basis data jika berkas kode program tersebar.
2. **Penonaktifan Verifikasi Sertifikat TLS:** Firmware menggunakan metode `setInsecure()` pada komunikasi HTTPS sehingga integritas server tujuan tidak dapat divalidasi oleh mikrokontroler.
3. **Pembagian Hak Akses Dashboard:** Aturan keamanan RTDB menolak akses publik secara default dan memetakan hak akses lewat path `/access/<uid>`. Namun, kepemilikan secret firmware memungkinkan pembacaan dan penulisan data tanpa melewati validasi peran dashboard.
4. **Komunikasi ESP-NOW Tanpa Enkripsi:** Transmisi data antar mikrokontroler pada frekuensi 2.4 GHz berjalan tanpa enkripsi payload sehingga rentan terhadap penyadapan lokal.
5. **Kredensial Default yang Pernah Terbuka:** Kata sandi awal dan konfigurasi berkas `js/firebase-config.js` sempat dibagikan dalam dokumentasi internal sehingga memerlukan rotasi kredensial berkala.

Temuan pada poin 1, 2, dan 5 telah dimitigasi pada replika laboratorium melalui penerapan kontrol pengamanan C1 (validasi input dan ACL topik), C2 (manajemen kredensial dan rotasi), serta A2 (autentikasi kunci SSH). Sedangkan poin 3 dan 4 menjadi materi evaluasi lanjutan pada pengujian Fase 2.

## Batasan Lingkungan Pengujian

- Replika laboratorium tidak menjalankan layanan cloud Firebase langsung; pengujian difokuskan pada validasi struktur input dan pembatasan hak otorisasi akses.
- Pengujian aktuasi fisik tidak menggunakan katup solenoid bertegangan tinggi demi keselamatan kerja di laboratorium; respon sistem dievaluasi melalui pencatatan status kendali pada memori dan log.
- Protokol MQTT yang diimplementasikan mencakup fungsionalitas inti (CONNECT, SUBSCRIBE, PUBLISH, PINGREQ) tanpa fitur retained message dan wildcard topic.
- Pengujian dibatasi pada segmen jaringan lokal tanpa melibatkan interaksi jaringan publik.
