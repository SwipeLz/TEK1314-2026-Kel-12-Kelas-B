# Skema Alokasi IP Address - Kelompok 12 Kelas B

**Segmen:** 192.168.12.0/24
**Netmask:** 255.255.255.0
**Mode VirtualBox:** Host-Only, IP statis semua. Jangan pakai Bridged.

| Hostname | IP Address | Peran | OS Rencana | Port / Keterangan |
| :--- | :--- | :--- | :--- | :--- |
| SRV-IOT-KEL12-B | 192.168.12.5 | Target (korban) / server IoT | Ubuntu Server 22.04 CLI, alternatif Metasploitable 2 | 80 HTTP, 21 FTP, 22 SSH, 1883 MQTT |
| ATTACKER-KEL12-B | 192.168.12.100 | Attacker | Kali Linux | Untuk scanning dan exploit |
| SOC-KEL12-B | 192.168.12.200 | Monitoring (mgmt) | Security Onion | eth0 untuk Web UI / Sguil |
| SOC-KEL12-B-sniff | No IP (promiscuous) | Monitoring (sensor) | Security Onion NIC ke-2 | Untuk menangkap trafik 192.168.12.0/24 |

Catatan:
1. Target (.5) IP statis, untuk latihan exploit Red Team. Dianggap sebagai server IoT.
2. Attacker (.100) untuk Nmap dan exploit, hanya ke .5.
3. Monitoring (.200) pakai 2 interface, satu ada IP untuk dashboard, satu tanpa IP untuk sniffing.
