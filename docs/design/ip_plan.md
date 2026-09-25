# IP Plan — Kelompok 12 Kelas B (Design Phase Minggu 4)

**Subnet:** `192.168.12.0/24` (unik untuk Kel-12, mengacu Kontrak Kuliah Poin 3a — contoh di panduan: 192.168.10.0/24 untuk Kel-10)
**Netmask:** 255.255.255.0
**Gateway (virtual/host-only):** 192.168.12.1
**Mode VirtualBox:** Host-Only Adapter (vboxnet, DHCP dimatikan, semua IP statis) atau Internal Network `kel12-net`. Jangan pakai Bridged ke Wi-Fi kampus agar tidak menyerang IP lain.
**Skenario:** Smart Greenhouse — 1 VM Target berperan sebagai Server Alat IoT.

| Hostname | IP Address | OS Direncanakan | Peran | Port/Service | Keterangan |
|----------|------------|-----------------|-------|--------------|------------|
| SRV-IOT-KEL12-G | 192.168.12.5 | Ubuntu Server 22.04 LTS CLI (1 vCPU, 1-2 GB RAM, 20 GB disk) + Mosquitto 2.x + Python Flask dashboard | Target Node (Korban) / Server Alat IoT | 22/tcp SSH, 80/tcp HTTP dashboard, 1883/tcp MQTT | Blue Team harden; Red Team attack HANYA ke IP ini |
| ATTACKER-KEL12 | 192.168.12.100 | Kali Linux (atau Cisco CyberOps Workstation jika RAM mepet) | Attacker Node | client: ping, nmap, mosquitto_pub/sub, hydra, curl | Simulasi ESP32 (publish normal) + simulasi penyerang (replay/anon/brute) |
| SOC-KEL12 | 192.168.12.200 | Security Onion 2.4 (4 GB RAM min, 2 vCPU, 40 GB disk, 2 NIC: 1 management .200 + 1 monitor promiscuous tanpa IP) | Monitoring Node | Sguil, Squert/Kibana, Wireshark, Zeek/Suricata | Wajib merekam ICMP + MQTT + HTTP antar .100 <-> .5 |
| ESP32-SIM (logis, bukan VM) | DHCP / via Attacker | Firmware ESP32 + DHT22 (disimulasikan dengan `mosquitto_pub` dari .100) | IoT Edge | publish ke 192.168.12.5:1883 topik `greenhouse/#` | Tidak perlu IP tetap; di diagram digambar sebagai node logis |

## Tabel Port (dari Red Team ke Blue Team)

| Port | Service | Dibuka? | Alasan |
|------|---------|---------|--------|
| 22/tcp | SSH | YA, terbatas (hanya dari .100/.200 via UFW) | Manajemen; akan diuji brute-force ringan di Fase 2 lalu di-harden key-auth |
| 80/tcp | HTTP Dashboard | YA | Dashboard greenhouse; akan diuji traversal/brute login di Fase 2 |
| 443/tcp | HTTPS | OPSIONAL (tutup dulu jika belum ada sertifikat) | Best practice, tapi tutup agar permukaan kecil |
| 1883/tcp | MQTT | YA, auth wajib | nyawa IoT; uji anon-publish harus GAGAL setelah hardening |
| 8883/tcp | MQTT-TLS | TUTUP dulu | Rencana hardening lanjutan Fase 3 |
| 3306, 23, 445, lainnya | — | TUTUP | Tidak dibutuhkan skenario ini |

## Routing

Satu broadcast domain, tidak perlu routing statis. Jika Security Onion pakai 2 NIC, pastikan NIC monitor tidak punya IP (promiscuous) dan NIC management di 192.168.12.200/24.

## Verifikasi cepat (jalankan di tiap VM)

```bash
ip addr show
ip route show
ping -c 4 192.168.12.5
ping -c 4 192.168.12.100
ping -c 4 192.168.12.200
ss -tulpn
hostnamectl
```

Semua harus saling ping sebelum lanjut ke Minggu 5 (Logging Check). Jika ada yang tidak ping, cek Network Adapter VirtualBox (harus 1 jaringan yang sama) dan firewall host Windows.
