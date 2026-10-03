# Attack plan Fase 2 — Kelompok 12 Kelas B

Skenario: **No 10 — IoT Protocol Guardian**. Target satu-satunya:
**192.168.12.5 (SRV-IOT-KEL12-B)**. Dilarang keluar dari segmen itu.

Tools di bawah ditulis apa adanya: yang sudah ada di attacker dicentang,
yang belum ditandai cara dapatnya. Blue team siapkan deteksinya dari daftar
ini, jangan tunggu eksekusi.

Tiga skenario di bawah sengaja disusun dari yang paling berisik sampai yang
paling senyap supaya blue team merasakan bedanya deteksi tiap lapis, mulai
dari scan yang terang-terangan dan pasti memicu alert, terus brute-force yang
memaksa analis membaca journal baris per baris, sampai replay MQTT yang cuma
kelihatan kalau tahu pola publish normalnya seperti apa.

## Skenario 1 — Reconnaissance: petakan target (kategori: recon)

- Teknik: scan port + service + OS fingerprint ke 192.168.12.5.
- Tools: `nmap` (sudah ada di attacker, versi 7.80). Contoh:
  `sudo nmap -sS -sV -O -p 21,22,23,80,1883,3306 192.168.12.5`.
- Hasil yang diharapkan: port 22 open (OpenSSH), 80/1883 closed (belum ada
  service), sisanya filtered (firewall DROP). OS tertebak Linux.
- Jejak deteksi: scan intensif memicu `ET SCAN` di Sguil; koneksi SSH
  berulang tercatat sebagai Potential SSH Scan.
- Bukti awal sudah ada: `docs/redteam/evidence/nmap-target-after.log`
  (scan 3 Okt 2026, 6 detik, 1 host up).

## Skenario 2 — Brute-force login SSH (kategori: akses)

- Teknik: tebak password SSH berkali-kali dalam waktu singkat ke port 22.
- Tools: utama `Hydra` (belum ada di attacker, butuh internet untuk install;
  fallback offline: script NSE bawaan nmap `ssh-brute`, sudah ikut paket nmap).
- Hasil yang diharapkan: dengan `MaxAuthTries 3` + faillock aktif, akun
  terkunci setelah gagal beruntun; Sguil mencatat `ET SCAN Potential SSH Scan`
  (+ OUTBOUND) lengkap dengan source port.
- Jejak deteksi: auth failure beruntun di journal target (`LogLevel VERBOSE`
  sudah dipasang) + alert Sguil dari .100 ke .5 port 22.
- Catatan: password asli tidak dipakai. Uji coba pakai wordlist kecil supaya
  tidak mengunci akun operasional lama-lama. Setelah uji, lock di-reset
  (`faillock --user sec_admin --reset`).

## Skenario 3 — MQTT replay & publish palsu (kategori: protokol IoT)

- Teknik: tangkap paket perintah (atau rakit sendiri), kirim ulang / publish
  ke topic perintah sehingga aktuator (semprotan) nyala tanpa threshold suhu.
- Tools: `mosquitto_pub` / MQTT Explorer (belum ada; butuh install Mosquitto
  saat segmen dapat internet, atau script Python `paho-mqtt`).
  Fallback Fase 2: simulasi service perintah di target + replay pakai
  `curl`/HTTP POST suhu palsu ke endpoint replika.
- Hasil yang diharapkan: perintah palsu diterima replika (sebelum mitigasi:
  tanpa autentikasi topic). Setelah mitigasi (auth + ACL topic + TLS):
  publish palsu ditolak dan tercatat di log broker.
- Jejak deteksi: koneksi ke 1883 + pola publish berulang di capture Onion;
  korelasi dengan log aplikasi replika.
- Kaitan ke proyek asli: persis seperti perintah semprot palsu (RTDB →
  ESP32 → relay → solenoid) versi lab. Bedanya di sini datanya dummy.

## Aturan main (RoE)

Hanya 192.168.12.5. Dilarang scanning/attack ke jaringan kampus, Wi-Fi publik,
atau kelompok lain. DoS tidak dipakai sebagai skenario (cukup 3 di atas,
sudah 3 kategori). Setiap skenario wajib lewat 5 tahap Purple Team Loop
(lihat `docs/purple-team-log.md`): serang → deteksi → analisis → respons →
verifikasi ulang. Serangan yang tercatat berhasil di tahap 1 harus berakhir
gagal di tahap 5.

Tidak ada pengecualian.
