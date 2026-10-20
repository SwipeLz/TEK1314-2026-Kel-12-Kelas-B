#!/usr/bin/env python3
"""smartcow-lab - broker MQTT minimal untuk Target Node PBL TEK1314 Kelompok 12.

Hanya poles protokol yang dipakai skenario: CONNECT (dengan username/password),
SUBSCRIBE, PUBLISH, PINGREQ. Antrean pesan per subscriber.

Sebelum hardening: koneksi anonim diterima dan semua topic boleh ditulis.
Sesudah hardening: kredensial wajib dan ACL topic membatasi penulisan.
"""
import json
import os
import socket
import struct
import threading

BIND = os.environ.get("SMARTCOW_MQTT_BIND", "0.0.0.0")
PORT = int(os.environ.get("SMARTCOW_MQTT_PORT", "1883"))
REQUIRE_AUTH = os.environ.get("SMARTCOW_MQTT_AUTH", "0") == "1"
ENFORCE_ACL = os.environ.get("SMARTCOW_MQTT_ACL", "0") == "1"
CRED_FILE = os.environ.get("SMARTCOW_MQTT_CRED", "/home/smartcow-lab/secrets/mqtt_users.json")
LOG_PATH = os.environ.get("SMARTCOW_MQTT_LOG", "")
READ_TOPICS = ("cow-sprinkler-01/control", "cow-sprinkler-01/status", "cow-sprinkler-01/telemetry/latest")
WRITE_TOPICS = ("cow-sprinkler-01/telemetry/latest",)

_clients = []
_lock = threading.Lock()


def log_event(kind, detail):
    if not LOG_PATH:
        return
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write("%s %s %s\n" % (time_now(), kind, detail))
    except OSError:
        pass


def time_now():
    from datetime import datetime, timedelta, timezone
    return (datetime.now(timezone.utc) + timedelta(hours=7)).strftime("%Y-%m-%dT%H:%M:%S+07:00")


def read_credentials():
    try:
        with open(CRED_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def topic_allowed(topic, write):
    if not ENFORCE_ACL:
        return True
    if write:
        return topic in WRITE_TOPICS
    return topic in READ_TOPICS


def encode_remaining(length):
    out = b""
    while True:
        byte = length % 128
        length //= 128
        if length > 0:
            byte |= 0x80
        out += bytes([byte])
        if length == 0:
            break
    return out


def read_exact(conn, count):
    buf = b""
    while len(buf) < count:
        chunk = conn.recv(count - len(buf))
        if not chunk:
            raise ConnectionError("peer menutup koneksi")
        buf += chunk
    return buf


def read_string(data, offset):
    (length,) = struct.unpack_from("!H", data, offset)
    offset += 2
    value = data[offset:offset + length].decode("utf-8", "replace")
    return value, offset + length


def send_publish(conn, topic, payload):
    body = struct.pack("!H", len(topic)) + topic.encode("utf-8") + payload
    conn.sendall(bytes([0x30]) + encode_remaining(len(body)) + body)


def handle_client(conn, addr):
    peer = "%s:%d" % addr
    client = {"conn": conn, "subs": set(), "id": "anon"}
    try:
        header = read_exact(conn, 1)
        if header[0] != 0x10:
            return
        length = 0
        multiplier = 1
        while True:
            byte = read_exact(conn, 1)[0]
            length += (byte & 127) * multiplier
            if not byte & 0x80:
                break
            multiplier *= 128
        body = read_exact(conn, length)
        offset = 0
        name, offset = read_string(body, offset)
        level = body[offset]
        offset += 1
        flags = body[offset]
        offset += 1
        offset += 2  # keepalive
        client_id, offset = read_string(body, offset)
        client["id"] = client_id or "anon"
        if flags & 0x04:
            _, offset = read_string(body, offset)  # will topic
            _, offset = read_string(body, offset)  # will payload
        username = password = None
        if flags & 0x80:
            username, offset = read_string(body, offset)
        if flags & 0x40:
            password, offset = read_string(body, offset)

        granted = 0
        if REQUIRE_AUTH:
            creds = read_credentials()
            if username and creds.get(username) == password:
                granted = 1
            else:
                log_event("denied", "kredensial MQTT salah dari %s user=%s" % (peer, username))
                conn.sendall(bytes([0x20, 0x02, 0x00, 0x05]))
                return
        else:
            log_event("connect", "MQTT anonim diterima dari %s id=%s" % (peer, client["id"]))
        conn.sendall(bytes([0x20, 0x02, 0x00, granted]))

        with _lock:
            _clients.append(client)

        while True:
            first = read_exact(conn, 1)[0]
            kind = first >> 4
            length = 0
            multiplier = 1
            while True:
                byte = read_exact(conn, 1)[0]
                length += (byte & 127) * multiplier
                if not byte & 0x80:
                    break
                multiplier *= 128
            payload = read_exact(conn, length) if length else b""
            if kind == 12:  # PINGREQ
                conn.sendall(bytes([0xD0, 0x00]))
            elif kind == 10:  # SUBSCRIBE
                packet_id = struct.unpack_from("!H", payload, 0)[0]
                offset = 2
                granted = b""
                while offset < len(payload):
                    topic, offset = read_string(payload, offset)
                    qos = payload[offset]
                    offset += 1
                    client["subs"].add(topic)
                    granted += bytes([qos])
                body = struct.pack("!H", packet_id) + granted
                conn.sendall(bytes([0x90]) + encode_remaining(len(body)) + body)
                log_event("subscribe", "id=%s topik=%s" % (client["id"], topic))
            elif kind == 3:  # PUBLISH
                qos = (first >> 1) & 0x03
                topic, offset = read_string(payload, 0)
                if qos > 0:
                    offset += 2
                data = payload[offset:]
                if not topic_allowed(topic, write=True):
                    log_event("denied", "publish ke topik terlarang dari %s id=%s topik=%s" % (peer, client["id"], topic))
                    conn.close()
                    return
                log_event("publish", "id=%s topik=%s ukuran=%dB" % (client["id"], topic, len(data)))
                with _lock:
                    targets = [c for c in _clients if topic in c["subs"] and c is not client]
                for target in targets:
                    try:
                        send_publish(target["conn"], topic, data)
                    except OSError:
                        pass
            elif kind == 8:  # CONNECT ulang
                continue
            elif kind == 14:  # DISCONNECT
                break
    except (ConnectionError, OSError, struct.error, IndexError):
        pass
    finally:
        with _lock:
            if client in _clients:
                _clients.remove(client)
        try:
            conn.close()
        except OSError:
            pass


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((BIND, PORT))
    server.listen(16)
    log_event("start", "broker MQTT bind=%s port=%d auth=%s acl=%s" % (BIND, PORT, REQUIRE_AUTH, ENFORCE_ACL))
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()


if __name__ == "__main__":
    main()
