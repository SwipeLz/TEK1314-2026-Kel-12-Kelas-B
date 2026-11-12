# TEK1314-2026-KEL-12-Kelas-B

1. Thevan Erlangga (J0404241073) - Lead, Purple Team
2. Muhamad Akhdan Ramadhan (J0404241102) - Red Team
3. Fachri Abyasa Tarid (J0404241136) - Blue Team

Repositori ini memuat dokumentasi, konfigurasi, dan artefak pengujian keamanan sistem IoT SmartCow (pengendali sprinkler kandang sapi perah). Sistem asli menggunakan enam sensor suhu DS18B20 dan empat sensor kelembapan DHT22 yang terhubung ke dua mikrokontroler ESP32, backend Firebase Realtime Database, web dashboard, serta aktuator solenoid 220V berbasis relay.

Untuk keperluan praktikum keamanan siber, seluruh arsitektur backend direplikasi ke dalam lingkungan laboratorium virtual terisolasi pada subnet 192.168.12.0/24, kemudian diterapkan kontrol pengamanan (hardening) bertingkat pada Target Node.

Seluruh pengujian pertahanan dan simulasi serangan Red Team dijalankan secara bertahap menggunakan data sintetis (dummy). Pengujian ini tidak melibatkan perangkat keras di kandang mitra maupun layanan produksi Firebase.

## Peta Berkas Repositori

| Lokasi Berkas | Deskripsi Isi |
| :--- | :--- |
| [LOGBOOK.md](LOGBOOK.md) | Catatan logbook mingguan dan kronologi teknis pengerjaan |
| [docs/design/ip_plan.md](docs/design/ip_plan.md) | Skema pengalamatan IP, peran node, dan alokasi port layanan |
| [docs/design/topology-minggu9.png](docs/design/topology-minggu9.png) | Diagram topologi jaringan lab minggu 9 (Target, Attacker, Monitoring) |
| [docs/blueteam/baseline-report.md](docs/blueteam/baseline-report.md) | Baseline report fase 1 (minggu 7) beserta aset, hardening, dan bukti logging |
| [docs/blueteam/evidence/verifikasi-2026-11-12/README.md](docs/blueteam/evidence/verifikasi-2026-11-12/README.md) | Verifikasi ulang kontrol fase 2 dan daftar bukti teks 12 November 2026 |
| [docs/presentation-minggu9/tech_stack_declaration.md](docs/presentation-minggu9/tech_stack_declaration.md) | Deklarasi arsitektur teknologi asli dan pemetaannya ke lab |
| [Presentasi Minggu 9](docs/presentation-minggu9/README.md) | PDF dan pratinjau gambar delapan slide evaluasi Minggu 9 |
| [docs/blueteam/hardening_checklist.md](docs/blueteam/hardening_checklist.md) | Dokumentasi 9 kontrol hardening beserta bukti verifikasi |
| [docs/blueteam/evidence/](docs/blueteam/evidence/) | Bukti before/after hardening, tangkapan baseline, dan log verifikasi kontrol |
| [docs/redteam/attack_plan.md](docs/redteam/attack_plan.md) | Rancangan skenario serangan Red Team (RT-01 s.d. RT-04) |
| [docs/redteam/evidence/](docs/redteam/evidence/) | Bukti keluaran eksekusi pengujian penyerangan |
| [docs/purple-team-log.md](docs/purple-team-log.md) | Catatan siklus 5 tahap Purple Team Loop dan evaluasi deteksi |
| [scripts/smartcow-lab/](scripts/smartcow-lab/README.md) | Kode replika backend lab (REST API, broker MQTT, simulator, unit systemd) yang dipasang di Target Node |

## Alur Penelusuran Dokumen

Penelusuran dokumentasi dapat dilakukan secara berurutan sesuai alur berikut:

