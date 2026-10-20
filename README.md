# TEK1314-2026-KEL-12-Kelas-B

1. Thevan Erlangga (J0404241073) - Lead, Purple Team
2. Muhamad Akhdan Ramadhan (J0404241102) - Red Team
3. Fachri Abyasa Tarid (J0404241136) - Blue Team

Proyek IoT yang dilindungi: SmartCow, sistem sprinkler kandang sapi. Enam sensor
DS18B20 dan empat DHT22 di dua ESP32, backend Firebase Realtime Database,
dashboard web, dan solenoid 220V di belakang relay.

Checkpoint ini menyalin stack backend proyek itu ke lab terisolasi
192.168.12.0/24, lalu mengeraskan replikanya.

Sembilan kontrol sudah terpasang dan teruji. Tiga skenario serangan juga
dieksekusi, dari reconnaissance sampai publish tanpa izin.

Seluruh data yang dipakai adalah data dummy. Tidak ada permintaan yang pernah
menyentuh Firebase produksi atau perangkat di kandang mitra.

## Peta repo

| Path | Isi |
| --- | --- |
| [LOGBOOK.md](LOGBOOK.md) | Catatan kerja Minggu 2 sampai 9 |
| [docs/design/ip_plan.md](docs/design/ip_plan.md) | Alokasi IP dan layanan tiap node |
| [docs/design/topology.png](docs/design/topology.png) | Topologi Attacker, Target, Monitoring |
| [docs/presentation-minggu9/tech_stack_declaration.md](docs/presentation-minggu9/tech_stack_declaration.md) | Pemetaan stack asli ke replika lab |
| [docs/presentation-minggu9/slides.pdf](docs/presentation-minggu9/slides.pdf) | Slide presentasi Minggu 9 |
| [docs/blueteam/hardening_checklist.md](docs/blueteam/hardening_checklist.md) | Sembilan kontrol hardening beserta bukti |
| [docs/blueteam/evidence/](docs/blueteam/evidence/) | Tangkapan layar before dan after tiap kontrol |
| [docs/redteam/attack_plan.md](docs/redteam/attack_plan.md) | Tiga skenario serangan Fase 2 beserta tools |
| [docs/redteam/evidence/](docs/redteam/evidence/) | Hasil eksekusi serangan |
| [docs/purple-team-log.md](docs/purple-team-log.md) | Lima tahap Purple Team Loop per skenario |

## Alur Penelusuran Dokumen

Dokumentasi repositori ini dapat ditinjau berdasarkan alur penelusuran berikut:

1. [ip_plan.md](docs/design/ip_plan.md) — Topologi jaringan, pembagian pengalamatan IP, dan peran setiap node (Target, Attacker, dan Monitoring).
2. [tech_stack_declaration.md](docs/presentation-minggu9/tech_stack_declaration.md) — Arsitektur sistem IoT SmartCow dan pemetaan komponen ke replika lab.
3. [hardening_checklist.md](docs/blueteam/hardening_checklist.md) — Implementasi sembilan kontrol pengamanan Blue Team beserta bukti verifikasinya.
4. [attack_plan.md](docs/redteam/attack_plan.md) dan [purple-team-log.md](docs/purple-team-log.md) — Skenario pengujian serangan Red Team dan catatan evaluasi deteksi Purple Team Loop.

## Ringkas singkat

Satu lab berisi tiga VM.
Sembilan kontrol hardening terpasang.
Tiga skenario serangan dieksekusi.
Seluruh bukti tersimpan di repository.
Tiga fase, tiga folder.
Dokumen selalu dapat diperiksa ulang.

## Ruang lingkup repository

Repository ini mengikuti struktur folder yang diminta Panduan PBL Minggu 9 secara
persis, yaitu `docs/design`, `docs/presentation-minggu9`, `docs/blueteam`,
`docs/redteam`, dan `docs/purple-team-log.md`. Materi pembelajaran yang di luar
struktur tersebut, seperti catatan konfigurasi lengkap, simulasi insiden, dan
runbook gladi bersih, disimpan terpisah di folder belajar PBL kelompok dan belum
diunggah ke repository publik.

Repository ini disusun agar setiap klaim pada slide presentasi dapat ditelusuri
menuju berkas bukti yang menyertainya, sehingga pemeriksaan oleh dosen maupun
asdos dapat dilakukan tanpa perlu menjalankan ulang lingkungan lab, dan seluruh
angka yang dicantumkan dalam dokumen diambil langsung dari output perintah pada
ketiga VM, bukan dari estimasi.
## Akses lab

| Peran | Host | User | Cara masuk |
| --- | --- | --- | --- |
| Blue Team | 192.168.12.5 | sec_admin | login berbasis kunci, autentikasi password dimatikan |
| Red Team | 192.168.12.100 | analyst | kata sandi lab |
| Monitoring | 192.168.12.200 | analyst | kata sandi lab |

Target Node hanya bisa dimasuki dengan kunci. Kata sandi yang pernah bocor sudah
dinonaktifkan, dan token yang bocor sudah dirotasi.
