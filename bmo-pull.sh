#!/usr/bin/env bash
set -u
SERVER_BASE="https://suchana.space"
API_TOKEN="CHANGE_THIS_TO_THE_SAME_LONG_RANDOM_SECRET"
DEST_DIR="/home/bmo_received"
mkdir -p "$DEST_DIR" && chmod 700 "$DEST_DIR"
for cmd in curl python3 file; do command -v "$cmd" >/dev/null || { echo "Missing $cmd"; exit 1; }; done
while true; do
 response="$(curl -sS --fail --connect-timeout 10 --max-time 25 -H "X-BMO-Token: ${API_TOKEN}" "${SERVER_BASE}/api/next.php" 2>/dev/null || true)"
 name="$(python3 -c 'import json,sys;d=json.load(sys.stdin);print((d.get("item") or {}).get("filename",""))' <<<"$response" 2>/dev/null || true)"
 url="$(python3 -c 'import json,sys;d=json.load(sys.stdin);print((d.get("item") or {}).get("url",""))' <<<"$response" 2>/dev/null || true)"
 if [[ -z "$name" || -z "$url" ]]; then sleep 4; continue; fi
 if [[ ! "$name" =~ ^[a-f0-9]{32}\.(jpg|png|webp|gif)$ ]]; then echo "Rejected filename: $name" >&2; sleep 5; continue; fi
 tmp="$DEST_DIR/$name.part"; dest="$DEST_DIR/$name"
 echo "Downloading $name"
 if curl -sS --fail --location --connect-timeout 10 --max-time 120 "$url" -o "$tmp" && file --brief "$tmp" | grep -Eqi 'JPEG image data|PNG image data|Web/P image|GIF image data'; then
   mv "$tmp" "$dest"; chmod 600 "$dest"; echo "Saved: $dest"
 else rm -f "$tmp"; echo "Download failed or file is not an image: $name" >&2; fi
 sleep 3
done
