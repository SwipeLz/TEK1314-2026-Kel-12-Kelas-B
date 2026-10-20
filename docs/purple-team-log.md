# Purple team log - Kelompok 12

Log ini mengikuti lima tahap pada Bagian X Panduan PBL. Satu aturan yang dipakai:
skenario yang tercatat berhasil pada tahap 1 harus berakhir gagal pada tahap 5.

Status per 20 Oktober 2026: ketiga skenario sudah lewat kelima tahap. Bukti
alert Security Onion untuk trafik Minggu 9 belum masuk, karena VM Onion tidak
dapat diakses dari host. Deteksi pada tahap 2 untuk sementara bersumber dari log
di Target Node, dan ditandai sebagai temuan, bukan dianggap lengkap.

## Skenario 1 - RT-01 pemetaan layanan

| Tahap | Red team | Blue team | Bukti | Hasil |
| --- | --- | --- | --- | --- |
| 1. Serang | `nmap -sS -sV -O` ke 192.168.12.5, seluruh port diperiksa | Mengamati trafik di Security Onion | `evidence/01-pemindaian-port-sebelum.png` | 22, 80, dan 1883 terbuka dengan OpenSSH 8.4 serta nginx 1.18.0; 9000 filtered |
| 2. Deteksi | Lanjut ke tahap berikutnya | Membandingkan hasil scan dengan daftar listener dan aturan firewall | `evidence/01-pemindaian-port-sebelum.png` dan `blueteam/evidence/kontrol B1 - Firewall whitelist dan persisten/iptables-sebelum.png` | Hasil scan cocok dengan listener. Port 9000 terbaca filtered karena firewall tidak pernah mengizinkannya |
| 3. Analisis | Menjelaskan apa yang dipetakan: empat port yang dipakai, versi layanan, dan sistem operasi Linux | Menemukan akar masalah: API replika mendengarkan di semua antarmuka sehingga cukup satu aturan firewall yang hilang untuk membukanya | Catatan di dokumen ini | Satu lapisan saja, yaitu firewall, yang menahan port 9000 |
| 4. Respons | Tidak melakukan apa-apa | Memindahkan API ke loopback dan menambah lapisan kedua | `blueteam/evidence/kontrol B2 - API hanya mendengarkan di loopback/listener-setelah.png` | Listener berubah dari `0.0.0.0:9000` menjadi `127.0.0.1:9000` |
| 5. Verifikasi | Mengulang pemindaian penuh | Memastikan port 9000 tetap tidak terjangkau dan layanan lain tetap hidup | `evidence/11-pemindaian-port-lengkap.png` | 9000 tetap filtered, port 22, 80, 1883 tetap terbuka untuk segmen lab, dashboard tetap HTTP 200 |

## Skenario 2 - RT-02 percobaan autentikasi berulang

| Tahap | Red team | Blue team | Bukti | Hasil |
| --- | --- | --- | --- | --- |
| 1. Serang | Empat kombinasi kredensial dicoba lewat `ssh_try.py`: `root` dan `sec_admin` dengan kata sandi lab, plus dua kata sandi salah | Mengamati log autentikasi Target Node | `evidence/03-percobaan-login-sebelum.png` | `sec_admin` berhasil masuk dengan kata sandi lab, `root` ditolak |
| 2. Deteksi | Mencoba login berikutnya | Membaca log sshd yang sudah `LogLevel VERBOSE` | `blueteam/evidence/kontrol A1 - Menolak login root langsung/sshd-efektif-sebelum.png` | Setiap percobaan tercatat lengkap dengan sumber dan hasilnya |
| 3. Analisis | Menjelaskan bahwa kata sandi lab yang bocor cukup untuk masuk | Akar masalah: autentikasi password masih diizinkan, batas percobaan masih longgar, dan tidak ada pembatas laju koneksi | Catatan di dokumen ini | Kata sandi yang bocor sama dengan akses penuh ke shell Target Node |
| 4. Respons | Tidak melakukan apa-apa | Memasang kunci publik, mematikan autentikasi password, mengecilkan `MaxStartups`, dan menambah rate limit iptables untuk penyerang | `blueteam/evidence/kontrol A2 - Login SSH berbasis kunci/kunci-publik-terpasang.png` dan `blueteam/evidence/kontrol A3 - Pembatasan percobaan login/sshd-maxstartups-dan-rate-limit.png` | `PasswordAuthentication no`, `MaxStartups 3:50:10`, aturan hashlimit 3 koneksi per detik dari 192.168.12.100 |
| 5. Verifikasi | Mengulang empat kombinasi yang sama, lalu membuka delapan koneksi paralel | Memastikan semua ditolak dan zahl koneksi dibatasi | `evidence/04-percobaan-login-setelah.png` dan `evidence/10-uji-rate-limit-koneksi.png` | Keempat kombinasi ditolak dengan `Permission denied (publickey)`, koneksi paralel sebagian ditolak |

