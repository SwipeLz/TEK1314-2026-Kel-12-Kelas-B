# Attack plan - pengujian keamanan backend IoT

**Kelompok 12 | TEK1314 - PBL Keamanan Siber | Fase 2**

## 1. Tujuan

Pengujian ini mengevaluasi keamanan replika backend sistem sprinkler kandang
sapi. Fokusnya paparan layanan, autentikasi masuk ke Target Node, dan
perlindungan data yang seharusnya hanya bisa ditulis perangkat dan dashboard.

Dokumen memuat tiga skenario dari tiga kategori berbeda. Semuanya diarahkan ke
replika di lab, memakai data dummy, dan tidak menyentuh Firebase produksi
maupun perangkat di kandang mitra. Ketiganya sudah dieksekusi pada checkpoint
Minggu 9 untuk memastikan kontrol yang dipasang benar-benar bekerja.

## 2. Lingkungan pengujian

| Komponen | Keterangan |
| --- | --- |
| Attacker | ATTACKER-KEL12-B, LabVM Ubuntu 22.04, `192.168.12.100` |
| Target | SRV-IOT-KEL12-B, Arch Linux, `192.168.12.5`, replika `smartcow-lab` |
| Monitoring | SOC-KEL12-B, Security Onion, `192.168.12.200` |
| Layanan yang diuji | SSH `22`, dashboard dan proxy API `80`, broker MQTT `1883`, API replika `9000` |
| Aplikasi | Replika REST bergaya Firebase RTDB pada path `devices/cow-sprinkler-01/...` |
| Data | Seluruhnya dummy, ditulis simulator tiap dua detik |
| Batas | Jaringan Host-Only, tanpa akses internet, tanpa akses ke sistem nyata |

## 3. Rencana skenario

| ID | Kategori | Skenario dan tools | Target | Hasil yang diharapkan |
| --- | --- | --- | --- | --- |
| RT-01 | Reconnaissance | Pemindaian port memakai **nmap** (`-sS -sV -O`), **tcpdump** dan **Wireshark** untuk membaca paket | TCP `22`, `80`, `1883`, `9000` di `192.168.12.5` | Port yang benar-benar terbuka terpetakan, versi layanan terlihat, trafik yang tidak diizinkan tidak terlihat dari jaringan |
| RT-02 | Exploitation dan akses | Percobaan login berulang memakai **nmap NSE ssh-brute**; lab offline tidak punya `sshpass`, jadi skrip klien sendiri `ssh_try.py` dipakai | Akun `root` dan `sec_admin` pada SSH `22` | Kredensial yang bocor ditolak, `root` tidak pernah bisa masuk, koneksi paralel dibatasi |
| RT-03 | Web, API, dan protokol IoT | Publish ke topik MQTT memakai **mosquitto_pub** atau **MQTT Explorer**, digantikan skrip `mqtt_pub.py`; suntik data memakai **curl** | Topik `cow-sprinkler-01/control` di broker `1883`, endpoint `devices/cow-sprinkler-01/{telemetry/latest,control}` | Publish ke topik perintah ditolak, nilai di luar rentang ditolak, penulisan tanpa token ditolak |

### RT-01 - Pemetaan layanan

Skenario ini beralas dari temuan Minggu 4 soal port yang perlu dibuka, yaitu 22,
80, 1883, 21, 23, dan 3306. Red Team memindai port dan mengidentifikasi versi
layanannya. Blue Team membandingkan hasilnya dengan aturan firewall dan daftar
listener di Target Node. Security Onion dipakai untuk observesinya.

Hasil eksekusi: port 22, 80, dan 1883 terbuka, dengan OpenSSH 8.4 dan nginx
1.18.0 teridentifikasi. Port 9000 terbaca filtered karena firewall tidak pernah
mengizinkan port itu, meski API-nya masih mendengarkan di semua antarmuka.

### RT-02 - Percobaan autentikasi berulang

Skenario ini menguji risiko tebakan kata sandi. Empat kombinasi diuji: `root`
dengan kata sandi lab, `sec_admin` dengan kata sandi lab, dan dua kata sandi
salah. Jumlah percobaan dibatasi, lalu Blue Team memeriksa log autentikasi
Target Node.

Hasil eksekusi: sebelum hardening, `sec_admin` berhasil masuk dengan kata sandi
lab dan `root` ditolak. Sesudah hardening, keempat kombinasi ditolak dengan
`Permission denied (publickey)`, dan delapan koneksi paralel dari penyerang
membentur batas laju di firewall.

### RT-03 - Manipulasi data dan publish tanpa izin

Skenario ini menguji celah yang paling dekat dengan risiko di proyek asli.
Firmware asli menyisipkan Database Secret di dalam sketch, dan siapa pun yang
memegangnya bisa menulis apa saja ke RTDB. Di lab, dua arah diuji: publish ke
topik perintah MQTT, dan suntik data lewat endpoint REST.

Hasil eksekusi: sebelum hardening, publish anonim ke topik `control` diterima,
dan `PUT` dengan kelembapan 150 serta perintah `manualSsr: on` juga diterima.
Sesudah hardening, publish ditolak dengan CONNACK 5, nilai di luar rentang
ditolak dengan HTTP 400, penulisan tanpa token ditolak dengan HTTP 401, dan
token yang bocor ditolak karena sudah dirotasi.

## 4. Pengamatan dan evaluasi

Setiap skenario mengikuti lima tahap Purple Team: pengujian pada kondisi saat
ini, deteksi, analisis, respons, lalu pengujian ulang dengan skenario yang sama.

- **Red Team** menjalankan pengujian dan mencatat hasil aktual.
- **Blue Team** menganalisis log, memverifikasi kontrol, menerapkan perbaikan,
  lalu memulihkan layanan.
- **Monitoring** mengamati trafik dan alert lewat Security Onion.
- **Lead** mengoordinasikan pelaksanaan dan kelengkapan dokumentasi.

Bukti berupa tangkapan layar terminal asli ada di `docs/redteam/evidence/`.
Analisis dan hasil kelima tahap tercatat di
[docs/purple-team-log.md](../purple-team-log.md). Bila alert tidak muncul, itu
dicatat sebagai temuan, bukan dianggap terdeteksi.

## 5. Batasan dan status

Pengujian hanya diarahkan ke replika Target Node, memakai data dummy, dan tanpa
DoS, malware, atau tindakan terhadap sistem mitra. Kontrol hardening yang sudah
aktif tidak dimatikan untuk membuat serangan terlihat berhasil, kecuali bagian
demonstrasi yang memang dicatat sebagai kondisi sebelum.

Yang belum dieksekusi dan masih ada di rencana Fase 2: pengujian ARP spoofing
di lapisan jaringan lokal, evaluasi rules Firebase RTDB asli, serta pengujian
rotasi Database Secret pada sistem produksi di luar lingkup lab.

**Status skenario: RT-01, RT-02, dan RT-03 dieksekusi pada 20 Oktober 2026.**
Keluarannya menjadi isi Vulnerability Assessment Report di Minggu 11.
