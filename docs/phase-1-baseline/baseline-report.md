# Baseline Report Fase 1 (Minggu 7) - Kelompok 12 Kelas B

Subnet 192.168.12.0/24. Kondisi before attack, sistem sudah di-hardening sebelum diserang.

## 1. Aset

| Hostname | IP | OS | Service |
| :--- | :--- | :--- | :--- |
| SRV-IOT-KEL12-B | 192.168.12.5 | Arch Linux (Security Workstation) | SSH 22 (iptables hanya buka 22/80/1883) |
| ATTACKER-KEL12-B | 192.168.12.100 | Cisco LabVM Ubuntu (user analyst) | nmap, ping, dumpcap/Wireshark |
| SOC-KEL12-B | 192.168.12.200 | Security Onion | tcpdump, Sguil server (sensor IDS belum provisioned, Plan B) |

Detail IP ada di `../design/ip_plan.md`. Gambar ada di `../design/topology.jpeg`.

## 2. Hardening

Network (iptables, karena target Arch tanpa UFW):
* Default INPUT DROP, OUTPUT ACCEPT.
* Buka ICMP + TCP 22/80/1883 hanya dari 192.168.12.0/24.
* Cek pakai `sudo iptables -L -n -v --line-numbers`.

System:
* Login pakai user biasa sec_admin (uid 1001, non-root).
* Matikan service tidak dipakai: vsftpd, telnet.socket, pox, ovs-vswitchd (cek `systemctl list-unit-files --state=enabled`).
* Patch via pacman tidak jalan karena segmen isolasi tanpa internet (dicatat sebagai keterbatasan).
* Mosquitto/MQTT belum diinstal (butuh internet). Port 1883 dibuka di firewall sebagai persiapan skenario IoT Fase 2.

Identitas:
* Hostname: SRV-IOT-KEL12-B, ATTACKER-KEL12-B, SOC-KEL12-B.
* IP: .5, .100, .200 di segmen 192.168.12.0/24.
* Cek pakai `hostnamectl` dan `ip addr`.

## 3. Logging Check Minggu 5

Sguil dibuka (sensor seconion-import) tapi RealTime Events kosong karena proses IDS snort/suricata tidak ter-provision di VM ini (hanya pipeline elastic/kibana/logstash yang Up). Dipakai Plan B sesuai panduan (Wireshark + log manual).

Cara uji yang dilakukan:
* Dari attacker: `ping 192.168.12.5` dan `nmap -sS` (0% loss, port 22 open).
* tcpdump di Onion menangkap ICMP (12 packets, 0 dropped).
* Capture Wireshark di attacker: 45 paket (ICMP .100 ke .5, ARP).

Bukti di `assets/`:
* `ping-attacker.log`
* `tcpdump-icmp.png`
* `wireshark-icmp.png` + `kel12-demo.pcap`
* `target-ip-hostname.png`, `target-ip-statis.png`, `onion-ip.png`
* `hardening-services.png`, `hardening-firewall.png`

## 4. Demo Minggu 7

1. Jelaskan topologi.
2. Tunjukkan file hardening.
3. Tunjukkan live ping tercatat di Onion.
4. Q&A alasan pilih hardening tersebut.
