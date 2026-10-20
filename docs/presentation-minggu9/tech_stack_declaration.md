# Deklarasi tech stack - Kelompok 12

**Proyek IoT:** SmartCow, sistem sprinkler kandang sapi. Enam sensor DS18B20 dan
empat DHT22 di dua ESP32, backend Firebase Realtime Database, dashboard web di
Firebase Hosting, dan solenoid 220V yang dikendalikan SSR.

Lab kami memakai replika, bukan sistem asli. Semua data yang dipakai adalah data
dummy, dan tidak ada satu pun permintaan yang pernah menyentuh Firebase produksi
maupun perangkat di kandang mitra.

## Pemetaan teknologi

| Komponen | Teknologi pada proyek IoT asli | Replika pada Target Node |
| --- | --- | --- |
| **Sistem operasi backend** | Infrastruktur Firebase terkelola Google, tanpa OS server yang dikelola kelompok | Arch Linux pada `SRV-IOT-KEL12-B` (192.168.12.5) |
| **Database dan penyimpanan data** | Firebase Realtime Database, path `devices/cow-sprinkler-01/{telemetry,control,status,events}` | Penyimpanan JSON lokal dengan endpoint REST bergaya RTDB di `127.0.0.1:9000` (`app.py`) |
| **Protokol komunikasi sensor ke backend** | HTTPS REST dengan Database Secret, ESP32 menulis telemetri tiap 2 detik | HTTP REST dengan token bearer, simulator menulis telemetri dummy tiap 2 detik (`simulator.py`) |
| **Protokol lanjutan IoT** | Broker MQTT belum diputuskan, MQTT dan ArduinoJson disiapkan sebagai opsi (`PRODUCT.md`) | Broker MQTT minimal di port 1883 dengan autentikasi dan ACL topik (`broker.py`) |
| **Komunikasi antar perangkat** | ESP-NOW 2,4 GHz antar dua ESP32, tanpa enkripsi | TCP/IP pada segmen Host-Only terisolasi 192.168.12.0/24 |
| **Dashboard monitoring** | Firebase Hosting, web statis HTML/CSS/JavaScript tanpa build step | Nginx 1.18.0 menyajikan dashboard yang sama dan meneruskan `/api` ke API lokal |
| **Autentikasi pengguna** | Firebase Authentication Email/Password plus rules RTDB berbasis peran di `/access/<uid>` | Token bearer pada API, kredensial broker, dan pembatasan topik |
| **Sensor** | 6x DS18B20 pada satu bus OneWire dan 4x DHT22 di dua ESP32 | Simulator Python, angka acak di rentang suhu dan kelembapan sapi |
| **Aktuator** | SSR pada GPIO23 menuju solenoid 220V | Perintah `control` pada API dan topik MQTT, tanpa tegangan nyata |
| **Logging** | Firebase `events`, `status`, dan log 30 detik | journald persistent, `access.log` aplikasi, `broker.log` |
| **Monitoring keamanan** | Tidak ada pada proyek asli | Security Onion di 192.168.12.200, sensor promiscuous |

## Kenapa replikanya seperti ini

Bagian III panduan melarang menyentuh sistem produksi dan meminta replika tech
stack yang sama persis. Dua hal yang paling menentukan yaitu REST dengan token
dan struktur path `devices/cow-sprinkler-01/...`, jadi keduanya ditiru persis: nama
path, nama field telemetri (`t1` sampai `t6`, `h1` sampai `h4`, `avg`, `thi`,
`validMask`), dan aturan penulisan.

Firebase Emulator tidak bisa dipasang karena segmen lab tidak punya akses
internet. Karena itu replika memakai Python 3.9 standar dari Arch tanpa dependensi
baru, dan bentuk datanya disimpan seperti bentuk Firebase.

MQTT ditambahkan sebagai lapisan kedua, bukan protocol utama. Pada proyek asli
broker masih belum diputuskan, jadi keputusannya kami catat sebagai broker kedua
yang perlu diuji di Fase 2.

## Celah nyata yang jadi dasar skenario

Temuan berikut diambil dari kode proyek asli dan jadi dasar tiga skenario serangan.

1. **Database Secret tertanam di firmware.** `esp32/src/main.cpp` menyusun URL
   dengan `?auth=` dan nilai secret itu ada di dalam sketch. Secret itu setara
   akses penuh, jadi siapa pun yang punya bisa menulis apa saja ke RTDB. Tim
   proyek sudah diberi tahu bahwa file `.ino` tidak boleh tersebar.
2. **TLS firmware memakai `setInsecure()`.** Verifikasi sertifikat dimatikan, jadi
   perangkat tidak bisa memastikan sedang berbicara dengan server Firebase.
3. **Autentikasi dashboard berbasis peran, tapi perimeternya tipis.** Rules RTDB
   menolak akses secara default dan `/access/<uid>` menyimpan peran, enabled, dan
   tiga izin. Admin pertama tidak bisa diubah dari browser, tapi API pendaftaran
   Firebase Auth secara teknis masih terbuka, dan siapa pun yang punya secret
   firmware melewati seluruh aturan itu.
4. **ESP-NOW tanpa enkripsi.** Paket antar dua ESP32 berjalan tanpa proteksi isi,
   dan kanal 2,4 GHz dipakai bersama.
5. **Kredensial pernah tersebar.** Password admin dan isi `js/firebase-config.js`
   pernah dibagikan, sehingga rotasi kredensial masuk daftar tindak lanjut.

Nomor 1, 2, dan 5 sudah dicermati di replika lab lewat kontrol C1, C2, dan A2.
Nomor 3 dan 4 menjadi bahan skenario yang akan diuji di Fase 2, karena
membutuskan rules RTDB dan menambahkan enkripsi ESP-NOW berada di luar lingkup
lab.

## Batasan yang kami akui

- Replika tidak memakai Firebase sungguhan, dan rules RTDB asli tidak dievaluasi
  langsung. Yang diuji adalah pola validasi dan aturan aksesnya.
- Sensor dan aktuator tidak ada. Semua angka berasal dari simulator, sehingga
  tidak ada perilaku fisik yang bisa diuji, termasuk keandalan sensor dan
  keselamatan listrik.
- Protokol MQTT yang dipakai hanya subset: CONNECT, SUBSCRIBE, PUBLISH, dan
  PINGREQ. Retained message dan wildcard topic belum didukung.
- Tidak ada layanan berbayar yang ditiru. Peran admin di proyek asli tidak
  punya batas kuota, dan itu tidak diuji di lab.
