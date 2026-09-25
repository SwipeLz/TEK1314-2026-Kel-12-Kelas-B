# Topologi — Kelompok 12 (Smart Greenhouse)

File gambar wajib: `topology.png` (di folder ini, dibuat Blue Team via Draw.io / Packet Tracer, lalu export PNG).
File ini sebagai penjelasan teks pendamping agar dosen/asdos paham tanpa buka gambar.

## Diagram Teks

```
                    +------------------+
                    | ESP32-SIM (logis)|
                    | DHT22 + Relay    |
                    +--------+---------+
                             | publish greenhouse/suhu (MQTT 1883)
                             v
+---------------+   +--------------------------+   +------------------+
| ATTACKER-KEL12|-->| SRV-IOT-KEL12-G (.5)      |<--| SOC-KEL12 (.200) |
| .100 Kali     |   | Ubuntu + Mosquitto + Web |   | Security Onion   |
| ping/scan/pub |   | :22 SSH :80 Web :1883 MQTT|   | Sguil/Squert     |
+---------------+   +--------------------------+   +------------------+
        \_________________ span / mirror _________________/
                   semua trafik .100<->.5 dimonitor .200
```

* Semua di `192.168.12.0/24`, Host-Only `kel12-net`.
* Satu VM Target berperan ganda: MQTT Broker + Web Dashboard = "Server Alat IoT".
* Security Onion dipasang di tengah (atau dengan port mirror vbox) agar melihat ICMP + MQTT + HTTP.

## Alur Data Normal (Baseline)

1. ESP32-SIM `mosquitto_pub -h 192.168.12.5 -u sensor1 -P <pass> -t greenhouse/suhu -m '{"t":27.5,"h":70}'`
2. Broker Mosquitto di .5 menerima, cek ACL.
3. Dashboard Web di .5:80 subscribe topik dan tampilkan grafik.
4. User buka `http://192.168.12.5/` dari .100 (browser).
5. Security Onion di .200 mencatat: TCP 1883 + TCP 80 + ICMP jika ada ping.

## Alur Serangan (Rencana Fase 2, belum dieksekusi di Fase 1)

* Replay / Unauthorized Publish: `mosquitto_pub -h 192.168.12.5 -t greenhouse/pompa/cmd -m "ON"` tanpa auth → harus GAGAL setelah hardening, dan kalaupun dipaksa harus muncul alert.
* MQTT anon probe + Web `../` traversal + SSH brute ringan — semua hanya ke .5.

## Cara Buat topology.png (Blue Team)

1. Buka draw.io → 4 kotak: ESP32-SIM, SRV-IOT (.5), ATTACKER (.100), SOC (.200).
2. Tulis IP + port di tiap kotak, panah berlabel `MQTT:1883`, `HTTP:80`, `ICMP`, `monitor/span`.
3. Tulis subnet `192.168.12.0/24` di atas.
4. Export PNG 1920px → simpan sebagai `topology.png` di folder ini (overwrite placeholder yang digenerate otomatis).
5. Screenshot juga dari Packet Tracer jika sempat (opsional).

> File `topology.png` yang sekarang adalah placeholder hasil generate otomatis — silakan timpa dengan gambar Draw.io final sebelum demo Minggu 7.
