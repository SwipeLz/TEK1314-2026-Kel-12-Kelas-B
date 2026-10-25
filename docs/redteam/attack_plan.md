# Rencana Pengujian Penetrasi & Simulasi Ancaman Siber (Fase 2)

**Kelompok 12 | Kelas B | Praktik Keamanan Siber Terapan (TEK1314)**  
**Skenario Proyek:** No. 10  -  *IoT Protocol Guardian* (Proteksi Backend Sprinkler Kandang Sapi)  
**Target Pengujian:** `SRV-IOT-KEL12-B` (Arch Linux  -  `192.168.12.5`)  

---

## I. Konteks Pengujian & Latar Belakang Ancaman

Dokumen ini memuat panduan operasional Red Team dalam menguji ketahanan arsitektur backend replika SmartCow selama siklus Fase 2. Sistem yang diuji merupakan pengendali otomatis pendingin kandang sapi perah yang mengandalkan transmisi data telemetri suhu/kelembapan serta jalur kendali aktuator relay pompa air 220V.

Berdasarkan penetapan **Skenario 10 (*IoT Protocol Guardian*)**, fokus utama pengujian diarahkan pada kerentanan protokol IoT, khususnya risiko pembajakan topik (*unauthorized publish*), injeksi data telemetri palsu, dan serangan pengulangan paket (*replay attack*) yang berpotensi memicu kegagalan fisik perangkat sprinkler atau *heat stress* pada hewan ternak.

Pengujian dirancang secara terukur untuk memverifikasi apakah kontrol pertahanan (*hardening*) Blue Team berfungsi optimal, sekaligus menyiapkan basis deteksi bagi sensor Snort di Security Onion.

---

## II. Profil Lingkungan & Parameter Simulasi

Simulasi berjalan penuh pada segmen jaringan terisolasi *Host-Only* (`192.168.12.0/24`) tanpa koneksi ke internet maupun infrastruktur peternakan mitra.

| Parameter Sistem | Deskripsi Teknis |
|---|---|
| **Simulasi Penyerang (Attacker)** | `ATTACKER-KEL12-B` (Ubuntu 22.04 LTS / IP `192.168.12.100`), dilengkapi utilitas audit jaringan, injeksi protokol, dan otomasi pengujian kredensial. |
| **Node Sasaran (Target Node)** | `SRV-IOT-KEL12-B` (Arch Linux / IP `192.168.12.5`), menjalankan tumpukan aplikasi `smartcow-lab` (Broker MQTT paho, REST API Python Flask, dan Web Reverse Proxy Nginx). |
| **Pusat Pengawasan (SOC/SIEM)** | `SOC-KEL12-B` (Security Onion / IP Manajemen `192.168.12.200`), memantau lalu lintas jaringan secara pasif melalui antarmuka *sniffing* sensor Snort/Sguil. |
| **Layanan Terpapar** | Port 22/TCP (OpenSSH), Port 80/TCP (HTTP Dashboard & Proxy API), Port 1883/TCP (MQTT Message Broker), Port 9000/TCP (Backend REST Internal). |
| **Karakteristik Data** | Data telemetri sintetis (suhu 24-30 derajat C, kelembapan 70-85%) yang diproduksi oleh simulator internal setiap 2 detik. |

---

## III. Matriks Perencanaan Skenario Serangan

Mengacu pada ketentuan Bagian IX Panduan PBL TEK1314, Red Team merancang empat vektor serangan lintas kategori untuk mengevaluasi lapisan perimeter hingga lapisan data:

