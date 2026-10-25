# Rencana Skenario Penyerangan dan Pengujian Keamanan (Fase 2)

**Kelompok 12 | Kelas B | Praktik Keamanan Siber Terapan (TEK1314)**  
**Skenario Proyek:** No. 10 - *IoT Protocol Guardian* (Sistem Sprinkler Kandang Sapi)  
**Target Pengujian:** `SRV-IOT-KEL12-B` (Arch Linux - `192.168.12.5`)  

---

## I. Latar Belakang dan Tujuan Pengujian

Dokumen ini memuat rancangan skenario penyerangan Red Team untuk menguji keamanan replika backend SmartCow pada Fase 2. Sistem yang diuji merupakan pengendali otomatis sprinkler kandang sapi perah yang bekerja berdasarkan data suhu serta kelembapan dan mengontrol relay pompa air.

Mengacu pada penugasan **Skenario 10 (*IoT Protocol Guardian*)**, pengujian menitikberatkan pada aspek komunikasi protokol IoT. Titik uji utama mencakup pengiriman data tanpa otorisasi (*unauthorized publish*), pemalsuan data telemetri, dan serangan pengulangan (*replay attack*). Pengujian ini diperlukan karena gangguan data kendali pada sistem nyata dapat menyebabkan pompa bekerja tanpa henti atau gagal menyala saat suhu kandang tinggi.

Tujuan utama pelaksanaan skenario ini adalah menguji apakah konfigurasi hardening yang diterapkan Blue Team pada Target Node bekerja dengan benar, sekaligus memverifikasi apakah sensor Snort pada Security Onion berhasil mencatat indikasi serangan.

---

## II. Lingkungan Laboratorium dan Batasan Sistem

Seluruh pengujian dijalankan di dalam jaringan virtual lokal bertipe *Host-Only* (`192.168.12.0/24`), terpisah dari internet dan sistem kandang mitra.

| Komponen | Spesifikasi dan Peran |
|---|---|
| **Attacker Node** | `ATTACKER-KEL12-B` (Ubuntu 22.04 LTS / IP `192.168.12.100`), digunakan untuk menjalankan pemindaian port, pengujian kredensial, dan pengiriman paket MQTT/HTTP. |
| **Target Node** | `SRV-IOT-KEL12-B` (Arch Linux / IP `192.168.12.5`), menjalankan broker MQTT, layanan REST API Flask, dan reverse proxy Nginx. |
| **Monitoring Node** | `SOC-KEL12-B` (Security Onion / IP `192.168.12.200`), bertugas menangkap lalu lintas jaringan dan memicu peringatan melalui sensor Snort dan antarmuka Sguil. |
| **Layanan Terbuka** | Port 22/TCP (SSH), Port 80/TCP (Web dashboard dan proxy API), Port 1883/TCP (MQTT broker), Port 9000/TCP (REST API internal). |
| **Karakteristik Data** | Data dummy berupa suhu (24-30 derajat C) dan kelembapan (70-85%) yang dikirim simulator lokal tiap dua detik. |

---

## III. Daftar Skenario Serangan Red Team

Mengikuti ketentuan Panduan PBL TEK1314 Bagian IX, skenario penyerangan dibagi ke dalam beberapa kategori uji:

