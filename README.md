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
| [docs/design/topology.png](docs/design/topology.png) | Diagram topologi jaringan lab (Target, Attacker, Monitoring) |
| [docs/presentation-minggu9/tech_stack_declaration.md](docs/presentation-minggu9/tech_stack_declaration.md) | Deklarasi arsitektur teknologi asli dan pemetaannya ke lab |
| [docs/presentation-minggu9/slides.pdf](docs/presentation-minggu9/slides.pdf) | Salinan berkas slide presentasi evaluasi Minggu 9 |
| [docs/blueteam/hardening_checklist.md](docs/blueteam/hardening_checklist.md) | Dokumentasi 9 kontrol hardening beserta bukti verifikasi |
| [docs/blueteam/evidence/](docs/blueteam/evidence/) | Tangkapan layar terminal sebelum dan sesudah hardening |
| [docs/redteam/attack_plan.md](docs/redteam/attack_plan.md) | Rancangan skenario serangan Red Team (RT-01 s.d. RT-04) |
| [docs/redteam/evidence/](docs/redteam/evidence/) | Bukti keluaran eksekusi pengujian penyerangan |
| [docs/purple-team-log.md](docs/purple-team-log.md) | Catatan siklus 5 tahap Purple Team Loop dan evaluasi deteksi |

## Alur Penelusuran Dokumen

Penelusuran dokumentasi dapat dilakukan secara berurutan sesuai alur berikut:

1. [ip_plan.md](docs/design/ip_plan.md) - Meninjau rancangan topologi jaringan, subnetting, dan penetapan fungsi setiap mesin virtual.
2. [tech_stack_declaration.md](docs/presentation-minggu9/tech_stack_declaration.md) - Memahami arsitektur sistem SmartCow dan dasar pemilihan replika backend lab.
3. [hardening_checklist.md](docs/blueteam/hardening_checklist.md) - Memeriksa implementasi sembilan kontrol pengamanan Blue Team pada Target Node.
4. [attack_plan.md](docs/redteam/attack_plan.md) dan [purple-team-log.md](docs/purple-team-log.md) - Menelaah skenario pengujian penyerangan dan evaluasi hasil deteksi pada sensor Security Onion.

## Ringkasan Proyek

- **Lingkungan Uji:** Tiga mesin virtual terisolasi pada jaringan Host-Only (192.168.12.0/24).
- **Pertahanan Blue Team:** Sembilan kontrol pengamanan aktif (tiga Access, tiga Service, tiga Data/Application).
- **Pengujian Red Team:** Empat skenario pengujian terencana (Reconnaissance, Brute Force SSH, Injeksi REST & Unauthorized MQTT Publish, serta Replay Attack).
- **Validasi Purple Team:** Siklus evaluasi lima tahap berbasis sensor Snort/Sguil dan audit log lokal.
- **Integritas Pengujian:** Seluruh pengujian menggunakan data dummy tanpa menyentuh perangkat maupun server produksi.

## Ruang Lingkup Repositori

Repositori ini disusun mengikuti struktur direktori yang ditetapkan dalam Panduan PBL Minggu 9 secara presisi (`docs/design`, `docs/presentation-minggu9`, `docs/blueteam`, `docs/redteam`, dan `docs/purple-team-log.md`). Dokumentasi pelengkap seperti naskah presentasi, lembar catatan latihan, dan prosedur pengujian insiden internal disimpan pada direktori kerja kelompok di luar repositori publik ini.

Setiap pernyataan teknis dan hasil pengujian yang disajikan dalam repositori maupun slide presentasi dapat diverifikasi secara langsung melalui tangkapan layar terminal asli yang terlampir.

## Akses Lingkungan Lab

| Peran | Alamat IP | Pengguna | Metode Akses |
| :--- | :--- | :--- | :--- |
| Blue Team | 192.168.12.5 | sec_admin | Kunci kriptografis SSH (login berbasis kata sandi dinonaktifkan) |
| Red Team | 192.168.12.100 | analyst | Kata sandi lingkungan lab |
| Monitoring | 192.168.12.200 | analyst | Kata sandi lingkungan lab |

Akses administratif ke Target Node dikunci menggunakan autentikasi kunci publik Ed25519. Kredensial kata sandi default telah dinonaktifkan dan token otentikasi API telah dirotasi.
