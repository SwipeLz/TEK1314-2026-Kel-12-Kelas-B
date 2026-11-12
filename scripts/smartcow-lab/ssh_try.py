#!/usr/bin/env python3
"""ssh_try.py - percobaan login SSH dengan kredensial yang diuji.

Nmap NSE ssh-brute butuh sshpass yang tidak tersedia di lab offline, jadi
klien ini memakai pty untuk memberi password ke OpenSSH client.
Keluar dengan kode 0 kalau login berhasil.
"""
import os
import pty
import select
import sys
import time


def try_login(host, user, password, timeout=12):
    args = [
        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
        "-o", "PreferredAuthentications=password,keyboard-interactive",
        "-o", "PubkeyAuthentication=no", "-o", "NumberOfPasswordPrompts=1",
        "-o", "ConnectTimeout=5", "-o", "LogLevel=ERROR",
        "%s@%s" % (user, host), "echo LOGIN_BERHASIL",
    ]
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp("ssh", args)
        os._exit(127)

    output = b""
    sent = False
    deadline = time.time() + timeout
    while time.time() < deadline:
        ready, _, _ = select.select([fd], [], [], 0.3)
        if fd in ready:
            try:
                chunk = os.read(fd, 4096)
            except OSError:
                break
            if not chunk:
                break
            output += chunk
            if not sent and b"assword" in output:
                os.write(fd, password.encode("utf-8") + b"\n")
                sent = True
        elif sent:
            break
    try:
        os.kill(pid, 9)
        os.waitpid(pid, 0)
    except (OSError, ChildProcessError):
        pass
    try:
        os.close(fd)
    except OSError:
        pass

    text = output.decode("utf-8", "replace")
    if "LOGIN_BERHASIL" in text:
        return "BERHASIL", text
    if "Permission denied" in text:
        return "DITOLAK", text
    if "Connection refused" in text or "timed out" in text or "reset" in text:
        return "TERPUTUS", text
    return "GAGAL", text


def main():
    host = sys.argv[1]
    for combo in sys.argv[2:]:
        user, password = combo.split(":", 1)
        status, text = try_login(host, user, password)
        print("user=%-10s password=%-14s -> %s" % (user, password, status))
        lines = [line for line in text.strip().splitlines() if line.strip()]
        for line in lines[-2:]:
            print("    " + line.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