| Kode | Kategori | Skenario dan Alat yang Digunakan | Target Uji | Indikator Keberhasilan Pertahanan |
|---|---|---|---|---|
| **RT-01** | *Reconnaissance* | Pemetaan port terbuka dan identifikasi versi perangkat lunak menggunakan **Nmap** (`-sS -sV -O`) serta pemeriksaan header via **cURL**. | Seluruh port TCP pada `192.168.12.5` | Port internal (9000) tidak dapat diakses langsung dari luar; header HTTP Nginx tidak menampilkan rilis versi perangkat lunak. |
| **RT-02** | *Exploitation & Access* | Pengujian ketahanan autentikasi SSH terhadap tebakan kata sandi dan banjir koneksi konkuren menggunakan skrip **ssh_try.py** dan klien OpenSSH. | Port 22/TCP (Akun `root` dan `sec_admin`) | Akses login user `root` ditolak; login berbasis kata sandi ditolak (*publickey authentication*); laju koneksi konkuren dibatasi firewall. |
| **RT-03** | *Web & Protokol IoT* | Pengiriman pesan kontrol relay pompa tanpa hak akses (*unauthorized publish*) via **mqtt_pub.py** dan injeksi data sensor di luar rentang via **cURL**. | Topik `cow-sprinkler-01/control` (MQTT 1883) dan endpoint REST API telemetri | Pesan pada topik kontrol ditolak broker dengan kode CONNACK 5; data sensor di luar batas wajar ditolak API dengan kode HTTP 400. |
| **RT-04** | *Replay Attack* | Perekaman paket kontrol pompa yang valid, lalu dikirimkan ulang ke broker MQTT (*replay*) saat jadwal penyiraman tidak aktif. | Broker MQTT `192.168.12.5:1883` pada kanal kontrol | Pesan usang ditolak atau diabaikan oleh sistem karena ketidaksesuaian stempel waktu, dan percobaan tercatat pada log. |

---

## IV. Detail Prosedur Pengujian

### 1. Skenario RT-01: Pemindaian Port dan Banner Layanan (*Reconnaissance*)
* **Alasan Pengujian:** Mengetahui sejauh mana informasi layanan pada Target Node dapat dibaca oleh pihak luar jaringan.
* **Langkah Kerja:**
  1. Menjalankan pemindaian TCP stealth dan deteksi layanan:
     ```bash
     nmap -sS -sV -O -p 22,80,1883,9000 192.168.12.5
     ```
  2. Memeriksa respon banner header web server:
     ```bash
     curl -I http://192.168.12.5/
     ```
* **Hasil Pengamatan Lapangan:**
  - *Sebelum Hardening:* Port 9000 dapat diakses langsung dari VM Attacker dan Nginx menampilkan informasi lengkap `nginx/1.18.0 (Arch Linux)`.
  - *Sesudah Hardening:* Port 9000 berstatus *filtered* karena dibatasi hanya pada localhost, dan respon Nginx hanya menampilkan `Server: nginx`.

---

### 2. Skenario RT-02: Pengujian Autentikasi dan Pembatasan Sesi SSH (*Exploitation*)
* **Alasan Pengujian:** Menguji ketahanan akses terminal dari ancaman tebakan kata sandi berulang dan serangan pembukaan sesi massal.
* **Langkah Kerja:**
  1. Menjalankan percobaan autentikasi berulang pada akun `root` dan `sec_admin`:
     ```bash
     python3 /home/smartcow-lab/ssh_try.py 192.168.12.5 root:kel12admin sec_admin:kel12admin
     ```
  2. Menjalankan 8 percobaan koneksi secara serentak untuk menguji batas koneksi:
     ```bash
     for i in {1..8}; do ssh -o BatchMode=yes sec_admin@192.168.12.5 & done
     ```
* **Hasil Pengamatan Lapangan:**
  - *Sebelum Hardening:* Akun `sec_admin` dapat login menggunakan kata sandi sederhana tanpa ada pembatasan jumlah sesi serentak.
  - *Sesudah Hardening:* Login kata sandi langsung ditolak dengan pesan `Permission denied (publickey)`, dan koneksi paralel berlebih diredam oleh iptables dan konfigurasi sshd.

---

