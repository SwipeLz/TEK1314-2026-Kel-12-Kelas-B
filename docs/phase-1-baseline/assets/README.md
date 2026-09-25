# Assets — Bukti Fase 1 (Minggu 5 Logging + Minggu 7 Hardening)

Taruh SEMUA screenshot / log di folder ini. Nama file wajib persis agar `baseline-report.md` tidak broken:

* `01-sguil-ping.png` — Sguil/Squert merekam ICMP (wajib, kriteria lulus Minggu 5: timestamp + src 192.168.12.100 + dst 192.168.12.5 kelihatan)
* `02-ping-terminal.png` — terminal Attacker `ping -c 10 192.168.12.5` sukses
* `03-ip-addr.png` — `ip addr show` + `hostnamectl` di 3 VM (bisa digabung 3 screenshot: `03a-target.png`, `03b-attacker.png`, `03c-soc.png`)
* `04-ufw-status.png` — `sudo ufw status verbose` = active + 3 rule
* `05-apt-upgrade.png` — bukti `apt update && apt upgrade` / `mosquitto.conf` (`allow_anonymous false`)
* `06-sguil-mqtt.png` — (nilai plus IoT) Sguil merekam TCP 1883 saat `mosquitto_pub` normal
* `wireshark-ping.pcap` — (Plan B jika Onion berat) hasil capture Wireshark saat ping
* `topology-screenshot.png` — (opsional) foto Packet Tracer jika sempat

Cara ambil cepat:
1. Attacker: `ping -c 10 192.168.12.5` → screenshot terminal.
2. SOC: buka Sguil → filter `192.168.12.100` → screenshot.
3. Target: `sudo ufw status verbose; cat /etc/ufw/user.rules; cat /etc/mosquitto/mosquitto.conf | grep -v "^#" | grep -v "^$"` → screenshot.
4. Copy semua ke folder ini, lalu `git add`, commit, push sebelum demo.
