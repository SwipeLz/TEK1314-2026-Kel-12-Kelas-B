# Hardening checklist — Target SRV-IOT-KEL12-B (192.168.12.5)

Standar panduan: minimal 8 kontrol, minimal 2 per kategori A/B/C, tiap kontrol
ada bukti before/after. Kami pasang 9. Status per 3 Okt 2026.

Sembilan, bukan delapan. Angka itu bukan gaya-gayaan karena tiap kontrol di
bawah lahir dari temuan langsung di target, mulai dari aturan firewall yang
ternyata hilang sampai akun nganggur yang masih bisa login, jadi tidak ada
satu pun yang dipasang sekadar biar tabelnya penuh.

## Kategori A — Access & authentication

| ID | Kontrol | Status | Bukti |
| :--- | :--- | :--- | :--- |
| A1 | `PermitRootLogin no` (sebelumnya `without-password`) | Selesai | `evidence/sshd-before.log`, `evidence/sshd-after.log`, login root ditolak |
| A2 | `AllowUsers sec_admin` (SSH hanya untuk user operasional) | Selesai | `evidence/sshd-after.log` (`allowusers sec_admin`) |
| A3 | `MaxAuthTries 3` + `LoginGraceTime 60` (sebelumnya 6 / default) | Selesai | `evidence/sshd-before.log`, `evidence/sshd-after.log` |

## Kategori B — Service & attack surface

| ID | Kontrol | Status | Bukti |
| :--- | :--- | :--- | :--- |
| B1 | iptables default INPUT DROP, whitelist ICMP + TCP 22/80/1883 dari 192.168.12.0/24; rules disimpan + service enabled (tahan reboot) | Selesai | `evidence/iptables-before.log` (kosong!), `evidence/iptables-after.log`, `/etc/iptables/iptables.rules` |
| B2 | Verifikasi attack surface: hanya sshd yang listen; 21/23/3306 filtered, 80/1883 closed | Selesai | `docs/redteam/evidence/nmap-target-after.log` |
| B3 | Kunci akun tak terpakai (`passwd -l analyst`); tidak ada password kosong | Selesai | `evidence/users-after.log` (analyst LOCKED, tanpa EMPTY) |

## Kategori C — Data & application

| ID | Kontrol | Status | Bukti |
| :--- | :--- | :--- | :--- |
| C1 | SSH `LogLevel VERBOSE` (sebelumnya INFO) buat forensik brute-force | Selesai | `evidence/sshd-before.log`, `evidence/sshd-after.log` |
| C2 | journald `Storage=persistent` (log selamat dari reboot) | Selesai | `evidence/journal-after.log` |
| C3 | Banner peringatan di `/etc/issue.net` + `Banner` sshd | Selesai | `evidence/sshd-after.log`, isi file di bawah |

Isi banner: "Authorized access only - KEL12 SOC. Disconnect immediately if you
are not an authorized user. All activity is logged and monitored."

## Temuan penting saat pengerjaan

Aturan iptables yang didokumentasikan Fase 1 ternyata hilang dari memori
(`iptables -L` kosong, policy ACCEPT). Kemungkinan rules tidak di-restore
setelah reboot. Makanya B1 kali ini disimpan ke `/etc/iptables/iptables.rules`
dan service-nya di-enable. Buktinya ada di `iptables-before.log`. Pelajaran
paling mahal dari pengerjaan ini adalah aturan firewall yang tidak disimpan
ulang setelah reboot akan lenyap begitu saja sehingga target sempat telanjang
tanpa perlindungan sama sekali dan tidak ada yang sadar sampai dicek langsung.

## Keterbatasan yang dicatat (bukan disembunyikan)

- `pacman -Syu` tidak jalan (segmen isolasi tanpa internet, log terakhir 2021).
  Patch manual menunggu akses internet. Fail2ban dan Mosquitto juga belum
  terinstal karena alasan yang sama; brute-force ditahan MaxAuthTries +
  faillock bawaan,   MQTT menyusul Fase 2.

Kami tulis apa adanya.
