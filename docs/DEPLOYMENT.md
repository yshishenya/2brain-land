# Deployment

## Release trigger

Production deployment is intentionally tag-based. Create and push a CalVer tag:

```bash
git tag v2026.08.20.1
git push origin v2026.08.20.1
```

The release workflow validates the site, uploads `site/`, `nginx/`, and `docker-compose.yml` to a release directory, recreates the pinned Nginx container, checks `/healthz`, checks `https://2brain.pro/`, and then marks the release as current.

## GitHub Actions secrets

The `production` environment requires:

- `DEPLOY_HOST` — production SSH host;
- `DEPLOY_USER` — deployment user;
- `DEPLOY_SSH_KEY` — private key for the dedicated GitHub Actions deploy key;
- `DEPLOY_KNOWN_HOSTS` — pinned SSH host key lines from `ssh-keyscan`.

Secrets are configured in GitHub and are never committed to this repository.

## Rollback

Re-run Compose against a previous directory on the production host:

```bash
docker compose -f /opt/projects/2br_land/releases/<commit-sha>/docker-compose.yml up -d --force-recreate
```

The host Nginx and Certbot configuration are outside the release bundle and are not modified by the release workflow.
