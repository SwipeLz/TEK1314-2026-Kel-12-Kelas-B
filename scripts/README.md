# Scripts

* `hardening-iot-server.sh` — jalankan di Target Ubuntu (.5) untuk UFW + user + Mosquitto hardening (Fase 1 Minggu 6-7). `chmod +x`, lalu `sudo ./hardening-iot-server.sh`.
* `verify-logging.sh` — jalankan di Attacker (.100) untuk uji ping + MQTT + HTTP agar tercatat di Security Onion (Minggu 5). `chmod +x`, lalu `./verify-logging.sh 192.168.12.5 sensor1 'passwordnya'`.

Kedua skrip hanya menyerang IP kelompok sendiri (`192.168.12.0/24`). Jangan jalankan ke Wi-Fi kampus.
