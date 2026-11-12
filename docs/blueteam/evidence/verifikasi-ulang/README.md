# Verifikasi Ulang Kontrol Fase 2

Folder ini memuat bukti teks verifikasi ulang kontrol pengamanan Fase 2 pada lingkungan lab yang benar-benar berjalan. Berkas dapat dibaca ulang tanpa menyalakan mesin virtual.

Seluruh berkas adalah keluaran perintah asli, bukan rekonstruksi. Nilai rahasia (token API, sandi akun broker, isi `.env`) tidak ikut tercetak.

## Daftar Isi

- [Daftar Berkas](#daftar-berkas)
- [Catatan Status dan Batasan](#catatan-status-dan-batasan)

## Daftar Berkas

| Berkas | Isi | Hasil |
| :--- | :--- | :--- |
| `01-c1-live-verification.log` | `c1_verify.py` dijalankan dua kali, langsung ke `127.0.0.1:9000` dan melalui Nginx `192.168.12.5:80` | 6 dari 6 lulus pada kedua jalur |
| `02-c3-backup-restore.log` | Backup harian, verifikasi pemulihan, dan uji gerbang dengan manifest yang dirusak | Backup `Succeeded`; pemulihan 4 dari 4 cocok; arsip rusak ditolak tanpa menyentuh data |
| `03-topology-reachability.log` | Ping dari host ke `192.168.12.5`, `.100`, dan `.200` | Ketiganya 0% loss |
| `04-onion-state.log` | Identitas dan antarmuka Monitoring Node | `SOC-KEL12-B`; `eth2` `192.168.12.200/24`; `eth0` promiscuous tanpa IP |
| `05-onion-ids-state.log` | Rantai deteksi di Security Onion | `snort`, `barnyard2`, `sguild` (`tclsh`), dan `mysqld` berjalan; rule SID 1000002 ada |
| `06-target-state-recon.log` | Kondisi Target Node sesudah perbaikan C3: sshd, iptables, listener, izin berkas, kunci `.env`, `/health` | Daftar arsip dipotong 10 baris; daftar lengkap ada pada `02-c3-backup-restore.log` |
| `07-backup-units-after.log` | Izin skrip dan status timer | Skrip `root:root` mode 750; timer `enabled` dan `active` |
| `08-password-login-rejected.log` | Login SSH dengan kata sandi lab untuk `root`, `sec_admin`, dan `analyst` | Ketiganya ditolak; hanya `publickey` diterima |
| `09-sguil-alerts.log` | Query basis data untuk seluruh alert `SMARTCOW%` | CID 6125, 6127, 6352, dan 6356 |
| `10-mqtt-credential-rotation.log` | Kredensial broker lama dan baru setelah rotasi | Lama ditolak `CONNACK 5`; baru diterima |
| `11-external-port-check.log` | Pemeriksaan dari Attacker Node sebelum B4 | 22, 80, dan 1883 terbuka; 9000 tertutup; API melalui port 80 membalas 401 tanpa token |
| `12-target-redaction-and-env.log` | Redaksi `auth` pada log akses dan kunci `.env` | `auth=REDACTED`; kunci `.env` terdaftar tanpa nilai |
| `13-backup-relocation-and-deploy.log` | Pemasangan skrip repositori, pemindahan arsip, pencadangan, uji pemulihan, dan uji tolak pengguna layanan | Skrip 750 `root:root`; arsip mode 700 di luar home; backup `Succeeded`; pemulihan 4 dari 4; `smartcow` ditolak |
| `14-c1-credential-and-liveness-recheck.log` | C1 sesudah pemasangan, penolakan kredensial lama, izin berkas, dan aliran telemetri | C1 6 dari 6 lulus; token API lama 401; dua sandi broker lama `CONNACK 5`; kredensial aktif diterima |
| `15-ssh-password-auth-disabled.log` | Kebijakan `sshd` efektif dan metode autentikasi ketiga node | `passwordauthentication no` pada `.100` dan `.200`; hanya `publickey`; login kunci berhasil; tanggal ubah sandi tidak berubah |

## Catatan Status dan Batasan

- Rantai deteksi Sguil berjalan penuh dan sudah diuji ulang. Alert kustom SID 1000002 dan 1000003 yang dihasilkan pada verifikasi ulang masuk ke basis data sebagai CID 6356 dan 6352 (`09-sguil-alerts.log`).
- Kredensial broker MQTT akun `esp32` dirotasi pada verifikasi ulang karena nilainya terlihat pada tangkapan layar lama. Berkas lama disimpan sebagai `mqtt_users.json.bak-<stempel>` mode 600; kredensial lama ditolak, kredensial baru diterima, dan uji C1 dijalankan ulang setelah rotasi dengan hasil 6 dari 6 lulus (`10-mqtt-credential-rotation.log`).
- Kata sandi akun sistem (bukan kredensial broker) tidak dirotasi karena masih dipakai untuk login konsol dan Sguil pada panduan demo; rotasi tetap keputusan pemilik lab. Sebagai gantinya jalur kata sandi SSH ditutup. Target Node sudah menolak kata sandi sejak hardening, dan pada verifikasi ulang Attacker Node serta Monitoring Node disetel `PasswordAuthentication no` dengan cadangan `sshd_config.bak-hardening-<stempel>`. Ketiga node hanya menawarkan `publickey`; kata sandi akun tidak berubah sehingga tidak ada akun terkunci (`15-ssh-password-auth-disabled.log`).
- Bukti RT-04 tersedia sebagai tangkapan layar: `docs/redteam/evidence/15-replay-sebelum-diterima.png` (replay diterima sebelum perbaikan), `16-replay-sesudah-ditolak.png` (replay ditolak setelah anti-replay aktif), dan `17-catatan-broker-replay.png` (catatan `broker.log`). Alert Sguil dibuktikan melalui query basis data pada `09-sguil-alerts.log`.
- Berkas `11-external-port-check.log` diambil sebelum kontrol B4 diterapkan. Sesudah B4, port 1883 tidak lagi terbuka dari Attacker Node (`docs/redteam/evidence/14-pemindaian-port-mqtt-setelah.png`).
