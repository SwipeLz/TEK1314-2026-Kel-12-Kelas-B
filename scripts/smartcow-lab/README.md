# Replika Backend smartcow-lab

Kode replika backend IoT yang berjalan di Target Node `SRV-IOT-KEL12-B`. Tujuannya meniru stack proyek asli, yaitu REST dengan token dan struktur path `devices/cow-sprinkler-01/...`, sehingga temuan di lab relevan dengan sistem asli.

Seluruh kode memakai Python 3.9 standar dari Arch tanpa dependensi baru, karena segmen lab tidak memiliki akses internet untuk memasang Firebase Emulator. Tidak ada paket yang perlu dipasang.

Folder ini dapat dipakai ulang di lab baru selama tiga hal dijaga: token disimpan pada berkas mode 600, akses jaringan ke port 1883 dibatasi (kini hanya loopback setelah kontrol B4), dan data yang mengalir ke API tidak pernah berisi data operasional.

## Daftar Isi

- [Isi Folder](#isi-folder)
- [Cara Pasang di Target Node](#cara-pasang-di-target-node)
- [Catatan Keamanan](#catatan-keamanan)

## Isi Folder

| Berkas | Fungsi |
| :--- | :--- |
| `app.py` | REST API bergaya Firebase RTDB dengan autentikasi token, validasi rentang sensor, dan log akses |
| `broker.py` | Broker MQTT minimal: CONNECT dengan kredensial, SUBSCRIBE, PUBLISH, PINGREQ, ACL topik, dan anti-replay stempel waktu (`SMARTCOW_MQTT_ANTIREPLAY`) |
| `simulator.py` | Meniru firmware ESP32 yang menulis telemetri dummy tiap dua detik |
| `mqtt_pub.py` | Klien publish MQTT sisi penyerang, dipakai skenario RT-03 |
| `ssh_try.py` | Klien percobaan login SSH berbasis pty, pengganti NSE ssh-brute yang membutuhkan `sshpass` |
| `nginx-smartcow.conf` | Server block Nginx untuk dashboard dan proxy `/api` |
| `patch-nginx.py` | Menambal `nginx.conf` dengan blok proxy; opsi `tokens` menambahkan `server_tokens off` |
| `patch-app-secrets.py` | Menghapus literal token dari `app.py` dan memindahkannya ke environment |
| `install-lab.sh` | Memasang pengguna aplikasi, folder, unit systemd, dan Nginx sebagai root |
| `smartcow-api.service`, `smartcow-broker.service`, `smartcow-sim.service` | Unit systemd untuk tiga layanan |
| `smartcow-backup` | Skrip pencadangan: membekukan `data/` dengan `cp -a`, mengarsipkan salinan beku, menulis checksum dan manifest sha256, publikasi atomik melalui `.part`, retensi tujuh arsip |
| `smartcow-restore` | Pemulihan bergerbang: verifikasi checksum dan manifest, hentikan `smartcow-api`/`smartcow-sim`, simpan `data.prev-<stempel>`, pasang data, perbaiki kepemilikan, rollback otomatis bila gagal |
| `smartcow-backup.service`, `smartcow-backup.timer` | Unit dan penjadwal harian untuk skrip pencadangan |
| `c3_restore_check.sh` | Verifikasi pemulihan non-destruktif: ekstrak arsip ke direktori sementara lalu cocokkan dengan manifest |
| `c1_verify.py` | Uji C1: publish anonim, publish sah, publish ke topik terlarang, lalu tiga variasi `PUT` REST. Kredensial dibaca langsung dari berkas rahasia |
| `app.env.example`, `mqtt.env.example` | Contoh berkas environment tanpa nilai rahasia |

## Cara Pasang di Target Node

1. Salin folder ini ke `/home/sec_admin/lab-files/` pada Target Node.
2. Jalankan `echo <password> | sudo -S bash /home/sec_admin/lab-files/install-lab.sh`.
3. Ganti nilai pada `app.env` dan `mqtt.env` dengan token dan sandi buatan sendiri.
4. Jalankan `python3 patch-nginx.py`, lalu `python3 patch-nginx.py tokens` untuk versi yang juga menyembunyikan nomor versi Nginx.
5. Pasang pencadangan sebagai root, bukan sebagai pengguna layanan:
   `install -o root -g root -m 750 smartcow-backup smartcow-restore /usr/local/bin/`.
   Salin `smartcow-backup.service` dan `.timer` ke `/etc/systemd/system/`, lalu jalankan
   `systemctl enable --now smartcow-backup.timer`. Skrip berjalan sebagai root dan menyimpan arsip
   di `/var/lib/smartcow/backup` (`root:root` mode 700), di luar `/home/smartcow-lab`, agar pengguna
   layanan tidak dapat mengganti arsip atau menaruh checksum palsu.

Semua layanan berjalan sebagai pengguna `smartcow` tanpa login, dengan `NoNewPrivileges=yes` dan `PrivateTmp=yes`.

## Catatan Keamanan

- Berkas `.env` dan `secrets/mqtt_users.json` tidak boleh masuk ke git. Repositori hanya memuat contoh dengan nilai kosong.
- Nilai yang dipakai saat pengujian checkpoint sudah dirotasi setelah bocor pada fase sebelum hardening, sehingga tidak berlaku lagi.
- Aturan firewall yang membuka port 1883 pernah berlaku untuk segmen lab `192.168.12.0/24`. Sejak kontrol B4, akses jaringan ke broker ditutup dan hanya loopback yang dilayani. Jangan membuka port tersebut ke jaringan publik.
