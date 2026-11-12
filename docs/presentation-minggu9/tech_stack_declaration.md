# Deklarasi Tech Stack - Kelompok 12

**Proyek IoT yang Dilindungi:** SmartCow, sistem pengendali sprinkler otomatis kandang sapi perah. Sistem terpasang memakai enam sensor suhu DS18B20 dan empat sensor kelembapan DHT22 pada dua modul ESP32, backend Firebase Realtime Database, web dashboard pada Firebase Hosting, serta aktuator solenoid 220V yang digerakkan Solid State Relay (SSR).

Sesuai ketentuan keselamatan dan etika pengujian, seluruh pengujian keamanan dilakukan pada lingkungan replika di laboratorium. Data telemetri yang diproses bersifat sintetis (dummy) dan tidak menyentuh database produksi Firebase maupun perangkat kandang mitra.

## Daftar Isi

- [Pemetaan Komponen Teknologi](#pemetaan-komponen-teknologi)
- [Dasar Pemilihan dan Arsitektur Replika](#dasar-pemilihan-dan-arsitektur-replika)
- [Analisis Kerentanan Asli sebagai Dasar Skenario](#analisis-kerentanan-asli-sebagai-dasar-skenario)
- [Batasan Lingkungan Pengujian](#batasan-lingkungan-pengujian)

## Pemetaan Komponen Teknologi

| Komponen Arsitektur | Teknologi Sistem Produksi | Replika pada Target Node Lab |
| :--- | :--- | :--- |
| **Sistem Operasi Backend** | Infrastruktur serverless terkelola Google Firebase | Arch Linux Security Workstation pada `SRV-IOT-KEL12-B` (`192.168.12.5`) |
| **Database dan Penyimpanan** | Firebase Realtime Database, path `devices/cow-sprinkler-01/{telemetry,control,status,events}` | Berkas JSON lokal dengan REST ala RTDB pada `127.0.0.1:9000` (`app.py`) |
| **Protokol Telemetri** | HTTPS REST dengan Database Secret; ESP32 mengirim tiap 2 detik | HTTP REST dengan token bearer; simulator mengirim data dummy tiap 2 detik |
| **Protokol Komunikasi IoT** | MQTT disiapkan sebagai opsi pengembangan (`PRODUCT.md`) | Broker MQTT mandiri pada 1883 dengan otentikasi dan ACL topik; akses jaringan ditutup lewat B4 |
| **Komunikasi Antar Node** | ESP-NOW 2.4 GHz tanpa enkripsi antar modul ESP32 | TCP/IP virtual terisolasi pada segmen Host-Only `192.168.12.0/24` |
| **Antarmuka Monitoring** | Firebase Hosting, aplikasi web statis HTML/CSS/JavaScript | Nginx 1.18.0 menyajikan antarmuka yang sama dan meneruskan `/api` ke backend lokal |
| **Otentikasi dan Otorisasi** | Firebase Auth email/kata sandi dan security rules RTDB berbasis peran (`/access/<uid>`) | Token bearer REST, kredensial broker MQTT, dan ACL topik |
| **Modul Sensor** | 6 DS18B20 pada bus OneWire dan 4 DHT22 pada dua ESP32 | Simulator Python dengan nilai acak dalam rentang biologis sapi |
| **Aktuator Fisik** | Modul SSR pada GPIO23 yang mengendalikan katup solenoid 220V | Status kendali pada REST API dan topik MQTT tanpa sambungan tegangan |
| **Pencatatan Log** | Node `events` dan `status` pada Firebase | systemd-journald, `logs/access.log`, dan `logs/broker.log` |
| **Monitoring Keamanan** | Belum tersedia pada rancangan awal produksi | Security Onion `192.168.12.200` dengan sensor Snort promiscuous |

## Dasar Pemilihan dan Arsitektur Replika

Bagian III Panduan PBL mewajibkan replika lingkungan uji agar tidak menimbulkan risiko operasional pada sistem mitra. Dua karakteristik produksi direplikasi secara presisi: mekanisme REST API berbasis token dan hierarki path Firebase Realtime Database (`devices/cow-sprinkler-01/...`). Penamaan rute, nama field telemetri (`t1` sampai `t6`, `h1` sampai `h4`, `avg`, `thi`, `validMask`), dan struktur data diselaraskan dengan spesifikasi produksi.

Karena jaringan laboratorium tidak memiliki akses internet untuk mengunduh Firebase Emulator, replika backend dibangun dengan modul standar Python 3.9 bawaan Arch Linux tanpa dependensi eksternal. Struktur berkas JSON lokal menyerupai cara kerja Realtime Database.

MQTT diimplementasikan sebagai lapisan komunikasi sekunder untuk melengkapi REST API. Pada dokumen rancangan proyek SmartCow, broker disiapkan sebagai jalur alternatif kendali aktuator, sehingga broker MQTT mandiri dibangun pada port 1883 agar skenario pengujian protokol IoT dapat diuji objektif pada Fase 2.

## Analisis Kerentanan Asli sebagai Dasar Skenario

Analisis kode sumber sistem SmartCow asli menemukan beberapa potensi celah yang menjadi landasan perancangan skenario:

1. **Penyimpanan Database Secret di dalam firmware:** `esp32/src/main.cpp` menyusun URL permintaan dengan menyematkan query `?auth=` secara eksplisit. Secret ini memberi akses administratif penuh ke basis data jika kode tersebar.
2. **Penonaktifan verifikasi sertifikat TLS:** firmware memakai `setInsecure()` pada komunikasi HTTPS, sehingga integritas server tujuan tidak dapat divalidasi mikrokontroler.
3. **Pembagian hak akses dashboard:** security rules RTDB menolak akses publik secara default dan memetakan hak melalui `/access/<uid>`. Namun kepemilikan secret firmware memungkinkan pembacaan dan penulisan data tanpa melewati validasi peran dashboard.
4. **Komunikasi ESP-NOW tanpa enkripsi:** transmisi antar mikrokontroler pada 2.4 GHz berjalan tanpa enkripsi payload sehingga rentan penyadapan lokal.
5. **Kredensial default yang pernah terbuka:** kata sandi awal dan konfigurasi `js/firebase-config.js` sempat dibagikan dalam dokumentasi internal, sehingga rotasi kredensial berkala diperlukan.

Temuan poin 1, 2, dan 5 telah dimitigasi pada replika melalui kontrol C1 (validasi input dan ACL topik), C2 (manajemen kredensial dan rotasi), serta A2 (autentikasi kunci SSH). Poin 3 dan 4 menjadi materi evaluasi lanjutan pada pengujian Fase 2.

## Batasan Lingkungan Pengujian

- Replika tidak menjalankan layanan cloud Firebase langsung; pengujian difokuskan pada validasi struktur input dan pembatasan hak otorisasi akses.
- Pengujian aktuasi fisik tidak memakai katup solenoid bertegangan tinggi demi keselamatan kerja; respons sistem dievaluasi melalui status kendali pada memori dan log.
- Broker MQTT mencakup fungsionalitas inti (CONNECT, SUBSCRIBE, PUBLISH, PINGREQ) tanpa retained message dan wildcard topic.
- Pengujian dibatasi pada segmen jaringan lokal tanpa interaksi jaringan publik.
