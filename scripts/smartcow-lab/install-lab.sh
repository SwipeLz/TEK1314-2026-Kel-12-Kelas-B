#!/bin/bash
# Pasang replika backend SmartCow di Target Node.
# Dijalankan sebagai root lewat sudo. Keadaan awal dibiarkan longgar supaya
# bukti before/after tiap kontrol bisa direkam.
LAB=/home/smartcow-lab
SRC=/home/sec_admin/lab-files

echo "== buat akun aplikasi =="
id -u smartcow >/dev/null 2>&1 || useradd -r -m -d $LAB -s /usr/bin/nologin smartcow

echo "== pasang berkas =="
mkdir -p $LAB/data $LAB/logs $LAB/secrets
cp $SRC/app.py $SRC/broker.py $SRC/simulator.py $SRC/mqtt_pub.py $LAB/
cp $SRC/app.env $LAB/.env
cp $SRC/mqtt.env $LAB/mqtt.env
cp $SRC/mqtt_users.json $LAB/secrets/mqtt_users.json
chown -R smartcow:smartcow $LAB
chmod 750 $LAB $LAB/data $LAB/logs $LAB/secrets
chmod 640 $LAB/app.py $LAB/broker.py $LAB/simulator.py $LAB/mqtt_pub.py
# Keadaan awal: berkas kredensial masih bisa dibaca user lain
chmod 644 $LAB/.env $LAB/mqtt.env $LAB/secrets/mqtt_users.json

echo "== unit systemd =="
cp $SRC/smartcow-api.service $SRC/smartcow-broker.service $SRC/smartcow-sim.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now smartcow-api.service
systemctl enable --now smartcow-broker.service
systemctl enable --now smartcow-sim.service

echo "== nginx sebagai pintu masuk =="
rm -f /etc/nginx/conf.d/default.conf
cp $SRC/nginx-smartcow.conf /etc/nginx/conf.d/smartcow.conf
systemctl enable --now nginx
nginx -t

sleep 3
echo "== STATUS LAYER =="
systemctl is-active smartcow-api smartcow-broker smartcow-sim nginx
echo "== LISTENER =="
ss -lntp | grep -E ':80 |:9000|:1883'
echo "== PERMISSION KREDENSIAL (sebelum hardening) =="
ls -l $LAB/.env $LAB/mqtt.env $LAB/secrets/mqtt_users.json
echo "== HEALTH CHECK =="
curl -s -m 5 http://127.0.0.1:9000/health
echo
curl -s -m 5 -o /dev/null -w "dashboard nginx http=%{http_code}\n" http://127.0.0.1/
