# 2BRAIN landing page

Static Russian-language landing page for 2BRAIN. The site is served by Nginx in a read-only Docker container and published through the host Nginx reverse proxy.

## Local run

```bash
docker compose up -d
curl -fsS http://127.0.0.1:8460/healthz
```

The local site is available at `http://127.0.0.1:8460/`.

## Production topology

```text
Internet → host Nginx + TLS → 127.0.0.1:8460 → Docker Compose → Nginx → site/
```

Host TLS and Certbot configuration are kept in `host-nginx/` and `deploy/`. A release updates the application container and does not change the public Nginx or certificate configuration.

## SEO work

The non-visual SEO plan and acceptance criteria are documented in [`docs/SEO-PLAN.md`](docs/SEO-PLAN.md). The current audit artifacts are intentionally kept outside Git under `output/`; regenerate them when needed.

## Deployment safety

- The container is read-only and runs without privilege escalation.
- The Nginx image is pinned by digest.
- Changes to the public host Nginx configuration require an explicit, separate operation.
- Releases must pass HTML/SEO checks and a container health check before being considered successful.
