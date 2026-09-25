#!/bin/bash
# hardening-iot-server.sh — Jalankan di SRV-IOT-KEL12-G (192.168.12.5, Ubuntu Server) sebagai user dengan sudo
# Tujuan Fase 1: Before Attack baseline. Idempoten (aman dijalankan ulang).
set -e
echo "[1/6] Update patch..."
sudo apt update && sudo apt upgrade -y

echo "[2/6] Buat user non-root iotadmin (skip jika sudah ada)..."
if ! id iotadmin >/dev/null 2>&1; then sudo adduser --disabled-password --gecos "" iotadmin; sudo usermod -aG sudo iotadmin; fi
echo "-> pastikan login SSH pakai iotadmin, bukan root."

echo "[3/6] Harden SSH..."
sudo sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
# Fase 3 nanti ganti ke 'no' + key-only. Sekarang tetap yes agar demo tidak lockout.
sudo systemctl restart ssh || sudo systemctl restart sshd || true

echo "[4/6] Install + config UFW (default deny, allow 22/80/1883)..."
sudo apt install -y ufw mosquitto mosquitto-clients
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.12.0/24 to any port 22 proto tcp comment 'SSH mgmt KEL12'
sudo ufw allow 80/tcp comment 'Web dashboard greenhouse'
sudo ufw allow 1883/tcp comment 'MQTT broker'
sudo ufw --force enable
sudo ufw status verbose

echo "[5/6] Harden Mosquitto (matikan anonymous)..."
sudo mosquitto_passwd -c -b /etc/mosquitto/passwd sensor1 'GantiPasswordKuat123!' || true
sudo mosquitto_passwd -b /etc/mosquitto/passwd dashboard 'GantiPasswordKuat123!' || true
sudo bash -c 'cat > /etc/mosquitto/conf.d/kel12.conf <<EOF
allow_anonymous false
password_file /etc/mosquitto/passwd
listener 1883 192.168.12.5
acl_file /etc/mosquitto/acl
EOF
cat > /etc/mosquitto/acl <<EOF
user sensor1
topic readwrite greenhouse/#
user dashboard
topic read greenhouse/#
topic write greenhouse/pompa/cmd
EOF'
sudo systemctl enable mosquitto --now
sudo systemctl restart mosquitto
echo "-> uji anon harus GAGAL:"
mosquitto_pub -h 192.168.12.5 -t greenhouse/suhu -m test && echo "WARNING: anon masih bisa!" || echo "OK: anon ditolak."

echo "[6/6] Matikan service tak perlu + cek akhir..."
sudo systemctl disable --now cups avahi-daemon telnet.socket 2>/dev/null || true
echo "--- ss -tulpn (harusnya hanya 22/80/1883) ---"
ss -tulpn || netstat -tulpn || true
echo "--- ufw rules ---"
cat /etc/ufw/user.rules || true
echo "SELESAI. Screenshot output di atas untuk assets/04 + 05."
