# LOGBOOK - Kelompok 12 Kelas B

**Praktik Keamanan Siber Terapan (TEK1314) | Skenario 10 - IoT Protocol Guardian**

| Nama | NIM | Peran |
| :--- | :--- | :--- |
| Thevan Erlangga | J0404241073 | Lead, Purple Team |
| Muhamad Akhdan Ramadhan | J0404241102 | Red Team |
| Fachri Abyasa Tarid | J0404241136 | Blue Team |

## Daftar Isi

- [Minggu 2](#minggu-2)
- [Minggu 3](#minggu-3)
- [Minggu 4](#minggu-4)
- [Minggu 5 (26 September 2026)](#minggu-5-26-september-2026)
- [Minggu 6 (3 Oktober 2026)](#minggu-6-3-oktober-2026)
- [Minggu 7](#minggu-7)
- [Minggu 8 dan 9 - Checkpoint Evaluasi Fase 2](#minggu-8-dan-9---checkpoint-evaluasi-fase-2)
- [Minggu 10](#minggu-10)
- [Minggu 11 - Finalisasi Fase 2](#minggu-11---finalisasi-fase-2)
- [Minggu 12 - Verifikasi Ulang Fase 2](#minggu-12---verifikasi-ulang-fase-2)

## Minggu 2

- Pembentukan tim dan pembagian peran fungsional: Lead/Purple Team, Red Team, dan Blue Team.
- Pemasangan perangkat lunak virtualisasi VirtualBox pada host, dilanjutkan pengunduhan citra Ubuntu, Kali Linux, dan Security Onion.
- Inisialisasi repositori Git dan GitHub sebagai media dokumentasi progres, pengelolaan berkas konfigurasi, dan penyimpanan artefak pengujian.

## Minggu 3

- Pendalaman administrasi Linux: manajemen berkas, hak akses pengguna, dan konfigurasi antarmuka jaringan.
- Red Team meninjau port standar yang relevan dengan arsitektur IoT: 80 (HTTP), 21 (FTP), 22 (SSH), dan 1883 (MQTT).
- Evaluasi teknis: administrasi Linux dan analisis jaringan menjadi dasar troubleshooting. Tanpa penguasaan dasar tersebut, pelacakan kendala pada sensor IDS berlapis membutuhkan waktu jauh lebih lama.

## Minggu 4

- Blue Team merancang topologi tiga node: Attacker Node, Target Node, dan Monitoring Node.
- Penetapan alamat pada subnet `192.168.12.0/24`: Target Node `.5`, Attacker Node `.100`, dan Security Onion `.200`.
- Lead menyusun dan mengunggah rancangan skema IP (`docs/design/ip_plan.md`) beserta diagram topologi.
- Identifikasi sistem operasi Target Node: citra lab yang tersedia adalah Arch Linux Security Workstation, bukan Ubuntu Server seperti rencana awal. Peran operasionalnya tetap server replika backend IoT.

## Minggu 5 (26 September 2026)

- Antarmuka Host-Only pada host disetel ke `192.168.12.1`; seluruh VM dipindahkan ke mode Host-Only agar lingkungan uji terisolasi.
- Attacker Node (LabVM): IP `192.168.12.100`, hostname `ATTACKER-KEL12-B`, pengguna `analyst`.
- Target Node (Arch Linux Workstation): kata sandi `sec_admin` dipulihkan lewat menu GRUB (`init=/bin/bash`), driver grafis disesuaikan (VBoxVGA, VRAM 64MB), IP statis `192.168.12.5`, hostname `SRV-IOT-KEL12-B`.
- Security Onion: IP `192.168.12.200` pada eth0, hostname `SOC-KEL12-B`, pengguna `analyst`.
- Uji konektivitas: ping dari Attacker Node ke Target Node dan Security Onion menghasilkan 0% packet loss.
- Rekaman tcpdump pada antarmuka sensor menangkap 12 paket ICMP tanpa kehilangan data (`docs/blueteam/evidence/baseline/tcpdump-icmp.png`).
- Visualisasi Sguil: jendela Sguil terbuka, tetapi tabel RealTime Events belum menampilkan alert. Investigasi menemukan dua penyebab, yaitu `IDS_ENGINE_ENABLED=no` dan izin mode promiscuous pada adapter virtual yang belum disetel allow. Setelah keduanya diperbaiki dan sensor dijalankan ulang dengan `nsm_sensor_ps-start`, basis data sguild mencatat alert ICMP ping (`GPL ICMP_INFO PING`) dan pemindaian SSH (`ET SCAN Potential SSH Scan`) dari `.100` ke `.5` (`docs/blueteam/evidence/baseline/sguil-db-events.log`).
- Wireshark pada Attacker Node merekam 45 paket pengujian (`docs/blueteam/evidence/baseline/wireshark-icmp.png` dan `kel12-demo.pcap`).
- Tangkapan layar Sguil pada sensor seconion-import didokumentasikan di `docs/blueteam/evidence/baseline/sguil-alert.png`.
- Evaluasi teknis: penangkapan paket mentah dan pemrosesan alert IDS adalah dua lapisan berbeda. tcpdump dapat merekam paket secara utuh meskipun basis data Sguil belum menampilkan alert. Setelah mesin Snort aktif dan antarmuka sensor disetel promiscuous, alur korelasi dari Snort melalui barnyard2 ke basis data sguild berjalan normal.

## Minggu 6 (3 Oktober 2026)

- Target Node (`SRV-IOT-KEL12-B`): penonaktifan layanan yang tidak dibutuhkan (`vsftpd`, `telnet.socket`, `pox`, `ovs-vswitchd`). Layanan yang dipertahankan hanya `sshd`, `systemd-networkd`, dan `lightdm`, diverifikasi dengan `systemctl list-unit-files --state=enabled`.
- Firewall iptables: kebijakan default INPUT DROP, dengan izin ICMP dan TCP 22, 80, serta 1883 khusus dari `192.168.12.0/24`. Ping dari Attacker Node tetap 0% loss, sehingga aturan tidak mengganggu konektivitas sah.
- Hak akses: akun non-root `sec_admin` (UID 1001) ditetapkan sebagai akun operasional. IP disetel permanen pada `192.168.12.5/24`.
- Keterbatasan lingkungan: `pacman -Syu` tidak dapat dijalankan karena isolasi jaringan lab tanpa internet. Kondisi ini dicatat sebagai batasan uji.
- Bukti: `docs/blueteam/evidence/baseline/hardening-services.png` dan `hardening-firewall.png`. Tangkapan layar `target-ip-statis.png` ditarik dari repositori karena memuat kata sandi; bukti IP dan hostname terkini ada pada `docs/blueteam/evidence/verifikasi-ulang/06-target-state-recon.log`.

## Minggu 7

- Penyusunan dan finalisasi Baseline Security Report Fase 1.
- Perancangan skenario demonstrasi bertahap: pembuktian topologi dan konektivitas, verifikasi kontrol pengamanan, lalu pembuktian pencatatan log secara langsung.

## Minggu 8 dan 9 - Checkpoint Evaluasi Fase 2

Penetapan skenario tugas kelompok: **Skenario No. 10 (*IoT Protocol Guardian*)**. Proyek yang dipelajari adalah **SmartCow**, sistem pengendali sprinkler otomatis kandang sapi perah. Rincian arsitektur ada pada `docs/presentation-minggu9/tech_stack_declaration.md`. Seluruh pengujian memakai data sintetis (dummy) demi keselamatan sistem mitra.

### Perbaikan Lingkungan Jaringan Laboratorium

- Kendala DHCP: VM Attacker sempat menerima alamat `192.168.18.6` dari server DHCP default VirtualBox. Alamat dikonfigurasi ulang secara statis ke `192.168.12.100` memakai Netplan, dan uji konektivitas ke `.5` menghasilkan 0% packet loss.
- Persistensi firewall: aturan iptables yang tereset setelah restart dimuat ulang, diekspor ke `/etc/iptables/iptables.rules`, dan `iptables.service` diaktifkan agar termuat saat boot.
- Logging: penyimpanan systemd-journald disetel persisten, dan akun nonaktif `analyst` pada Target Node dikunci.

### Implementasi Replika Backend IoT pada Target Node

Ketiadaan akses internet mencegah instalasi Firebase Emulator, sehingga kelompok membangun replika backend mandiri dengan pustaka standar Python 3.9 tanpa dependensi pihak ketiga:

- `app.py`: REST API bergaya Realtime Database pada path `devices/cow-sprinkler-01/{telemetry/latest,telemetry/log,control,status,events}`, dengan otentikasi token bearer, validasi rentang sensor, dan log akses.
- `broker.py`: broker MQTT minimal dengan otentikasi akun dan pembatasan hak topik (ACL); topik `cow-sprinkler-01/control` dibatasi hak tulisnya.
- `simulator.py`: simulator telemetri yang meniru ESP32 dengan mengirim nilai suhu dan kelembapan dummy setiap dua detik untuk membentuk lalu lintas baseline IDS.
- Nginx 1.18.0: menyajikan dashboard pada port 80 dan meneruskan rute `/api` ke backend lokal melalui proxy terbalik.
- Manajemen layanan: seluruh komponen berjalan sebagai unit systemd di bawah akun sistem non-privilese `smartcow`.

### Penerapan Sepuluh Kontrol Pengamanan (Hardening)

Sepuluh kontrol terbagi ke tiga kategori: 3 Access & Authentication, 4 Service & Attack Surface, dan 3 Data & Application (rincian pada `docs/blueteam/hardening_checklist.md`).

- **Kategori A (Access & Authentication):** A1 penolakan login root via SSH; A2 autentikasi SSH berbasis kunci Ed25519 dan penonaktifan kata sandi; A3 pembatasan `MaxStartups 3:50:10` dan pembatasan laju koneksi iptables hashlimit.
- **Kategori B (Service & Attack Surface):** B1 firewall iptables whitelist persisten; B2 isolasi REST API pada loopback `127.0.0.1:9000`; B3 penyembunyian banner versi Nginx (`server_tokens off`); B4 penutupan akses jaringan ke broker MQTT.
- **Kategori C (Data & Application):** C1 validasi batas nilai telemetri dan ACL topik MQTT; C2 penghapusan literal token, izin berkas kredensial mode 600, dan rotasi token; C3 pencatatan log akses tersanitasi serta verifikasi prosedur backup/restore.

### Hasil Pengujian Serangan Red Team

Seluruh skenario diuji nyata memakai data dummy untuk memverifikasi efektivitas kontrol:

- **Kondisi Sebelum Hardening Fase 2:** Pemindaian Nmap mencatat port 22, 80, dan 1883 terbuka. Port 9000 sudah berstatus filtered karena API mendengarkan di `0.0.0.0:9000` tetapi tidak pernah diloloskan firewall. Login SSH `sec_admin` berhasil dengan kata sandi sederhana. Publikasi MQTT ke topik kontrol diterima broker tanpa kredensial. Injeksi telemetri palsu (kelembapan 150%) dan perintah aktivasi pompa manual diterima REST API.
- **Kondisi Sesudah Hardening:** Upaya login SSH berbasis kata sandi ditolak (`Permission denied (publickey)`). Publikasi MQTT tanpa otorisasi ditolak broker dengan `CONNACK 5`. Injeksi di luar batas ditolak REST API dengan `HTTP 400 Bad Request`, dan request tanpa token ditolak `HTTP 401 Unauthorized`. Port 1883 ditutup lewat kontrol B4, sedangkan port 9000 tetap filtered dan hanya melayani loopback; pemindaian akhir hanya menemukan 22 dan 80 terbuka.
- Bukti: `docs/blueteam/evidence/` (71 berkas) dan `docs/redteam/evidence/` (19 berkas), termasuk tangkapan layar terminal dan log eksekusi.

### Hasil Analisis dan Kendala Monitoring Node

- **Konfigurasi antarmuka:** antarmuka manajemen Security Onion pada citra lab awalnya memakai `192.168.0.1/24` (eth1) dan NAT (eth2), lalu dikonfigurasi ulang statis ke `192.168.12.200/24` melalui NetworkManager (`ipv4.method manual`, `ipv4.never-default yes`). Bukti kondisi awal: `docs/blueteam/evidence/monitoring-node/sebelum-eth2-dhcp-nat.png`; daftar listener layanan: `docs/blueteam/evidence/monitoring-node/daftar-listener-onion.png`.
- **Karakteristik sensor:** Security Onion memakai mesin Snort dengan korelasi basis data melalui barnyard2 ke `sguildb`.
- **Verifikasi alert Sguil:** antarmuka Sguil memvalidasi alert lalu lintas penyerangan (`ET SCAN Nmap Scripting Engine`, `ET POLICY curl User-Agent`, dan `ET SCAN Potential SSH Scan`) pada 06:30 sampai 06:47 GMT (13:30 sampai 13:47 WIB). Bukti: `docs/blueteam/evidence/sguil-alert-minggu9.png`.
- **Kendala isolasi:** lingkungan lab tanpa internet dan memori host terbatas, sehingga pengujian dijalankan terukur memakai skrip Python mandiri dengan pemakaian sumber daya efisien.

## Minggu 10

- Red Team merancang dan menguji skenario ofensif Fase 2: RT-01 pemetaan port, RT-02 eksploitasi SSH, RT-03 manipulasi MQTT dan injeksi REST, RT-04 replay pesan kendali.
- Blue Team menambahkan signature Snort kustom pada `/etc/nsm/rules/local.rules`:
  - SID 1000001: `LOCAL-TEST-ICMP` untuk verifikasi keterhubungan.
  - SID 1000002: `SMARTCOW-MQTT Unauthorized Control Topic Access` untuk penulisan tanpa izin ke topik kontrol.
  - SID 1000003: `SMARTCOW-HTTP Telemetry Attack Injection` untuk upaya injeksi telemetri.
- Verifikasi rule update: proses Snort dan Barnyard2 memuat aturan baru tanpa galat.
- Penyesuaian jaringan Attacker Node: IP disetel permanen `192.168.12.100/24` melalui Netplan agar komunikasi antar-node stabil pada segmen Host-Only.

## Minggu 11 - Finalisasi Fase 2

- Replikasi antarmuka web SmartCow: seluruh aset web asli (dashboard Overview, kartu suhu dan kelembapan, status SSR, tabel riwayat telemetri, log pompa, manajemen akses admin) dipindahkan ke `/usr/share/nginx/html/` dengan adapter JavaScript offline tanpa dependensi CDN.
- Penyesuaian performa: efek visual berat (animasi CSS, blur, bayangan kompleks) dimatikan dan interval polling disetel 4 detik agar pemakaian CPU Target Node tetap rendah (sekitar 4%).
- Penyelesaian siklus Purple Team lima tahap untuk RT-01 sampai RT-04:
  - RT-01: Nmap dari Attacker Node memastikan port 9000 filtered dan header web server menyembunyikan nomor versi.
  - RT-02: brute force kata sandi ditolak autentikasi kunci Ed25519, dan laju koneksi konkuren diredam firewall.
  - RT-03: publish tanpa otentikasi ditolak dengan `CONNACK 5`, dan injeksi data sensor ditolak dengan `HTTP 400`.
  - RT-04: replay paket kendali ditolak aturan ACL broker dan oleh anti-replay stempel waktu pada kanal tulis (`SMARTCOW_MQTT_ANTIREPLAY=1`, jendela 120 detik); token lama ditolak `HTTP 401`; percobaan terdeteksi Snort dengan CID 6127, diverifikasi ulang lewat query basis data pada sesi verifikasi ulang. Bukti: `docs/redteam/evidence/15-replay-sebelum-diterima.png` sampai `17-catatan-broker-replay.png`.
- Verifikasi C3: uji coba 20 Oktober 2026 berhenti di langkah pencadangan karena `tar` gagal membaca berkas arsip yang belum ada, sehingga klaim pemulihan berbasis hash SHA256 pada catatan sebelumnya belum punya bukti. Penjadwalan dan pengujian ulang yang valid dilakukan pada sesi verifikasi ulang.
- Penyusunan Vulnerability Assessment Report sebagai laporan formal Fase 2 di `docs/vulnerability-assessment-report.md`.
- Pemutakhiran repositori dengan seluruh artefak pengujian dan dokumentasi.

## Minggu 12 - Verifikasi Ulang Fase 2

- Pemulihan struktur Fase 1: artefak baseline yang terhapus pada commit restrukturisasi dikembalikan dari riwayat repositori dan ditempatkan sesuai Bagian XI Panduan PBL, yaitu `docs/blueteam/baseline-report.md` dan `docs/blueteam/evidence/baseline/`. Diagram kondisi akhir Fase 2 dipasang sebagai `docs/design/topology-akhir-fase2.png` dan dipakai pada `README.md` serta `ip_plan.md`, sedangkan `docs/design/topology-minggu9.png` dipertahankan sebagai snapshot Minggu 9 dan `topology.png` dirujuk pada `ip_plan.md` sebagai rancangan awal Minggu 4. Folder `scripts/smartcow-lab/` juga dikembalikan agar kode yang terpasang di Target Node dapat ditelusuri.
- Perbaikan topologi: server DHCP VirtualBox pada jaringan Host-Only dipindahkan ke rentang `192.168.12.3` sampai `192.168.12.254`, lalu antarmuka Attacker disetel statis `192.168.12.100/24` dengan gateway `192.168.12.1`. Ketiga node saling terhubung dan merespons ping dari host tanpa kehilangan paket.
- Uji ulang C1 di Target Node yang hidup: 6 dari 6 pemeriksaan lulus. Tangkapan layar `mqtt-acl-terverifikasi.png` dari 20 Oktober 2026 hanya memuat kegagalan `Permission denied` saat skrip dijalankan dan memperlihatkan kredensial broker, sehingga berkas itu ditarik dan bukti utama diganti log eksekusi.
- Perbaikan C3: skrip `/usr/local/bin/smartcow-backup` dilengkapi checksum arsip dan manifest sha256 per berkas, ditambah retensi tujuh arsip. Skrip dipasang `root:root` mode 750 agar tidak dapat ditimpa pengguna layanan. Unit `smartcow-backup.service` dan `smartcow-backup.timer` diaktifkan, lalu pencadangan dijalankan. Uji gerbang keamanan dengan manifest yang dirusak ditolak tanpa menyentuh data (`rc=1`), sedangkan pemulihan sah berhasil, menyisakan salinan `data.prev-<stempel>`, dan `/health` kembali `200`.
- Monitoring: rantai deteksi lengkap berjalan (`snort`, `barnyard2`, `sguild`, `mysqld`). Pengujian ulang dari Attacker Node menghasilkan alert kustom yang masuk basis data, yaitu CID 6352 (SID 1000003, injeksi HTTP) dan CID 6356 (SID 1000002, publish topik kontrol). Alert lama CID 6125 dan 6127 masih tersimpan. Catatan: kolom `event.sid` pada basis data Sguil berisi ID sensor, bukan SID Snort; SID Snort ada pada kolom `signature_id`.
- Penanganan kredensial: sebelas tangkapan layar yang memuat kata sandi atau token ditarik dari repositori dan tautannya dialihkan ke bukti log tersanitasi. Kredensial broker MQTT akun `esp32` dirotasi karena nilainya terlihat pada tangkapan layar lama; berkas lama disimpan sebagai `mqtt_users.json.bak-<stempel>` mode 600, dan uji C1 dijalankan ulang setelah rotasi (6/6 lulus).
- Seluruh hasil pemeriksaan tersimpan sebagai berkas teks di `docs/blueteam/evidence/verifikasi-ulang/` (berkas `01` sampai `15`).
- Pemasangan skrip repositori di Target Node: `app.py` versi repositori (validasi body JSON, token gagal-tertutup saat kosong, direktori data dirapikan) menggantikan versi lama, bersama `smartcow-backup`, `smartcow-restore`, dan `smartcow-restore-check` milik `root:root` mode 750. Salinan versi lama disimpan di `/root/rollback-<stempel>` sebelum penggantian.
- Batas kepercayaan arsip diperbaiki: arsip dipindahkan dari `/home/smartcow-lab/backup` ke `/var/lib/smartcow/backup` milik `root:root` mode 700. Direktori arsip di dalam home layanan masih dapat dihapus dan dibuat ulang oleh `smartcow`, sehingga checksum palsu mungkin ditanam. Setelah pemindahan, `smartcow` gagal membuka, menulis, dan menghapus direktori arsip, sedangkan uji pemulihan non-destruktif tetap lulus 4 dari 4 berkas.
- Verifikasi ulang C1/C2 setelah pemasangan: 6 dari 6 pemeriksaan lulus. Token API lama ditolak `HTTP 401`, kedua sandi broker lama ditolak `CONNACK 5`, dan kredensial aktif tetap diterima. Telemetri tetap mengalir dan `/health` membalas 200.
- Jalur kata sandi SSH ditutup pada Attacker Node dan Monitoring Node (`PasswordAuthentication no`, cadangan `sshd_config.bak-hardening-<stempel>`). Kata sandi akun tidak diubah, sehingga login konsol dan Sguil tetap memakai nilai yang sama dan tidak ada akun terkunci; ketiga node kini hanya menerima `publickey`.
- Bukti baru: `13-backup-relocation-and-deploy.log`, `14-c1-credential-and-liveness-recheck.log`, dan `15-ssh-password-auth-disabled.log`.
- Penutupan celah Fase 1-2 pada sesi lanjutan yang sama:
  - Kontrol B4 diterapkan: aturan ACCEPT `tcp/1883` dihapus dari INPUT dan tabel disimpan ulang ke `/etc/iptables/iptables.rules`. Pemindaian Nmap dari Attacker Node turun dari tiga port terbuka (22, 80, 1883) menjadi dua (22, 80); pemindaian penuh `-p-` hanya menemukan 22 dan 80. Rollback terkontrol: `iptables -I INPUT -s 192.168.12.0/24 -p tcp --dport 1883 -j ACCEPT` lalu `iptables-save > /etc/iptables/iptables.rules`.
  - Anti-replay MQTT (CWE-294) diterapkan pada `broker.py` (`SMARTCOW_MQTT_ANTIREPLAY=1`, `SMARTCOW_MQTT_TS_WINDOW=120`, urutan `ts` wajib naik per topik) dan dipasang di Target Node. Uji unit 8/8 lulus; replay byte-identik dari Attacker Node ditolak dan tercatat `replay ditolak ... stempel waktu mundur atau duplikat` pada `broker.log`.
  - Jendela demonstrasi RT-02: `PasswordAuthentication` dikembalikan sementara ke `yes` (cadangan di `/root/backup-phase12-<stempel>`), `ssh_try.py` dijalankan dari Attacker Node (`sec_admin` BERHASIL, `root` GAGAL, kata sandi disamarkan), lalu konfigurasi dipulihkan ke `no` dan diverifikasi dengan `sshd -T` pada sesi yang sama.
  - Tangkapan layar pengganti: `docs/redteam/evidence/03-...`, `04-...`, `11-...`, `12-...`, `13-...` sampai `17-...`, serta `docs/blueteam/evidence/kontrol A1/A2/B1/C2/C3` (lihat `hardening_checklist.md` dan `purple-team-log.md`).
