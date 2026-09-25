# Fase 2 — Vulnerability Assessment (Rencana, Minggu 9-11, BELUM dieksekusi)

> Jangan serang sebelum Fase 1 lulus + dosen memberi lampu hijau. Semua hanya ke `192.168.12.5`.

## Rencana Red Team (Fachri)
1. **Scanning:** `nmap -sV -p 22,80,1883 192.168.12.5` → catat versi OpenSSH, Flask, Mosquitto.
2. **MQTT:** coba anon publish `mosquitto_pub -h 192.168.12.5 -t greenhouse/pompa/cmd -m "ON"` (harus GAGAL), coba replay dengan kredensial curian simulasi, catat di log.
3. **Web:** `curl http://192.168.12.5/`, coba `?file=../../etc/passwd`, brute login dashboard dengan wordlist kecil (throttle, jangan DoS).
4. **SSH:** `hydra -l iotadmin -P /usr/share/wordlists/rockyou.txt -t 2 ssh://192.168.12.5` (terbatas, stop jika lockout).
5. **Bukti:** simpan output `.txt` + screenshot + pcap Onion di folder ini (`nmap.txt`, `mqtt-anon-fail.txt`, `web-traversal.png`).

Output akhir nanti: `VA-Report.md` berisi daftar CVE/service lemah + bukti log serangan berhasil/gagal.