| ID Vektor | Kategori Serangan | Deskripsi Skenario & Utilitas | Target Spesifik | Kriteria Keberhasilan Pertahanan |
|---|---|---|---|---|
| **RT-01** | *Reconnaissance* | Pemetaan port aktif, enumerasi sidik jari sistem operasi (*OS fingerprinting*), dan audit keterpaparan banner layanan via **Nmap** (`-sS -sV -O`). | Seluruh port TCP pada `192.168.12.5` | Layanan backend internal (9000) tidak dapat dijangkau dari luar; header respons HTTP Nginx tidak membocorkan nomor versi rilis. |
| **RT-02** | *Exploitation & Access* | Eksploitasi kelemahan autentikasi administratif melalui serangan kamus (*dictionary brute-force*) dan banjir koneksi paralel via **ssh_try.py** serta utilitas OpenSSH. | Port 22/TCP (Akun `root` dan `sec_admin`) | Login langsung `root` ditolak mutlak; seluruh autentikasi berbasis kata sandi gagal (*publickey required*); koneksi konkuren dibatasi oleh firewall. |
| **RT-03** | *Web, API & Protokol IoT* | Penetrasi kendali tanpa izin (*unauthorized publish*) ke kanal kontrol sprinkler dan manipulasi muatan telemetri via **mqtt_pub.py** dan **cURL**. | Broker MQTT port 1883 (`cow-sprinkler-01/control`) & API `/devices/cow-sprinkler-01/telemetry/latest` | Pengiriman data ke topik kontrol ditolak dengan kode CONNACK 5 (*Not Authorized*); pengiriman data sensor di luar batas fisik ditolak dengan status HTTP 400. |
| **RT-04** | *Availability & Replay* | Penyadapan paket kontrol MQTT yang sah, dilanjutkan dengan injeksi ulang muatan paket secara berulang (*replay attack*) untuk memanipulasi siklus pompa. | Kanal telemetri & kendali broker MQTT `192.168.12.5:1883` | Sistem mendeteksi anomali duplikasi token waktu (*timestamp nonce*); percobaan injeksi perintah usang digagalkan sebelum dieksekusi aktuator. |

---

## IV. Rincian Teknis & Prosedur Pelaksanaan

### 1. Skenario RT-01: Audit Keterpaparan Port & Sidik Jari Layanan (*Reconnaissance*)
* **Rasional Celah:** Menilai sejauh mana penyerang luar dapat memetakan arsitektur Target Node untuk mencari celah perangkat lunak usang.
* **Prosedur Pengujian:**
  1. Red Team menjalankan pemindaian SYN stealth dan deteksi versi layanan:
     ```bash
     nmap -sS -sV -O -p 22,80,1883,9000 192.168.12.5
     ```
  2. Menginspeksi *banner header* yang dikembalikan oleh layanan web:
     ```bash
     curl -I http://192.168.12.5/
     ```
* **Hasil Pengamatan (Kondisi Teruji):**
  - *Sebelum Hardening:* Port 9000 terbuka secara publik dan banner Nginx menampilkan rilis lengkap `nginx/1.18.0 (Arch Linux)`.
  - *Sesudah Hardening:* Port 9000 berstatus *filtered* (diisolasi ke loopback `127.0.0.1`), sedangkan respons Nginx hanya menampilkan tanda generik `Server: nginx`.

---

### 2. Skenario RT-02: Pengujian Ketahanan Akses Administratif SSH (*Exploitation*)
* **Rasional Celah:** Percobaan pengambilalihan hak akses terminal konsol melalui tebakan kredensial default dan serangan laju tinggi.
* **Prosedur Pengujian:**
  1. Menjalankan pengujian autentikasi menggunakan akun `root` dan `sec_admin` dengan berbagai kata sandi lab:
     ```bash
     python3 /home/smartcow-lab/ssh_try.py 192.168.12.5 root:kel12admin sec_admin:kel12admin
     ```
  2. Meluncurkan 8 sesi konkuren secara serempak guna menguji mekanisme *rate limiting*:
     ```bash
     for i in {1..8}; do ssh -o BatchMode=yes sec_admin@192.168.12.5 & done
     ```
* **Hasil Pengamatan (Kondisi Teruji):**
  - *Sebelum Hardening:* Akun `sec_admin` berhasil masuk menggunakan kata sandi teks biasa; tidak ada pembatasan laju koneksi.
  - *Sesudah Hardening:* Seluruh sesi kata sandi ditolak seketika dengan respon `Permission denied (publickey)`; lonjakan koneksi paralel diredam oleh aturan `MaxStartups` dan modul *hashlimit* iptables.

---

