#!/usr/bin/env bash
set -Eeuo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Запустите скрипт через sudo." >&2
  exit 1
fi

project_dir="/opt/projects/2br_land"
available="/etc/nginx/sites-available/2brain.pro.conf"
enabled="/etc/nginx/sites-enabled/2brain.pro.conf"
http_source="${project_dir}/host-nginx/2brain.pro-http.conf"
https_source="${project_dir}/host-nginx/2brain.pro-https.conf"
backup_dir="${project_dir}/backups/host-$(date +%Y%m%d-%H%M%S)"

test -f "${http_source}"
test -f "${https_source}"
test -d /var/www/certbot

if [[ -e "${available}" ]] && ! grep -qF "Managed by /opt/projects/2br_land/install-host.sh" "${available}"; then
  echo "Обнаружена посторонняя конфигурация ${available}; установка остановлена." >&2
  exit 2
fi

if [[ -e "${enabled}" ]] && [[ "$(readlink -f "${enabled}")" != "${available}" ]]; then
  echo "Обнаружена посторонняя конфигурация ${enabled}; установка остановлена." >&2
  exit 3
fi

install -d -m 0750 "${backup_dir}"
had_available=0
had_enabled=0
enabled_target=""

if [[ -e "${available}" ]]; then
  cp -a "${available}" "${backup_dir}/2brain.pro.conf"
  had_available=1
fi

if [[ -e "${enabled}" ]]; then
  enabled_target="$(readlink "${enabled}")"
  had_enabled=1
fi

rollback() {
  set +e
  if [[ ${had_available} -eq 1 ]]; then
    cp -a "${backup_dir}/2brain.pro.conf" "${available}"
  else
    rm -f "${available}"
  fi

  if [[ ${had_enabled} -eq 1 ]]; then
    ln -sfn "${enabled_target}" "${enabled}"
  else
    rm -f "${enabled}"
  fi

  nginx -t && systemctl reload nginx
}

trap rollback ERR

install -m 0644 "${http_source}" "${available}"
ln -sfn "${available}" "${enabled}"
nginx -t
systemctl reload nginx

certbot certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  --cert-name 2brain.pro \
  --domain 2brain.pro \
  --domain www.2brain.pro \
  --non-interactive \
  --agree-tos \
  --keep-until-expiring \
  --deploy-hook "systemctl reload nginx"

test -s /etc/letsencrypt/live/2brain.pro/fullchain.pem
test -s /etc/letsencrypt/live/2brain.pro/privkey.pem

install -m 0644 "${https_source}" "${available}"
nginx -t
systemctl reload nginx
nginx -t

trap - ERR
certbot certificates --cert-name 2brain.pro
