#!/bin/sh
# C3 restore verification: extract newest archive to a temp dir and verify every
# file against the manifest written at backup time. Prints PASS/FAIL lines only.
set -eu
DEST=/home/smartcow-lab/backup
TMP=$(mktemp -d /tmp/restore-check.XXXXXX)
trap 'rm -rf "$TMP"' EXIT INT TERM

arch=$(ls -1t "$DEST"/state-*.tar.gz | head -1)
echo "archive=$(basename "$arch")"

# Integrity of the archive itself.
if [ -f "$arch.sha256" ] && (cd "$DEST" && sha256sum -c "$(basename "$arch").sha256" >/dev/null 2>&1); then
    echo "PASS archive-checksum"
else
    echo "FAIL archive-checksum"
fi

# Restore into an isolated directory and verify every file against the
# manifest captured at backup time.
tar -xzf "$arch" -C "$TMP"
if (cd "$TMP" && sha256sum -c "$arch.sha256sums" >/dev/null 2>&1); then
    echo "PASS restore-content-matches-manifest files=$(find "$TMP/data" -type f | wc -l)"
else
    echo "FAIL restore-content-matches-manifest"
    (cd "$TMP" && sha256sum -c "$arch.sha256sums" 2>&1 | grep -v ': OK$' | head -5)
fi

count=$(find "$TMP/data" -type f | wc -l)
echo "SUMMARY restored_files=$count"
