# Verifikasi Kontrol 12 November 2026

Folder ini memuat bukti teks verifikasi ulang kontrol pengamanan fase 2 pada lingkungan lab yang benar-benar berjalan. Berkas dapat dibaca ulang tanpa menyalakan mesin virtual.

Seluruh berkas pada folder ini adalah keluaran perintah asli, bukan rekonstruksi. Nilai rahasia (token API, sandi akun broker, isi `.env`) tidak ikut tercetak.

## Daftar Berkas

| Berkas | Isi | Hasil |
| :--- | :--- | :--- |
| `01-c1-live-verification.log` | `c1_verify.py` dijalankan dua kali: langsung ke `127.0.0.1:9000` dan lewat Nginx `192.168.12.5:80` | 6/6 lulus pada kedua jalur |
| `02-c3-backup-restore.log` | Backup harian, verifikasi pemulihan, dan uji gerbang keamanan dengan manifest yang dirusak | backup `Succeeded`; pemulihan 4/4 cocok; arsip rusak ditolak tanpa menyentuh data |
| `03-topology-reachability.log` | Ping dari host ke 192.168.12.5, .100, dan .200 | ketiganya 0% loss |
| `04-onion-state.log` | Identitas dan antarmuka Monitoring Node | `SOC-KEL12-B`, `eth2=192.168.12.200/24`, `eth0` promiscuous tanpa IP |
| `05-onion-ids-state.log` | Rantai deteksi di Onion | `snort`, `barnyard2`, `sguild` (`tclsh`), `mysqld` berjalan; rule SID 1000002 ada |
| `06-target-state-recon.log` | Kondisi Target Node sesudah perbaikan C3 | sshd, iptables, listener, izin berkas, kunci `.env`, isi direktori `backup` (daftar dipotong 10 baris), `/health`. Daftar arsip lengkap beserta checksum ada pada `02-c3-backup-restore.log` |
| `07-backup-units-after.log` | Izin skrip dan status timer | skrip `root:root` mode 750, timer `enabled`/`active` |
| `08-password-login-rejected.log` | Login SSH memakai kata sandi lab untuk `root`, `sec_admin`, `analyst` | ketiganya ditolak, hanya `publickey` diterima |
| `09-sguil-alerts.log` | Query basis data untuk seluruh alert `SMARTCOW%` | CID 6125, 6127, 6352, 6356 |
| `10-mqtt-credential-rotation.log` | Kredensial broker lama dan baru setelah rotasi | lama ditolak `CONNACK 5`, baru diterima |
| `11-external-port-check.log` | Pemeriksaan dari Attacker Node | 22/80/1883 terbuka, 9000 tertutup, API lewat 80 membalas 401 tanpa token |
| `12-target-redaction-and-env.log` | Redaksi `auth` pada log akses dan kunci `.env` | `auth=REDACTED`, kunci `.env` terdaftar tanpa nilai |
| `13-backup-relocation-and-deploy.log` | Pemasangan skrip repositori di Target Node, pemindahan arsip ke `/var/lib/smartcow/backup`, pencadangan, uji pemulihan, dan uji tolak pengguna layanan | skrip `root:root` mode 750; direktori arsip `root:root` mode 700 di luar home layanan; backup `Succeeded`; pemulihan 4/4 cocok; `smartcow` tidak dapat menulis, membaca, atau menghapus arsip |
| `14-c1-credential-and-liveness-recheck.log` | Verifikasi C1 sesudah pemasangan, penolakan kredensial lama, izin berkas rahasia, dan aliran telemetri | C1 6/6 lulus; token API lama dibalas 401; dua sandi broker lama ditolak `CONNACK 5`; kredensial aktif diterima; telemetri tetap mengalir |
| `15-ssh-password-auth-disabled.log` | Kebijakan `sshd` efektif dan metode autentikasi yang ditawarkan ketiga node | `passwordauthentication no` pada .100 dan .200; ketiga node hanya menawarkan `publickey`; login kunci berhasil; tanggal ubah kata sandi tidak berubah hari ini |

## Catatan status dan batasan

- Rantai deteksi Sguil berjalan penuh dan sudah diuji ulang: alert kustom SID 1000002 dan 1000003 yang dihasilkan pada 12 November 2026 masuk ke basis data sebagai CID 6356 dan 6352 (`09-sguil-alerts.log`).
- Kredensial broker MQTT akun `esp32` dirotasi pada 12 November 2026 karena nilainya terlihat pada tangkapan layar lama. Berkas lama disimpan sebagai `mqtt_users.json.bak-20261112` mode 600, kredensial lama ditolak sedangkan yang baru diterima, dan uji C1 dijalankan ulang setelah rotasi dengan hasil 6/6 lulus (`10-mqtt-credential-rotation.log`).
- Kata sandi akun sistem (bukan kredensial broker) tidak dirotasi karena nilainya dipakai untuk login konsol dan Sguil pada panduan demo; rotasi tetap keputusan pemilik lab. Sebagai gantinya jalur kata sandi SSH ditutup: Target Node memang sudah menolak kata sandi sejak hardening, dan pada 12 November 2026 Attacker Node serta Monitoring Node disetel `PasswordAuthentication no` (cadangan `sshd_config.bak-hardening-20261112`). Ketiga node kini hanya menawarkan `publickey`, kata sandi akun tidak berubah sehingga tidak ada akun yang terkunci (`15-ssh-password-auth-disabled.log`).
- Bukti RT-04 kini tersedia sebagai tangkapan layar di `docs/redteam/evidence/15-replay-sebelum-diterima.png` (replay diterima sebelum perbaikan), `16-replay-sesudah-ditolak.png` (replay ditolak setelah anti-replay aktif), dan `17-catatan-broker-replay.png` (catatan `broker.log`); alert Sguil tetap terbukti lewat query basis data pada `09-sguil-alerts.log`.