## Skenario 3 - RT-03 publish tanpa izin dan suntik data

| Tahap | Red team | Blue team | Bukti | Hasil |
| --- | --- | --- | --- | --- |
| 1. Serang | Publish ke topik `cow-sprinkler-01/control` tanpa kredensial, lalu `PUT` telemetri dengan kelembapan 150 dan perintah `manualSsr: on` | Mengamati log aplikasi dan log broker | `evidence/05-publish-mqtt-sebelum.png` dan `evidence/08-suntik-telemetri-rest-sebelum.png` | Publish diterima, data palsu tersimpan dengan `h1` 150, dan perintah sprinkler manual diterima |
| 2. Deteksi | Melanjutkan uji | Membaca `access.log` dan `broker.log`, keduanya aktif sejak hardening | `blueteam/evidence/kontrol C3 - Logging aktivitas dan backup data/log-akses-aplikasi.png` | Setiap permintaan tercatat, termasuk yang ditolak |
| 3. Analisis | Menjelaskan bahwa publish ke topik perintah berarti penyerang bisa menyalakan semprotan | Akar masalah: broker menerima koneksi anonim tanpa ACL topik, dan API tidak memvalidasi rentang sensor | Catatan di dokumen ini | Pola ini meniru firmware asli yang menyisipkan Database Secret di dalam sketch, sehingga siapa pun yang punya secret bisa menulis apa saja |
| 4. Respons | Tidak melakukan apa-apa | Mengaktifkan validasi input, mewajibkan kredensial broker, membatasi topik yang boleh ditulis, memperketat permission berkas kredensial, dan merotasi token yang bocor | `blueteam/evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/validasi-input-setelah.png` dan `blueteam/evidence/kontrol C2 - Kredensial tidak hardcoded/kredensial-setelah.png` | Validasi aktif, kredensial wajib, topik `control` tidak bisa ditulis, token lama ditolak |
| 5. Verifikasi | Mengulang publish dan suntik yang sama | Memastikan penulisan yang sah tetap jalan | `evidence/06-publish-mqtt-tanpa-kredensial-setelah.png`, `evidence/09-suntik-telemetri-rest-setelah.png`, `blueteam/evidence/kontrol C1 - Validasi input API dan ACL topik MQTT/mqtt-acl-terverifikasi.png` | Publish ditolak dengan CONNACK 5, nilai di luar rentang ditolak dengan HTTP 400, penulisan tanpa token ditolak dengan HTTP 401, data sah tetap diterima |

## Yang belum lengkap

- Bukti alert Security Onion untuk trafik Minggu 9 belum masuk. Penyebabnya
  teknis: antarmuka management VM Onion tidak menjawab ARP dari host dan VM itu
  tidak punya SSH server maupun Guest Additions, sehingga sensor hanya bisa
  dilihat lewat layar di dalam VM.
- Skenario ARP spoofing di lapisan jaringan lokal belum dieksekusi. Rencana
  lengkapnya ada di attack plan untuk Fase 2.
- Evaluasi rules Firebase RTDB asli belum dilakukan. Yang diuji di lab adalah
  pola validasi dan aturan aksesnya, bukan rules aslinya.
