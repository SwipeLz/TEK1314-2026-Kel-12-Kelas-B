# Skema Alokasi IP Address - Kelompok 12
**Mata Kuliah:** TEK1314 - Keamanan Siber  
**Segmen Jaringan:** 192.168.12.0/24  
**Netmask:** 255.255.255.0 (/24)  

| Hostname | IP Address | Peran / Node | OS yang Direncanakan | Keterangan / Port Terbuka |
| :--- | :--- | :--- | :--- | :--- |
| **v-target-srv** | 192.168.12.5 | Target Node (Korban) | Metasploitable 2 / Ubuntu Server | Port 80 (HTTP), 21 (FTP), 22 (SSH), 3306 (MySQL) |
| **v-attacker** | 192.168.12.100 | Attacker Node | Kali Linux | Port dinamis (Reconnaissance, Exploit Engine) |
| **v-seconion-mgmt** | 192.168.12.200 | Monitoring Node (Mgmt) | Security Onion | Interface eth0: Akses Web UI, Kibana, SOC Analyst |
| **v-seconion-sniff** | *No IP (Promiscuous)* | Monitoring Node (Sensor) | Security Onion | Interface eth1: Tap/SPAN Port pemantau trafik |

### Catatan Alokasi Jaringan:
1. **Target Server (192.168.12.5):** Dikonfigurasi statis, menjalankan web server rentan untuk skenario eksploitasi Red Team.
2. **Attacker Node (192.168.12.100):** Bertindak sebagai mesin ofensif untuk scanning (Nmap), sniffing, dan peluncuran eksploitasi.
3. **Monitoring Node (192.168.12.200):** Menggunakan 2 antarmuka jaringan: satu interface ber-IP untuk manajemen dasbor SOC, dan satu interface promiscuous tanpa IP untuk menangkap seluruh paket di segmen `192.168.12.0/24`.