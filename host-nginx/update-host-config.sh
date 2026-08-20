#!/usr/bin/env bash
set -Eeuo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Запустите скрипт через sudo." >&2
  exit 1
fi

project_dir="/opt/projects/2br_land"
source_config="${project_dir}/host-nginx/2brain.pro-https.conf"
active_config="/etc/nginx/sites-available/2brain.pro.conf"
backup="${project_dir}/backups/2brain.pro.conf.$(date +%Y%m%d-%H%M%S)"

test -f "${source_config}"
test -f "${active_config}"
grep -qF "Managed by /opt/projects/2br_land/install-host.sh" "${active_config}"

cp -a "${active_config}" "${backup}"

rollback() {
  set +e
  cp -a "${backup}" "${active_config}"
  nginx -t && systemctl reload nginx
}

trap rollback ERR
install -m 0644 "${source_config}" "${active_config}"
nginx -t
systemctl reload nginx
nginx -t
trap - ERR

