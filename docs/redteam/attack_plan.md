# Rencana Skenario Penyerangan dan Pengujian Keamanan (Fase 2)

**Kelompok 12 | Kelas B | Praktik Keamanan Siber Terapan (TEK1314)**  
**Skenario Proyek:** No. 10 - *IoT Protocol Guardian* (Sistem Sprinkler Kandang Sapi)  
**Target Pengujian:** `SRV-IOT-KEL12-B` (Arch Linux, `192.168.12.5`)

## Daftar Isi

- [I. Latar Belakang dan Tujuan Pengujian](#i-latar-belakang-dan-tujuan-pengujian)
- [II. Lingkungan Laboratorium dan Batasan Sistem](#ii-lingkungan-laboratorium-dan-batasan-sistem)
- [III. Daftar Skenario Serangan Red Team](#iii-daftar-skenario-serangan-red-team)
- [IV. Detail Prosedur Pengujian](#iv-detail-prosedur-pengujian)
- [V. Alur Kerja Purple Team](#v-alur-kerja-purple-team)
- [VI. Batasan Ruang Lingkup Pengujian](#vi-batasan-ruang-lingkup-pengujian)

## I. Latar Belakang dan Tujuan Pengujian

Dokumen ini memuat rancangan skenario penyerangan Red Team untuk menguji keamanan replika backend SmartCow pada Fase 2. Sistem yang diuji adalah pengendali otomatis sprinkler kandang sapi perah yang bekerja berdasarkan suhu dan kelembapan untuk mengendalikan relay pompa air.

Mengacu pada **Skenario 10 (*IoT Protocol Guardian*)**, pengujian menitikberatkan komunikasi protokol IoT. Titik uji utamanya adalah pengiriman data tanpa otorisasi (*unauthorized publish*), pemalsuan telemetri, dan serangan pengulangan (*replay attack*). Pengujian ini penting karena gangguan pada data kendali dapat membuat pompa bekerja tanpa henti atau gagal menyala saat suhu kandang tinggi.

Tujuan pelaksanaan: menguji apakah hardening Blue Team pada Target Node bekerja benar, sekaligus memverifikasi apakah sensor Snort pada Security Onion mencatat indikasi serangan.

## II. Lingkungan Laboratorium dan Batasan Sistem

Seluruh pengujian berjalan di jaringan virtual Host-Only `192.168.12.0/24`, terpisah dari internet dan sistem kandang mitra.

| Komponen | Spesifikasi dan Peran |
| :--- | :--- |
| **Attacker Node** | `ATTACKER-KEL12-B` (Ubuntu 22.04 LTS, `192.168.12.100`), menjalankan pemindaian port, pengujian kredensial, dan pengiriman paket MQTT/HTTP |
| **Target Node** | `SRV-IOT-KEL12-B` (Arch Linux, `192.168.12.5`), menjalankan broker MQTT, REST API Python (`http.server`, bukan Flask), dan reverse proxy Nginx |
| **Monitoring Node** | `SOC-KEL12-B` (Security Onion, `192.168.12.200`), menangkap lalu lintas dan memicu peringatan melalui sensor Snort dan antarmuka Sguil |
| **Port Awal Fase 2** | 22 (SSH), 80 (dashboard dan proxy API), 1883 (broker MQTT) terbuka; 9000 (REST API internal) sudah filtered |
| **Port Akhir** | 22 dan 80 terbuka; 1883 ditutup lewat kontrol B4; 9000 hanya loopback |
| **Karakteristik Data** | Data dummy suhu 24-30 °C dan kelembapan 70-85%, dikirim simulator lokal tiap dua detik |

## III. Daftar Skenario Serangan Red Team

Skenario mengikuti Bagian IX Panduan PBL TEK1314.

| Kode | Kategori | Skenario dan Alat | Target Uji | Indikator Keberhasilan Pertahanan |
| :--- | :--- | :--- | :--- | :--- |
| **RT-01** | *Reconnaissance* | Pemetaan port dan identifikasi versi dengan **Nmap** (`-sS -sV -O`), serta pemeriksaan header dengan **cURL** | Seluruh port TCP `192.168.12.5` | Port 9000 tidak terjangkau dari luar; header Nginx tanpa nomor versi |
| **RT-02** | *Exploitation & Access* | Uji ketahanan autentikasi SSH terhadap tebakan kata sandi dan banjir koneksi memakai **ssh_try.py** serta klien OpenSSH | Port 22 (akun `root` dan `sec_admin`) | Login root ditolak; login kata sandi ditolak; laju koneksi konkuren dibatasi |
| **RT-03** | *Web & Protokol IoT* | Publish pesan kontrol relay tanpa hak akses via **mqtt_pub.py** dan injeksi telemetri di luar rentang via **cURL** | Topik `cow-sprinkler-01/control` (1883) dan endpoint REST telemetri | Publish ditolak `CONNACK 5`; nilai di luar batas ditolak `HTTP 400` |
| **RT-04** | *Replay Attack* | Perekaman pesan telemetri/kendali yang sah, lalu pengiriman ulang byte-identik dari Attacker Node | Broker MQTT `192.168.12.5:1883` (topik tulis dan topik kontrol) | Topik kontrol ditolak ACL; anti-replay stempel waktu menolak replay; token REST lama ditolak `HTTP 401` |

## IV. Detail Prosedur Pengujian

### 1. RT-01: Pemindaian Port dan Banner Layanan (*Reconnaissance*)

- **Alasan Pengujian:** Mengetahui sejauh mana informasi layanan Target Node terbaca dari luar jaringan.
- **Langkah Kerja:**
  1. Menjalankan pemindaian TCP stealth dengan deteksi layanan:
     ```bash
     nmap -sS -sV -O -p 22,80,1883,9000 192.168.12.5
     ```
  2. Memeriksa banner header web server:
     ```bash
     curl -I http://192.168.12.5/
     ```
- **Hasil Pengamatan Lapangan:**
  - *Sebelum Hardening:* API mendengarkan pada `0.0.0.0:9000` dan hanya dilindungi firewall, sehingga pemindaian dari Attacker Node mencatat port 9000 filtered. Nginx menampilkan `nginx/1.18.0 (Arch Linux)`.
  - *Sesudah Hardening:* Listener API terikat pada `127.0.0.1:9000`, port 9000 filtered, dan respons Nginx hanya `Server: nginx`.

### 2. RT-02: Pengujian Autentikasi dan Pembatasan Sesi SSH (*Exploitation*)

- **Alasan Pengujian:** Menguji ketahanan akses terminal terhadap tebakan kata sandi berulang dan pembukaan sesi massal.
- **Langkah Kerja:**
  1. Menjalankan percobaan autentikasi berulang pada akun `root` dan `sec_admin`:
     ```bash
     python3 /home/analyst/ssh_try.py 192.168.12.5 root:<SANDI_LAB> sec_admin:<SANDI_LAB>
     ```

     Nilai sandi lab tidak ditulis di repositori. Pasangan akun dan sandi diisi manual dari catatan internal kelompok saat pengujian.
  2. Menjalankan 8 percobaan koneksi serentak untuk menguji batas koneksi:
     ```bash
     for i in {1..8}; do ssh -o BatchMode=yes sec_admin@192.168.12.5 & done
     ```
- **Hasil Pengamatan Lapangan:**
  - *Sebelum Hardening:* `sec_admin` dapat login dengan kata sandi sederhana, tanpa pembatasan sesi serentak.
  - *Sesudah Hardening:* Login kata sandi ditolak dengan `Permission denied (publickey)`, dan koneksi paralel berlebih diredam iptables serta konfigurasi sshd.

### 3. RT-03: Pengiriman Perintah Ilegal dan Manipulasi Data IoT (*Protocol Vulnerability*)

- **Alasan Pengujian:** Menguji otorisasi kanal MQTT agar relay sprinkler tidak dapat dikendalikan sembarangan.
- **Langkah Kerja:**
  1. Mengirim perintah menghidupkan sprinkler tanpa kredensial sah:
     ```bash
     python3 /home/analyst/mqtt_pub.py --host 192.168.12.5 --port 1883 --topic cow-sprinkler-01/control --message '{"manualSsr":"on"}'
     ```
  2. Mengirim telemetri palsu dengan kelembapan 150% ke endpoint REST:
     ```bash
     curl -X PUT "http://192.168.12.5/devices/cow-sprinkler-01/telemetry/latest.json?auth=<TOKEN_API>" \
          -H "Content-Type: application/json" \
          -d '{"t1":28.5,"t2":28.5,"t3":28.5,"t4":28.5,"t5":28.5,"t6":28.5,"h1":150,"h2":68,"h3":68,"h4":68}'
     ```
- **Hasil Pengamatan Lapangan:**
  - *Sebelum Hardening:* Broker menerima publish dari klien anonim, dan API menerima kelembapan 150% tanpa validasi.
  - *Sesudah Hardening:* Broker menolak koneksi dengan `CONNACK return code 5`, dan API membalas `HTTP 400 Bad Request`.

### 4. RT-04: Pengujian Serangan Pengulangan Paket (*Replay Attack*)

- **Alasan Pengujian:** Memastikan perintah kendali pompa yang disadap tidak dapat dipakai ulang untuk memanipulasi status penyemprotan.
- **Langkah Kerja:**
  1. Menangkap muatan kendali sprinkler yang sah saat sistem beroperasi normal:
     ```json
     {"manualSsr": "on", "source": "operator", "timestamp": 1771987654321}
     ```
  2. Mengirim ulang paket yang sama dari Attacker Node ke topik kontrol:
     ```bash
     python3 /home/analyst/mqtt_pub.py --host 192.168.12.5 --port 1883 --topic cow-sprinkler-01/control --message '{"manualSsr":"on","source":"replay"}'
     ```
  3. Menguji pengiriman ulang request kendali ke REST API dengan token yang sudah dicabut:
     ```bash
     curl -X PUT "http://192.168.12.5/devices/cow-sprinkler-01/control.json?auth=<TOKEN_LAMA>" \
          -H "Content-Type: application/json" \
          -d '{"manualSsr":"on"}'
     ```
- **Hasil Pengamatan Lapangan:**
  - *Sebelum Hardening:* Broker menerima pengiriman ulang dari klien anonim tanpa otorisasi topik, status relay berubah, dan ketiadaan validasi token membiarkan perubahan kendali tanpa pengawasan operator.
  - *Sesudah Hardening:* Publish ke topik kendali diputus broker sesuai ACL (`broker.log` mencatat penolakan publish ke topik terlarang). Request REST dengan token lama ditolak `HTTP 401 Unauthorized`. Sensor Snort membangkitkan alert SID 1000002 (`SMARTCOW-MQTT Unauthorized Control Topic Access`) dengan CID 6127 yang diverifikasi melalui query basis data. Status sprinkler tetap aman.
  - *Uji anti-replay:* pada broker sebelum perbaikan, payload 60 byte yang sama diterima dua kali (`15-replay-sebelum-diterima.png`). Setelah `SMARTCOW_MQTT_ANTIREPLAY=1` dipasang, pengiriman pertama diterima dan replay ditolak dengan entri `replay ditolak ... stempel waktu mundur atau duplikat` (`16-replay-sesudah-ditolak.png` dan `17-catatan-broker-replay.png`).

## V. Alur Kerja Purple Team

Pelaksanaan pengujian memakai siklus kerja sama antara penyerang dan pihak bertahan:

```text
[ 1. Eksekusi Serangan ] --> [ 2. Pemeriksaan Deteksi ] --> [ 3. Analisis Hasil ]
       (Red Team)                   (Security Onion)              (Evaluasi Tim)
                                                                        |
[ 5. Pengujian Ulang   ] <-- [ 4. Penerapan Mitigasi  ] <---------------+
       (Verifikasi)                   (Blue Team)
```

1. **Eksekusi Serangan:** Red Team menjalankan skenario sesuai daftar dan mencatat waktu eksekusi.
2. **Pemeriksaan Deteksi:** Blue Team memeriksa apakah aktivitas memunculkan alert di Security Onion (Snort/Sguil) atau log Target Node.
3. **Analisis Hasil:** Kedua tim menilai apakah kontrol yang ada sudah menahan serangan atau masih memiliki celah.
4. **Penerapan Mitigasi:** Blue Team menambahkan perbaikan yang dibutuhkan (firewall, ACL broker, atau validasi input).
5. **Pengujian Ulang:** Red Team mengulang pengujian yang sama untuk memastikan serangan tidak lagi berhasil.

Seluruh tangkapan layar bukti disimpan di `docs/redteam/evidence/`. Rekapitulasi hasil dicatat bertahap pada [purple-team-log.md](../purple-team-log.md).

## VI. Batasan Ruang Lingkup Pengujian

1. **Keamanan sistem:** tidak ada serangan Denial of Service yang mematikan VM secara permanen, dan tidak ada malware perusak.
2. **Keterisolasian jaringan:** pengujian dibatasi pada subnet `192.168.12.0/24`. Layanan cloud Firebase dan kandang mitra tidak diakses.
3. **Integritas konfigurasi:** hardening yang aktif dipertahankan, kecuali pada demonstrasi terencana untuk membandingkan kondisi sebelum dan sesudah perbaikan.
