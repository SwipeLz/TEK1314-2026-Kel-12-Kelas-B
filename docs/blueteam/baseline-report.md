# Baseline Report Fase 1 (Minggu 7) - Kelompok 12 Kelas B

> **Status dokumen.** Dokumen ini adalah potret kondisi akhir Minggu 7 (Fase 1, sebelum penyerangan). Isinya sengaja tidak diperbarui agar tetap menjadi pembanding kondisi *before*. Perubahan sesudahnya ada pada [hardening_checklist.md](hardening_checklist.md), [vulnerability-assessment-report.md](../vulnerability-assessment-report.md), dan [purple-team-log.md](../purple-team-log.md). Pemeriksaan ulang seluruh node pada 12 November 2026 ada di [evidence/verifikasi-2026-11-12/](evidence/verifikasi-2026-11-12/).

Lingkungan uji: subnet `192.168.12.0/24`, kondisi sebelum penyerangan Fase 2. Sistem sudah di-hardening pada Fase 1. Seluruh angka pada dokumen ini dapat dicek ulang pada berkas bukti yang ditautkan.

## Daftar Isi

- [1. Aset](#1-aset)
- [2. Hardening](#2-hardening)
- [3. Pemeriksaan Logging Minggu 5](#3-pemeriksaan-logging-minggu-5)
- [4. Demo Minggu 7](#4-demo-minggu-7)

## 1. Aset

| Hostname | IP | Sistem Operasi | Layanan |
| :--- | :--- | :--- | :--- |
| `SRV-IOT-KEL12-B` | 192.168.12.5 | Arch Linux Security Workstation | SSH 22; firewall hanya membuka 22, 80, dan 1883 |
| `ATTACKER-KEL12-B` | 192.168.12.100 | Ubuntu 22.04 LTS (Cisco LabVM), pengguna `analyst` | Nmap, ping, dumpcap/Wireshark |
| `SOC-KEL12-B` | 192.168.12.200 | Security Onion | tcpdump dan server Sguil |

Sensor IDS pada Monitoring Node belum terprovisioning saat itu, sehingga penangkapan paket langsung dipakai sebagai rencana cadangan. Detail alamat ada di [ip_plan.md](../design/ip_plan.md) dan diagram topologi di [topology-minggu9.png](../design/topology-minggu9.png).

Catatan sistem operasi: `ip_plan.md` awalnya merencanakan Ubuntu Server 22.04 atau Metasploitable 2, sedangkan lab memakai Arch Linux Security Workstation. Layanan dan port yang dibuka menyesuaikan kondisi tersebut; fungsi tiap node tetap sama.

## 2. Hardening

**Jaringan (iptables, karena Target Arch Linux tidak memakai UFW):**

- Kebijakan default INPUT DROP dan OUTPUT ACCEPT.
- ICMP serta TCP 22, 80, dan 1883 dibuka hanya dari `192.168.12.0/24`.
- Pemeriksaan memakai `sudo iptables -L -n -v --line-numbers`.

**Sistem:**

- Login memakai pengguna biasa `sec_admin` (UID 1001, non-root).
- Layanan yang tidak dipakai dimatikan: `vsftpd`, `telnet.socket`, `pox`, dan `ovs-vswitchd`, diverifikasi dengan `systemctl list-unit-files --state=enabled`.
- Pembaruan paket melalui pacman tidak berjalan karena segmen terisolasi tanpa internet. Kondisi ini dicatat sebagai keterbatasan, bukan disembunyikan.
- Mosquitto belum diinstal karena membutuhkan internet. Port 1883 dibuka di firewall sebagai persiapan skenario IoT Fase 2.

**Identitas:**

- Hostname: `SRV-IOT-KEL12-B`, `ATTACKER-KEL12-B`, dan `SOC-KEL12-B`.
- Alamat IP: `.5`, `.100`, dan `.200` pada `192.168.12.0/24`.
- Pemeriksaan memakai `hostnamectl` dan `ip addr`. Konsistensi hostname dan IP penting agar log Security Onion mudah ditelusuri.

## 3. Pemeriksaan Logging Minggu 5

Awalnya tabel Sguil kosong dan sempat diduga sensor rusak. Investigasi menemukan dua penyebab: mesin IDS dimatikan pada konfigurasi (`IDS_ENGINE_ENABLED=no`), dan NIC monitoring berstatus promiscuous deny sehingga tidak melihat trafik antar-VM. Setelah `IDS_ENGINE_ENABLED=yes`, izin promiscuous diubah menjadi allow, dan sensor dijalankan ulang dengan `nsm_sensor_ps-start`, rantai deteksi berjalan dan event tercatat.

Alur pemrosesan: `snort (eth0) -> unified2 -> barnyard2 -> sguild -> MySQL (sguildb.event)`.

Hasil uji dari Attacker Node `.100` ke Target Node `.5`:

- 10 kali ping tercatat sebagai `GPL ICMP_INFO PING *NIX`.
- 12 koneksi SSH ke port 22 tercatat sebagai `ET SCAN Potential SSH Scan` dan `ET SCAN Potential SSH Scan OUTBOUND`, lengkap dengan source port.
- Bukti basis data: [sguil-db-events.log](evidence/baseline/sguil-db-events.log) (timestamp, src, dst, signature).
- Bukti jendela Sguil: [sguil-alert.png](evidence/baseline/sguil-alert.png), sensor `seconion-import`, terlihat baris `192.168.12.100` ke `.5`.

Bukti lain di `evidence/baseline/`:

- [ping-attacker.log](evidence/baseline/ping-attacker.log): ping 0% loss.
- [tcpdump-icmp.png](evidence/baseline/tcpdump-icmp.png): capture langsung di Onion.
- [wireshark-icmp.png](evidence/baseline/wireshark-icmp.png) dan [kel12-demo.pcap](evidence/baseline/kel12-demo.pcap): 45 paket, rencana cadangan.
- [hardening-services.png](evidence/baseline/hardening-services.png) dan [hardening-firewall.png](evidence/baseline/hardening-firewall.png).
- Tiga tangkapan layar identitas node (`target-ip-hostname.png`, `target-ip-statis.png`, `onion-ip.png`) ditarik dari repositori karena memuat kata sandi. Bukti bebas kredensial ada pada [06-target-state-recon.log](evidence/verifikasi-2026-11-12/06-target-state-recon.log) dan [04-onion-state.log](evidence/verifikasi-2026-11-12/04-onion-state.log).

## 4. Demo Minggu 7

1. Menjelaskan topologi.
2. Menunjukkan berkas hardening.
3. Menunjukkan ping langsung yang tercatat di Security Onion.
4. Sesi tanya jawab tentang alasan pemilihan hardening: tutup layanan yang tidak perlu, buka seperlunya, dan catat semua aktivitas.

Urutan demo dibuat dari topologi, hardening, lalu live logging, agar penonton yang belum pernah membuka Security Onion dapat mengikuti. Setiap langkah menampilkan layar yang sama dengan tangkapan pada `evidence/baseline/`, sehingga klaim pada laporan ini dapat dipakai langsung sebagai bahan penjelasan tanpa slide tambahan.
