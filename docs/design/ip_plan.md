# Skema Pengalamatan IP - Kelompok 12 Kelas B

**Subnet Laboratorium:** 192.168.12.0/24  
**Netmask:** 255.255.255.0  
**Mode Jaringan VirtualBox:** Host-Only dengan konfigurasi IP statis pada seluruh node guna menjamin isolasi total lingkungan pengujian (tidak menggunakan mode Bridged).

## Alokasi Alamat dan Peran Node

| Nama Host | Alamat IP | Peran Fungsional | Sistem Operasi | Port Layanan dan Keterangan |
| :--- | :--- | :--- | :--- | :--- |
| SRV-IOT-KEL12-B | 192.168.12.5 | Target Node (Replika Backend IoT) | Arch Linux Security Workstation | Port 22 (SSH), Port 80 (Dashboard Nginx), Port 1883 (Broker MQTT), Port 9000 (REST API internal via loopback) |
| ATTACKER-KEL12-B | 192.168.12.100 | Attacker Node | Ubuntu 22.04 LTS | Nmap, tcpdump, Wireshark, skrip pengujian berbasis Python |
| SOC-KEL12-B | 192.168.12.200 | Monitoring Node (Manajemen) | Security Onion | Antarmuka manajemen untuk aplikasi Sguil dan Squert |
| SOC-KEL12-B-sniff | Tanpa IP (Promiscuous) | Monitoring Node (Sensor) | Security Onion | Menangkap dan menganalisis lalu lintas jaringan 192.168.12.0/24 |
| Host Laptop | 192.168.12.1 | Host Administrasi | Windows | Manajemen hypervisor VirtualBox dan pengujian akses web |

## Layanan pada Target Node

| Port / Protokol | Layanan | Status Akses Setelah Hardening | Fokus Pengujian Keamanan |
| :--- | :--- | :--- | :--- |
| 22/TCP | OpenSSH | Akses dibatasi pada subnet 192.168.12.0/24, autentikasi berbasis kunci, login root ditolak, pembatasan laju koneksi aktif | Percobaan login berulang dan ketahanan pembatasan koneksi |
| 80/TCP | Nginx (Dashboard & Proxy) | Akses dibuka untuk subnet 192.168.12.0/24, banner versi perangkat lunak disembunyikan | Pengujian kebocoran versi dan mitigasi manipulasi API |
| 1883/TCP | Broker MQTT | Akses dibuka untuk subnet 192.168.12.0/24, otentikasi wajib, pembatasan ACL topik aktif | Pengujian publish tanpa hak akses dan perlindungan kanal kontrol |
| 9000/TCP | REST API Replika | Dibatasi hanya pada antarmuka loopback (127.0.0.1), tidak dapat diakses dari jaringan luar | Validasi rentang data sensor dan otentikasi token bearer |

Port layanan yang tidak digunakan seperti 21 (FTP), 23 (Telnet), dan 3306 (MySQL) telah dinonaktifkan dan diblokir oleh firewall. Tidak ada service listener lain yang terbuka di luar daftar di atas.

## Diagram Alur Komunikasi

```text
Simulator Sensor (Telemetri dummy dikirim tiap 2 detik)
                  |
                  | HTTP :9000 (Loopback internal)
                  v
       API Replika pada Target Node (192.168.12.5)
       Path: devices/cow-sprinkler-01/...
                  ^
                  | HTTP :80
                  v
       Nginx Dashboard & Proxy Terbalik (/api)

Attacker (192.168.12.100) --(SSH 22, HTTP 80, MQTT 1883)--> Target (192.168.12.5)
                                                                 |
                                       Mode Promiscuous          v
                               Security Onion Sensor Node (192.168.12.200)
```

## Catatan Teknis

1. Target Node menggunakan citra Arch Linux Security Workstation yang disediakan di laboratorium, menggantikan rencana awal Ubuntu Server. Peran operasional dan alokasi port tetap identik.
2. Attacker Node hanya diarahkan ke alamat IP 192.168.12.5 dan tidak memiliki rute jaringan ke luar segmen laboratorium.
3. Security Onion mengoperasikan dua kartu jaringan virtual: satu antarmuka beralamat IP untuk manajemen sistem, dan satu antarmuka tanpa IP berkonfigurasi *promiscuous mode* khusus untuk penyadapan paket jaringan.
4. Aturan firewall disimpan secara permanen pada berkas `/etc/iptables/iptables.rules` dan dimuat otomatis saat proses boot melalui unit `iptables.service`. Langkah ini memastikan aturan keamanan tidak hilang saat mesin virtual dinyalakan ulang.
