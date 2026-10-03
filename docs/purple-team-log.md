# Purple team log — Kelompok 12 Kelas B

Tiap skenario attack plan wajib lewat 5 tahap. Aturan main: yang tercatat
berhasil di tahap 1 harus berakhir gagal di tahap 5. Diisi bertahap Minggu
10–11.

Status per 3 Okt 2026: skenario 1 tahap 1 sebagian jalan (scan nmap sudah
dieksekusi, bukti di `docs/redteam/evidence/`). Tahap lainnya belum mulai.

## Skenario 1 — Recon nmap ke 192.168.12.5

| Tahap | Red team | Blue team | Bukti |
| :--- | :--- | :--- | :--- |
| 1. Serang | Scan `-sS -sV -O` ke target | Amati Sguil | `docs/redteam/evidence/nmap-target-after.log` |
| 2. Deteksi | — | Identifikasi alert (atau catat bila tidak muncul) | Screenshot Sguil / grep log |
| 3. Analisis | Jelaskan teknik scan | Root cause: kenapa lolos/terdeteksi, kontrol apa yang kurang | Catatan di Incident Report |
| 4. Respons | — | Kontrol tambahan (alert rule / firewall) | Diff config |
| 5. Verifikasi | Ulangi scan yang sama | Konfirmasi hasil + alert | Screenshot scan ulang |

## Skenario 2 — Brute-force SSH port 22

| Tahap | Red team | Blue team | Bukti |
| :--- | :--- | :--- | :--- |
| 1. Serang | Tebak password beruntun (wordlist kecil) | Amati Sguil + journal target | Log Hydra/NSE + screenshot |
| 2. Deteksi | — | Alert `ET SCAN Potential SSH Scan`, auth failure di journal (VERBOSE) | Screenshot/grep |
| 3. Analisis | Teknik brute-force | Root cause + evaluasi MaxAuthTries/faillock | Catatan analisis |
| 4. Respons | — | Kuatkan bila perlu (deny lebih ketat / AllowUsers sudah ada) | Diff config |
| 5. Verifikasi | Ulangi serangan sama | Akun terkunci / serangan gagal tercatat | Screenshot + reset lock (`faillock --user sec_admin --reset`) |

## Skenario 3 — MQTT replay / publish palsu

| Tahap | Red team | Blue team | Bukti |
| :--- | :--- | :--- | :--- |
| 1. Serang | Publish perintah palsu ke broker replika | Amati capture Onion + log broker | pcap + log |
| 2. Deteksi | — | Koneksi 1883 + pola publish berulang | Screenshot/grep |
| 3. Analisis | Teknik replay | Root cause (auth/ACL topic) | Catatan analisis |
| 4. Respons | — | Auth + ACL topic (+TLS bila sempat) | Diff config broker |
| 5. Verifikasi | Ulangi publish palsu | Publish ditolak + tercatat | Screenshot + log |

Catatan: broker MQTT dan service replika dibangun Fase 2 (butuh install saat
ada internet). Loop skenario 3 jalan setelah itu.
