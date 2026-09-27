# Baseline report fase 1 (minggu 7) - Kelompok 12 Kelas B

Subnet 192.168.12.0/24. Kondisi before attack. Sistem sudah di-hardening sebelum diserang.

Semua bisa dicek ulang.

## 1. Aset

| Hostname | IP | OS | Service |
| :--- | :--- | :--- | :--- |
| SRV-IOT-KEL12-B | 192.168.12.5 | Arch Linux (Security Workstation) | SSH 22 (iptables hanya buka 22/80/1883) |
| ATTACKER-KEL12-B | 192.168.12.100 | Cisco LabVM Ubuntu (user analyst) | nmap, ping, dumpcap/Wireshark |
| SOC-KEL12-B | 192.168.12.200 | Security Onion | tcpdump, Sguil server (sensor IDS sempat belum provisioned, jadi capture paket dipakai sebagai Plan B) |

Detail IP ada di `../design/ip_plan.md`. Gambar ada di `../design/topology.jpeg`.

Catatan soal OS: `ip_plan.md` nulis rencana Ubuntu Server 22.04 atau Metasploitable 2. Yang kepakai di lab ternyata Arch Linux Security Workstation. Service dan port yang dibuka menyesuaikan kondisi itu.

Fungsinya tetap sama.

## 2. Hardening

Network (iptables, karena target Arch tanpa UFW):

* Default INPUT DROP, OUTPUT ACCEPT.
* Buka ICMP + TCP 22/80/1883 hanya dari 192.168.12.0/24.
* Cek pakai `sudo iptables -L -n -v --line-numbers`.

System:

* Login pakai user biasa sec_admin (uid 1001, non-root).
* Matikan service tidak dipakai: vsftpd, telnet.socket, pox, ovs-vswitchd (cek `systemctl list-unit-files --state=enabled`).
* Patch via pacman tidak jalan karena segmen isolasi tanpa internet. Kami catat sebagai keterbatasan, bukan diumpetin.
* Mosquitto/MQTT belum diinstal (butuh internet). Port 1883 dibuka di firewall sebagai persiapan skenario IoT fase 2.

Identitas:

* Hostname: SRV-IOT-KEL12-B, ATTACKER-KEL12-B, SOC-KEL12-B.
* IP: .5, .100, .200 di segmen 192.168.12.0/24.
* Cek pakai `hostnamectl` dan `ip addr`. Singkat. Kalau hostname atau IP meleset, log Onion susah dibaca.

## 3. Logging check minggu 5

Awalnya Sguil kosong. Kami kira sensor rusak.

Ternyata dua hal. IDS engine sensor mati di config (IDS_ENGINE_ENABLED=no). Dan NIC monitoring mode promiscuous deny, jadi tidak melihat trafik antar VM. Setelah dibetulkan (IDS_ENGINE_ENABLED=yes + promiscuous allow-all + sensor direstart resmi pakai nsm_sensor_ps-start), rantai deteksi jalan. Sebelum diperbaiki, Sguil cuma pajangan karena tidak ada satu pun event yang nyangkut, dan setelah dua setelan itu dibetulkan plus sensor direstart dengan prosedur resmi, semua pengujian yang tadinya sepi langsung tercatat satu per satu, dan sejak saat itu semua pengujian tercatat rapi tanpa jeda sama sekali.

snort (eth0) -> unified2 -> barnyard2 -> sguild -> MySQL (sguildb.event).

Hasil uji (attacker .100 ke target .5):

* 10x ping: tercatat sebagai GPL ICMP_INFO PING *NIX.
* 12x koneksi SSH ke port 22: tercatat sebagai ET SCAN Potential SSH Scan (+ OUTBOUND), lengkap dengan source port.
* Bukti database: `assets/sguil-db-events.log` (timestamp, src, dst, signature).
* Bukti jendela Sguil: `assets/sguil-alert.png` (pilih sensor seconion-import, terlihat baris 192.168.12.100 ke .5).

Bukti lain di `assets/`:

* `ping-attacker.log` (ping 0% loss)
* `tcpdump-icmp.png` (capture live di Onion)
* `wireshark-icmp.png` + `kel12-demo.pcap` (45 paket, Plan B)
* `target-ip-hostname.png`, `target-ip-statis.png`, `onion-ip.png`
* `hardening-services.png`, `hardening-firewall.png`

## 4. Demo minggu 7

1. Jelaskan topologi.
2. Tunjukkan file hardening.
3. Tunjukkan live ping tercatat di Onion.
4. Q&A alasan pilih hardening tersebut. Intinya: tutup yang tidak perlu, buka seperlunya, catat semua.

Demo diurut dari topologi ke hardening ke live logging supaya penonton yang belum pernah buka Security Onion tetap bisa ngikutin, karena tiap langkah nunjukin layar yang sama dengan yang ada di screenshot assets, dan sesi tanya jawab di akhir khusus ngebahas alasan tiap aturan dibuka atau ditutup. Urutan ini juga ngebantu kami sendiri, karena tiap klaim di laporan ini kepakai langsung sebagai bahan omongan tanpa perlu nyiapin slide tambahan.