1. [ip_plan.md](docs/design/ip_plan.md) - Meninjau rancangan topologi jaringan, subnetting, dan penetapan fungsi setiap mesin virtual.
2. [baseline-report.md](docs/blueteam/baseline-report.md) - Membaca kondisi awal setelah hardening dan bukti logging minggu ke-5.
3. [tech_stack_declaration.md](docs/presentation-minggu9/tech_stack_declaration.md) - Memahami arsitektur sistem SmartCow dan dasar pemilihan replika backend lab.
4. [hardening_checklist.md](docs/blueteam/hardening_checklist.md) - Memeriksa implementasi sembilan kontrol pengamanan Blue Team pada Target Node.
5. [attack_plan.md](docs/redteam/attack_plan.md) dan [purple-team-log.md](docs/purple-team-log.md) - Menelaah skenario pengujian penyerangan dan evaluasi hasil deteksi pada sensor Security Onion.
6. [verifikasi-2026-11-12/README.md](docs/blueteam/evidence/verifikasi-2026-11-12/README.md) - Melihat hasil verifikasi ulang kontrol fase 2 beserta bukti teksnya.

## Ringkasan Proyek

- **Lingkungan Uji:** Tiga mesin virtual terisolasi pada jaringan Host-Only (192.168.12.0/24).
- **Pertahanan Blue Team:** Sembilan kontrol pengamanan aktif (tiga Access, tiga Service, tiga Data/Application).
- **Pengujian Red Team:** Empat skenario pengujian terencana (Reconnaissance, Brute Force SSH, Injeksi REST & Unauthorized MQTT Publish, serta Replay Attack).
- **Validasi Purple Team:** Siklus evaluasi lima tahap berbasis sensor Snort/Sguil dan audit log lokal.
- **Integritas Pengujian:** Seluruh pengujian menggunakan data dummy tanpa menyentuh perangkat maupun server produksi.

## Ruang Lingkup Repositori

Repositori ini disusun mengikuti struktur direktori yang ditetapkan dalam Panduan PBL Minggu 9 secara presisi (`docs/design`, `docs/presentation-minggu9`, `docs/blueteam`, `docs/redteam`, dan `docs/purple-team-log.md`). Dokumentasi pelengkap seperti naskah presentasi, lembar catatan latihan, dan prosedur pengujian insiden internal disimpan pada direktori kerja kelompok di luar repositori publik ini.

Setiap pernyataan teknis dan hasil pengujian disertai bukti tangkapan layar atau berkas log asli. Pemeriksaan ulang pada 12 November 2026 menemukan dua tangkapan layar lama yang isinya justru memperlihatkan kegagalan perintah, yaitu pada kontrol C1 dan C3; keduanya sudah diganti dengan bukti log eksekusi baru di `docs/blueteam/evidence/verifikasi-2026-11-12/` dan statusnya dicatat pada `hardening_checklist.md`.

## Akses Lingkungan Lab

| Peran | Alamat IP | Pengguna | Metode Akses |
| :--- | :--- | :--- | :--- |
| Blue Team | 192.168.12.5 | sec_admin | Kunci SSH Ed25519 (login berbasis kata sandi dinonaktifkan) |
| Red Team | 192.168.12.100 | analyst | Konsol VirtualBox atau `guestcontrol`; mesin juga punya SSH |
| Monitoring | 192.168.12.200 | analyst | Kunci SSH yang sama dengan lab |

Akses administratif ke Target Node dikunci menggunakan autentikasi kunci publik Ed25519. Kredensial kata sandi default telah dinonaktifkan dan token otentikasi API telah dirotasi. Ketiga alamat tersebut terverifikasi saling terhubung pada 12 November 2026 (`docs/blueteam/evidence/verifikasi-2026-11-12/03-topology-reachability.log`).

Kata sandi lingkungan lab tidak disimpan di repositori. Pada Target Node seluruh akun menolak login berkata sandi (`docs/blueteam/evidence/verifikasi-2026-11-12/08-password-login-rejected.log`); pada 12 November 2026 jalur kata sandi SSH juga ditutup pada Attacker Node dan Monitoring Node (`PasswordAuthentication no`), sehingga ketiga node hanya menerima `publickey` (`docs/blueteam/evidence/verifikasi-2026-11-12/15-ssh-password-auth-disabled.log`). Kata sandi akun sengaja tidak diubah supaya login konsol dan Sguil pada panduan demo tetap berlaku; rotasi kata sandi tetap menjadi keputusan pemilik lab, dan selama jalur SSH berbasis kata sandi tertutup nilainya tidak dapat dipakai masuk dari jaringan.
