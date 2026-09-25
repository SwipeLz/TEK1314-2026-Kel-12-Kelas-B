# Skema Alokasi IP Address - Kelompok 12 Kelas B
**Mata Kuliah:** TEK1314 - Keamanan Siber
**Segmen Jaringan:** 192.168.12.0/24 (unik Kel-12, sesuai Kontrak Kuliah Poin 3a)
**Netmask:** 255.255.255.0 (/24)
**Gateway (virtual/host-only):** 192.168.12.1
**Mode VirtualBox:** Host-Only (DHCP off, IP statis) atau Internal Network `kel12-net`. Jangan Bridged ke Wi-Fi kampus.

| Hostname | IP Address | Peran / Node | OS yang Direncanakan | Keterangan / Port Terbuka |
| :--- | :--- | :--- | :--- | :--- |
| **SRV-IOT-KEL12-G** (alias `v-target-srv`) | 192.168.12.5 | Target Node (Korban) / Server Alat IoT | Ubuntu Server 22.04 LTS CLI (ringan, 1 vCPU / 1-2 GB) + Mosquitto + Flask dashboard. Alternatif: Metasploitable 2 jika butuh service rentan demo | 22 SSH, 80 HTTP dashboard, 1883 MQTT (wajib auth). Desain awal tim: 21 FTP, 3306 MySQL (tutup jika tidak dipakai IoT) |
| **ATTACKER-KEL12** (alias `v-attacker`) | 192.168.12.100 | Attacker Node | Kali Linux (atau CyberOps jika RAM mepet) | Recon: Nmap, curl, mosquitto_pub/sub (simulasi ESP32 normal + attack replay/anon), hydra (terbatas) |
| **SOC-KEL12-mgmt** (alias `v-seconion-mgmt`) | 192.168.12.200 | Monitoring Node (Mgmt) | Security Onion 2.4 | eth0: Web UI, Kibana, Sguil/Squert, Zeek/Suricata |
| **SOC-KEL12-sniff** (alias `v-seconion-sniff`) | *No IP (Promiscuous)* | Monitoring Node (Sensor) | Security Onion (NIC ke-2) | eth1: Tap/SPAN tanpa IP, tangkap seluruh trafik `192.168.12.0/24` |
| **ESP32-SIM** (logis) | via .100 | IoT Edge (simulasi) | Firmware ESP32 + DHT22 (simulasi `mosquitto_pub` dari Attacker) | Publish ke `192.168.12.5:1883` topik `greenhouse/#` |

### Catatan Alokasi Jaringan:
1. **Target Server (192.168.12.5):** IP statis. Desain awal: web rentan untuk eksploitasi Red Team. Adaptasi IoT: tambah Mosquitto + dashboard greenhouse di OS yang sama agar 1 VM berperan sebagai Server Alat IoT (hemat RAM).
2. **Attacker Node (192.168.12.100):** mesin ofensif Nmap/sniffing/eksploitasi + sekaligus simulator ESP32 (publish normal vs replay jahat).
3. **Monitoring Node (192.168.12.200):** 2 interface — `.200` untuk dashboard SOC, 1 promiscuous untuk capture. Wajib merekam ICMP + MQTT + HTTP `.100` ↔ `.5` untuk lulus Logging Check Minggu 5.
4. **Port final Fase 1 (prinsip least exposure):** buka 22 (terbatas segmen sendiri), 80, 1883. Tutup 443/8883 dulu, tutup 21/3306 kecuali dibutuhkan demo Metasploitable. Lihat `scripts/hardening-iot-server.sh` + `../phase-1-baseline/baseline-report.md`.

### Verifikasi cepat (tiap VM):
```bash
ip addr show
ip route show
ping -c 4 192.168.12.5
ping -c 4 192.168.12.100
ping -c 4 192.168.12.200
ss -tulpn
hostnamectl
```
Harus saling ping sebelum Minggu 5. Jika gagal cek VirtualBox adapter (harus 1 jaringan sama) + firewall host Windows.