### 3. Skenario RT-03: Pelanggaran Batas Input & Otorisasi Kanal IoT (*Protocol Hijack*)
* **Rasional Celah:** Menguji kerentanan otentikasi lemah pada tumpukan IoT, di mana penyerang berupaya mempublikasikan instruksi liar ke topik aktuator relay pompa.
* **Prosedur Pengujian:**
  1. Mengirimkan instruksi pemaksaan relay aktif ke topik kendali menggunakan kredensial sensor biasa:
     ```bash
     python3 /home/smartcow-lab/mqtt_pub.py 192.168.12.5 1883 cow-sprinkler-01/control '{"manualSsr":"on"}'
     ```
  2. Menyuntikkan data sensor ekstrem (kelembapan 150%) melalui antarmuka REST API:
     ```bash
     curl -X PUT "http://192.168.12.5/devices/cow-sprinkler-01/telemetry/latest.json?auth=kel12-secret-token" \
          -H "Content-Type: application/json" \
          -d '{"humidity": 150, "temperature": 28.5}'
     ```
* **Hasil Pengamatan (Kondisi Teruji):**
  - *Sebelum Hardening:* Broker MQTT menerima data tanpa otorisasi ACL; REST API menyimpan kelembapan 150% ke dalam database.
  - *Sesudah Hardening:* Broker MQTT memutuskan koneksi dengan penolakan `CONNACK return code 5`; REST API menolak payload ekstrem dengan kode `HTTP 400 Bad Request`.

---

### 4. Skenario RT-04: Simulasi Serangan Pengulangan Protokol (*Replay Attack*)
* **Rasional Celah:** Menangkap lalu lintas transmisi data yang valid, kemudian memancarkannya kembali ke jaringan secara berulang tanpa modifikasi untuk mengelabui logika otomatisasi sprinkler.
* **Prosedur Pengujian:**
  1. Menyadap sampel muatan instruksi pompa yang sah di jaringan lokal.
  2. Memancarkan ulang paket yang sama secara beruntun (*replay burst*) saat siklus kandang seharusnya berada dalam mode *idle*.
* **Hasil Pengamatan (Kondisi Teruji):**
  - Validasi otentikasi token berhasil diverifikasi pada runbook skenario pengujian, dan sistem log mencatat aktivitas anomali duplikasi paket.

---

## V. Mekanisme Koordinasi Tim (*Purple Team Loop*)

Pengujian keamanan ini dijalankan dengan model kerja kolaboratif (*Purple Team*) yang mengintegrasikan eksekusi ofensif dan defensif dalam lima tahap:

```text
[ 1. Injeksi Serangan ] --> [ 2. Observasi Deteksi ] --> [ 3. Evaluasi Forensik ]
      (Red Team)                 (Security Onion)               (Purple Meeting)
                                                                       |
[ 5. Validasi Ulang   ] <-- [ 4. Penerapan Mitigasi  ] <---------------+
      (Verifikasi)                 (Blue Team)
```

1. **Injeksi Terkendali:** Red Team menjalankan vektor uji sesuai matriks dan mencatat stempel waktu pengujian.
2. **Inspeksi Sensor:** Blue Team meninjau *alert console* Sguil/Snort di Security Onion serta log sistem Target Node.
3. **Analisis Celah:** Mengidentifikasi akar masalah teknis mengapa sebuah serangan dapat menembus sistem atau lolos dari pantauan sensor.
4. **Perbaikan Berlapis:** Blue Team mengonfigurasi aturan mitigasi tambahan (iptables, ACL topik, modul sanitasi input).
5. **Konfirmasi Ketahanan:** Red Team mengulang skenario uji persis sama guna memastikan serangan berakhir dengan kegagalan total.

Seluruh dokumentasi bukti eksekusi berupa artefak tangkapan layar terminal disimpan secara sistematis pada direktori `docs/redteam/evidence/`. Log kemajuan penanganan antar-tim tercatat pada [docs/purple-team-log.md](../purple-team-log.md).

---

## VI. Batasan Etika & Integritas Pengujian

1. **Non-Destruktif:** Pengujian dilarang merusak integritas sistem operasi dasar atau memicu *kernel panic* pada VM lab.
2. **Isolasi Penuh:** Seluruh aktivitas pengujian dilarang diarahkan ke luar segmen IP `192.168.12.0/24`. Layanan Firebase produksi dan kandang mitra tidak disentuh dalam bentuk apa pun.
3. **Konsistensi Keamanan:** Konfigurasi hardening yang telah terbukti menangkis serangan tidak boleh dinonaktifkan kembali, kecuali dalam sesi demonstrasi komparasi *before/after* yang terkontrol.
