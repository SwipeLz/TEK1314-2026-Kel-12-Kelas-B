# Skema alokasi IP address - Kelompok 12 Kelas B

**Segmen:** 192.168.12.0/24
**Netmask:** 255.255.255.0
**Mode VirtualBox:** Host-Only, IP statis semua. Jangan pakai Bridged.

## Alokasi alamat

| Hostname | IP address | Peran | Sistem operasi | Port dan keterangan |
| :--- | :--- | :--- | :--- | :--- |
| SRV-IOT-KEL12-B | 192.168.12.5 | Target, replika backend IoT | Arch Linux Security Workstation | 22 SSH, 80 dashboard Nginx, 1883 broker MQTT, 9000 API hanya di loopback |
| ATTACKER-KEL12-B | 192.168.12.100 | Attacker | LabVM Ubuntu 22.04 | nmap, tcpdump, Wireshark, python3 |
| SOC-KEL12-B | 192.168.12.200 | Monitoring, management | Security Onion | antarmuka management untuk Sguil dan Squert |
| SOC-KEL12-B-sniff | tanpa IP, promiscuous | Monitoring, sensor | Security Onion | menangkap trafik 192.168.12.0/24 |
| Host laptop | 192.168.12.1 | Administrasi | Windows | Manage VirtualBox, akses ke API replika |

## Layanan pada Target Node

| Port | Layanan | Akses setelah hardening | Fokus pengujian |
| :--- | :--- | :--- | :--- |
| 22/TCP | SSH | Hanya dari 192.168.12.0/24, login key-based, root ditolak, rate limit untuk penyerang | Percobaan login berulang dan pemulihan akses |
| 80/TCP | Nginx, dashboard dan proxy `/api` | Hanya dari 192.168.12.0/24 | Penyembunyian versi, penyuntikan data lewat API |
| 1883/TCP | Broker MQTT | Hanya dari 192.168.12.0/24, wajib kredensial | Publish tanpa izin dan pemotongan topik |
| 9000/TCP | API replika (gaya RTDB) | Loopback saja, tidak terjangkau dari jaringan | Validasi input dan otentikasi token |

Port 21, 23, dan 3306 ditutup dan difilter. Tidak ada listener lain di luar
keempat port di atas.

## Alur komunikasi

```text
Simulator sensor (telemetri dummy tiap 2 detik)
                  |
                  | HTTP :9000 loopback
                  v
        API replika di Target Node 192.168.12.5
        path devices/cow-sprinkler-01/...
                  ^
                  | HTTP :80
                  v
        Nginx dashboard + proxy /api

Attacker 192.168.12.100  --(SSH 22, HTTP 80, MQTT 1883)-->  Target 192.168.12.5
                                                              |
                                  promiscuous               v
                              Security Onion sensor 192.168.12.200
```

## Catatan

1. Target memakai Arch Linux Security Workstation dari lab, bukan Ubuntu Server
   seperti rencana awal. Peran dan pembagian port tetap sama.
2. Attacker hanya boleh mengarah ke .5. Tidak ada rute ke luar segmen.
3. Security Onion memakai dua antarmuka: satu beralamat untuk management, satu
   tanpa alamat dengan mode promiscuous untuk sniffing.
4. Aturan iptables disimpan di `/etc/iptables/iptables.rules` dan dimuat ulang
   oleh `iptables.service`. Aturan yang hanya hidup di memori hilang begitu mesin
   restart, dan kejadian itu memang pernah terjadi.
