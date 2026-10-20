# Replika backend smartcow-lab

Sumber replika backend IoT yang berjalan di Target Node `SRV-IOT-KEL12-B`.
Tujuannya meniru stack proyek asli, yaitu REST dengan token dan struktur path
`devices/cow-sprinkler-01/...`, supaya temuan di lab relevan dengan sistem asli.

Tidak ada dependensi yang perlu dipasang.

Semua kode memakai Python 3.9 standar dari Arch, tanpa dependensi baru, karena
segmen lab tidak punya akses internet untuk memasang Firebase Emulator.

Folder ini bisa dipakai ulang di lab baru, selama tiga hal tetap dijaga: token
disimpan di berkas mode 600, port 1883 hanya dibuka untuk segmen lab, dan data
yang mengalir ke API tidak pernah berisi data operasional.

## Isi folder

| Berkas | Fungsi |
| --- | --- |
| `app.py` | API REST bergaya Firebase RTDB dengan autentikasi token, validasi rentang sensor, dan log akses |
| `broker.py` | Broker MQTT minimal: CONNECT dengan kredensial, SUBSCRIBE, PUBLISH, PINGREQ, plus ACL topik |
| `simulator.py` | Meniru firmware ESP32 yang menulis telemetri dummy tiap dua detik |
| `mqtt_pub.py` | Klien publish MQTT sisi penyerang, dipakai skenario RT-03 |
| `ssh_try.py` | Klien percobaan login SSH berbasis pty, pengganti NSE ssh-brute yang butuh `sshpass` |
| `nginx-smartcow.conf` | Server block Nginx untuk dashboard dan proxy `/api` |
| `patch-nginx.py` | Menambal `nginx.conf` dengan blok proxy, opsional menambahkan `server_tokens off` |
| `patch-app-secrets.py` | Menghapus literal token dari `app.py` dan memindahkannya ke environment |
| `install-lab.sh` | Memasang pengguna aplikasi, folder, unit systemd, dan Nginx sebagai root |
| `smartcow-api.service`, `smartcow-broker.service`, `smartcow-sim.service` | Unit systemd untuk tiga service |
| `app.env.example`, `mqtt.env.example` | Contoh berkas environment, tanpa nilai rahasia |

## Cara pasang di Target Node

1. Salin folder ini ke `/home/sec_admin/lab-files/` pada Target Node.
2. Jalankan `echo <password> | sudo -S bash /home/sec_admin/lab-files/install-lab.sh`.
3. Ganti nilai pada `app.env` dan `mqtt.env` dengan token dan sandi buatan sendiri.
4. Jalankan `python3 patch-nginx.py` lalu `python3 patch-nginx.py tokens` untuk
  versi yang juga menyembunyikan nomor versi Nginx.

Semua service berjalan sebagai pengguna `smartcow` tanpa login, dengan
`NoNewPrivileges=yes` dan `PrivateTmp=yes`.

## Catatan keamanan

- Berkas `.env` dan `secrets/mqtt_users.json` tidak boleh masuk ke git. Yang
  ada di repo hanya contoh dengan nilai kosong.
- Nilai yang dipakai saat pengujian checkpoint ini sudah dirotasi setelah bocor
  di fase sebelum hardening, jadi tidak berlaku lagi di mana pun.
- Aturan firewall yang membuka port 1883 hanya berlaku untuk segmen lab
  `192.168.12.0/24`. Jangan dibuka ke jaringan publik.
