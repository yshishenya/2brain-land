#!/usr/bin/env bash
set -euo pipefail

SOURCE_HOOK="${1:-/opt/projects/2br_land/deploy/certbot-hooks/20-reload-nginx.sh}"
TARGET_DIR="/etc/letsencrypt/renewal-hooks/deploy"
TARGET_HOOK="$TARGET_DIR/20-reload-nginx.sh"

test -f "$SOURCE_HOOK"
/bin/sh -n "$SOURCE_HOOK"
/usr/sbin/nginx -t

install -d -m 755 "$TARGET_DIR"
if [ -e "$TARGET_HOOK" ]; then
  backup_suffix="$(date -u +%Y%m%dT%H%M%SZ)"
  cp -a "$TARGET_HOOK" "$TARGET_HOOK.bak.$backup_suffix"
fi
install -o root -g root -m 755 "$SOURCE_HOOK" "$TARGET_HOOK"

systemctl enable --now certbot.timer
/bin/sh "$TARGET_HOOK"

echo 'Installed global Certbot deploy hook:'
ls -l "$TARGET_HOOK"
echo 'Certbot timer state:'
systemctl is-enabled certbot.timer
systemctl is-active certbot.timer
systemctl list-timers certbot.timer --all --no-pager