### 3. Skenario RT-03: Pengiriman Perintah Ilegal dan Manipulasi Data IoT (*Protocol Vulnerability*)
* **Alasan Pengujian:** Menguji otorisasi kanal komunikasi MQTT agar aktuator relay sprinkler tidak dapat dikendalikan sembarangan.
* **Langkah Kerja:**
  1. Mengirim perintah menghidupkan sprinkler ke broker MQTT tanpa kredensial yang sah:
     ```bash
     python3 /home/smartcow-lab/mqtt_pub.py 192.168.12.5 1883 cow-sprinkler-01/control '{"manualSsr":"on"}'
     ```
  2. Mengirimkan data telemetri palsu dengan nilai kelembapan 150% ke endpoint REST:
     ```bash
     curl -X PUT "http://192.168.12.5/devices/cow-sprinkler-01/telemetry/latest.json?auth=kel12-secret-token" \
          -H "Content-Type: application/json" \
          -d '{"humidity": 150, "temperature": 28.5}'
     ```
* **Hasil Pengamatan Lapangan:**
  - *Sebelum Hardening:* Broker MQTT mengizinkan publikasi pesan dari klien anonim, dan API menerima kelembapan 150% tanpa validasi.
  - *Sesudah Hardening:* Broker menolak koneksi dengan pesan `CONNACK return code 5`, dan REST API mengembalikan respon `HTTP 400 Bad Request`.

---

### 4. Skenario RT-04: Pengujian Serangan Pengulangan Paket (*Replay Attack*)
* **Alasan Pengujian:** Memastikan perintah kendali pompa yang disadap tidak dapat dipakai kembali di lain waktu untuk memanipulasi jadwal penyiraman kandang.
* **Langkah Kerja:**
  1. Menangkap paket data perintah pompa yang sah saat siklus normal berjalan.
  2. Mengirimkan kembali paket yang persis sama ke broker MQTT saat sistem dalam status istirahat (*idle*).
* **Hasil Pengamatan Lapangan:**
  - Payload yang dikirim ulang tercatat sebagai anomali pada log sistem dan verifikasi parameter waktu menggagalkan eksekusi berulang pada relay.

---

## V. Alur Kerja Purple Team

Pelaksanaan pengujian keamanan ini menggunakan siklus kerja sama antara penyerang dan pihak bertahan:

```text
[ 1. Eksekusi Serangan ] --> [ 2. Pemeriksaan Deteksi ] --> [ 3. Analisis Hasil ]
       (Red Team)                   (Security Onion)              (Evaluasi Tim)
                                                                        |
[ 5. Pengujian Ulang   ] <-- [ 4. Penerapan Mitigasi  ] <---------------+
       (Verifikasi)                   (Blue Team)
```

1. **Eksekusi Serangan:** Red Team menjalankan skenario pengujian sesuai daftar yang telah ditentukan dan mencatat waktu eksekusi.
2. **Pemeriksaan Deteksi:** Blue Team memeriksa apakah aktivitas tersebut memunculkan alert di Security Onion (Snort/Sguil) atau log Target Node.
3. **Analisis Hasil:** Kedua tim membahas apakah kontrol keamanan yang ada sudah cukup menahan serangan atau masih memiliki celah.
4. **Penerapan Mitigasi:** Blue Team menambahkan konfigurasi perbaikan yang dibutuhkan (firewall, aturan ACL broker, atau validasi input).
5. **Pengujian Ulang:** Red Team mengulang pengujian yang sama untuk memastikan bahwa serangan tidak lagi berhasil.

Seluruh tangkapan layar bukti eksekusi disimpan di folder `docs/redteam/evidence/`. Rekapitulasi hasil pengujian dicatat secara bertahap pada berkas [docs/purple-team-log.md](../purple-team-log.md).

---

## VI. Batasan Ruang Lingkup Pengujian

1. **Keamanan Sistem:** Pengujian tidak menggunakan serangan Denial of Service (DoS) yang mematikan VM secara permanen, dan tidak memasang malware perusak.
2. **Keterisolasian Jaringan:** Seluruh pengujian dibatasi hanya pada subnet `192.168.12.0/24`. Layanan cloud Firebase dan kandang peternakan mitra tidak diakses sama sekali.
3. **Integritas Konfigurasi:** Pengaturan hardening yang sudah aktif tetap dipertahankan, kecuali pada saat demonstrasi terencana untuk membandingkan kondisi sebelum dan sesudah perbaikan.
