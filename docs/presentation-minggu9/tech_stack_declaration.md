# Deklarasi tech stack & replikasi — Kelompok 12 Kelas B

Skenario resmi: **No 10 — IoT Protocol Guardian** (MQTT replay & publish tanpa izin).
Proyek IoT asli: **sistem penyemprotan sapi otomatis berbasis suhu kandang**.

## 1. Cara kerja sistem asli

Sensor DS18B20 dibaca ESP32, dikirim ke Firebase Realtime Database via HTTP.
Dashboard web (Firebase Hosting) menampilkan suhu. Saat suhu menyentuh threshold,
perintah semprot ditulis ke database, dibaca ESP32, diteruskan ke relay lalu ke
solenoid valve. Semprotan nyala. Sederhana. Makanya celahnya juga sederhana:
siapa pun yang bisa menyuntik data suhu palsu atau perintah palsu bisa
menyalakan semprotan seenaknya.

## 2. Tabel pemetaan asli ke replika

| Komponen | Sistem asli | Replika (Target Node 192.168.12.5) |
| :--- | :--- | :--- |
| OS backend | Firebase managed (tanpa OS) | Arch Linux Security Workstation |
| Database | Firebase Realtime Database | Belum ada, ditentukan Fase 2 |
| Sensor | ESP32 + DS18B20, kirim via HTTP | Publish suhu via MQTT, port 1883 siap |
| Perintah aktuator | RTDB → ESP32 → relay → solenoid valve | Service simulasi di replika, Fase 2 |
| Dashboard | Web Firebase Hosting | Halaman HTTP replika, Fase 2 |
| Data | Data kandang asli | 100% dummy, tidak ada data asli masuk lab |

## 3. Batasan yang kami pegang

Target Node di lab BUKAN sistem kandang. Dilarang scanning atau eksploitasi ke
sistem Firebase asli, ke jaringan kampus, atau ke kelompok lain. Serangan hanya
ke 192.168.12.5. Rekomendasi hardening yang terbukti di lab boleh dibawa ke
sistem asli setelah praktikum, bareng pembimbing proyek IoT.

## 4. Kenapa replika ini setara buat latihan

Pola komunikasinya sama: publish data sensor, simpan status, kirim perintah ke
aktuator. Bedanya cuma medianya (lab pakai MQTT + HTTP di segmen terisolasi).
Celah yang kami kejar (replay perintah, publish tanpa izin, brute-force akses)
mungkin ada juga di sistem asli. Nemu di sini, betulkan di sana.
