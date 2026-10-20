#!/usr/bin/env python3
"""mqtt_pub.py - klien MQTT minimal untuk skenario red team Target Node.

Penggunaan:
  python3 mqtt_pub.py --host 192.168.12.5 --topic cow-sprinkler-01/control --message '{"mode":"manual"}'
  python3 mqtt_pub.py --host ... --user esp32 --password ... --topic ...

Keluar dengan kode 0 kalau PUBLISH diterima broker, selain itu non-zero.
"""
import argparse
import socket
import struct
import sys
import time


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


def read_remaining_length(conn):
    length = 0
    multiplier = 1
    while True:
        byte = read_exact(conn, 1)[0]
        length += (byte & 127) * multiplier
        if not byte & 0x80:
            return length
        multiplier *= 128


def encode_string(text):
    raw = text.encode("utf-8")
    return struct.pack("!H", len(raw)) + raw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--message", default="{}")
    parser.add_argument("--user", default="")
    parser.add_argument("--password", default="")
    parser.add_argument("--client-id", default="attacker-kel12")
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    conn = socket.create_connection((args.host, args.port), timeout=args.timeout)
    conn.settimeout(args.timeout)

    flags = 0x02
    payload = encode_string("MQTT") + bytes([4, flags]) + struct.pack("!H", 60)
    payload += encode_string(args.client_id)
    if args.user:
        flags |= 0x80
        payload += encode_string(args.user)
    if args.password:
        flags |= 0x40
        payload += encode_string(args.password)
    payload = encode_string("MQTT") + bytes([4, flags]) + struct.pack("!H", 60) + payload[len(encode_string("MQTT")) + 4:]
    conn.sendall(bytes([0x10]) + encode_remaining(len(payload)) + payload)

    head = read_exact(conn, 1)[0]
    if head >> 4 != 2:
        print("GAGAL: broker tidak mengirim CONNACK", file=sys.stderr)
        return 2
    length = read_remaining_length(conn)
    body = read_exact(conn, length)
    code = body[1]
    if code != 0:
        print("GAGAL: CONNACK return code %d (0x05 = tidak diizinkan)" % code)
        return 3
    print("CONNACK: diterima (rc=0)")

    topic = args.topic.encode("utf-8")
    body = struct.pack("!H", len(topic)) + topic + args.message.encode("utf-8")
    conn.sendall(bytes([0x30]) + encode_remaining(len(body)) + body)
    print("PUBLISH dikirim ke %s (payload %d byte)" % (args.topic, len(args.message)))

    conn.settimeout(1.0)
    try:
        peek = conn.recv(1)
        if peek:
            print("GAGAL: broker menutup koneksi setelah publish (tolak topik / AUTH_DENIED)")
            return 4
    except socket.timeout:
        pass
    conn.close()
    print("PUBLISH diterima broker (koneksi tetap hidup)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
