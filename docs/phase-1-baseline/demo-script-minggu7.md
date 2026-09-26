# Script Demo Minggu 7 (10-15 menit) - Kelompok 12 Kelas B

Total 12 menit. Yang demo buka 3 jendela: VirtualBox (3 VM), GitHub repo, file ini.

## 0. Pembuka (1 menit)

> Kami Kelompok 12 Kelas B. Subnet 192.168.12.0/24, terisolasi Host-Only.
> Skenario: satu VM target dianggap server alat IoT, diserang Red Team, dipantau Blue Team.
> Anggota: Thevan (Lead), Akhdan (Red Team), Fachri (Blue Team).

Tunjukkan struktur repo di GitHub: `docs/design/`, `docs/phase-1-baseline/assets/`, `LOGBOOK.md`.

## 1. Topologi (3 menit)

Buka `docs/design/topology.jpeg`. Jelaskan:

* `ATTACKER-KEL12-B` (.100, LabVM Ubuntu) kirim ping + scan.
* `SRV-IOT-KEL12-B` (.5, Arch) sebagai target / server IoT.
* `SOC-KEL12-B` (.200, Security Onion) memonitor, NIC promiscuous.
* Semua Host-Only, tidak menyentuh Wi-Fi kampus. Serangan hanya ke .5.

Bukti: `docs/design/ip_plan.md` (tabel IP + port 22/80/21/1883).

## 2. Hardening walkthrough (4 menit) - di VM target

Ketik di terminal target (user sec_admin):

```
hostnamectl --static
ip -4 -o addr show dev eth0
sudo iptables -L -n -v --line-numbers
systemctl list-unit-files --state=enabled | head -12
id
```

Yang ditunjuk:
* hostname SRV-IOT-KEL12-B, IP 192.168.12.5/24 statis permanen (file /etc/systemd/network/10-static.network).
* iptables default INPUT DROP, buka ICMP + TCP 22/80/1883 hanya dari 192.168.12.0/24.
* Service berbahaya mati: vsftpd, telnet.socket, pox, ovs-vswitchd. Sisa sshd, networkd, lightdm.
* Login non-root sec_admin (uid 1001).

Bukti repo: `assets/hardening-firewall.png`, `assets/hardening-services.png`, `assets/target-ip-statis.png`.

Kalau ditanya UFW: target ini Arch tanpa UFW, jadi pakai iptables langsung (fungsinya sama).

## 3. Logging verification live (4 menit)

Di attacker, ketik:

```
ping -c 5 192.168.12.5
```

Sambil jalan, jelaskan: paket ini lewat segmen host-only dan ditangkap Onion (bukti tcpdump kemarin: `assets/tcpdump-icmp.png`, 12 packets 0 dropped).

Lalu tunjukkan `assets/wireshark-icmp.png` (45 paket: ICMP request/reply .100 ke .5 + ARP) dan sebut file `assets/kel12-demo.pcap` bisa dibuka di Wireshark.

Jujur soal Sguil: Sguil dibuka dan konek, tapi RealTime Events kosong karena service IDS snort/suricata tidak ter-provision di VM ini (yang jalan hanya pipeline elastic/kibana/logstash). Sesuai panduan ini kasus Plan B: bukti manual via tcpdump + Wireshark + log, yang dinilai analisisnya.

## 4. Q&A (sisanya)

| Pertanyaan | Jawaban |
|---|---|
| Kenapa Arch bukan Ubuntu? | VM yang dikasih lab untuk target adalah Arch Security Workstation. Disesuaikan, hardening via iptables + systemd. |
| Kenapa Sguil kosong? | Sensor IDS tidak ter-provision (tidak ada proses snort/suricata, container so-suricata tidak ada). Pipeline Up. Dipakai Plan B sesuai panduan. |
| Kenapa belum patch/update? | Segmen isolasi tanpa internet (target cuma Host-Only). pacman butuh internet. Dicatat di LOGBOOK sebagai keterbatasan. |
| Kenapa MQTT belum jalan? | Mosquitto butuh download (tidak ada internet di segmen). Port 1883 sudah dibuka di firewall sebagai persiapan Fase 2. |
| Kenapa IP statis, bukan DHCP? | Wajib segmen unik Kel-12 dan IP tetap agar bukti log konsisten + tidak nyerang IP lain. |
| Kenapa matikan ftp/telnet? | Tidak dipakai skenario, memperkecil permukaan serangan. FTP/telnet kirim password plaintext. |
| Kenapa ICMP dibuka kalau firewall ketat? | Agar Logging Check Minggu 5 bisa dibuktikan (ping tercatat). Di Fase 2 bisa diperketat lagi. |
| Password sec_admin? | Direset ke kel12admin via GRUB init=/bin/bash karena password awal tidak diberikan. |

## Checklist sebelum maju

* [ ] 3 VM running
* [ ] Dari attacker: `ping -c 2 192.168.12.5` dan `ping -c 2 192.168.12.200` 0% loss
* [ ] Repo sudah di-push terakhir, LOGBOOK Minggu 7 diisi setelah demo
* [ ] Buka tab: topology.jpeg, ip_plan.md, baseline-report.md, folder assets/
