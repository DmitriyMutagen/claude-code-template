# VPS Deploy & CI/CD — Global Rules (ALL Projects)

## Production Server
- **IP**: 94.198.219.232
- **SSH**: `ssh root@94.198.219.232` (key auth, ~/.ssh/id_ed25519)
- **Root pass**: xRbq2*djGbM_zV (backup, use key)
- **OS**: Ubuntu 24.04 LTS
- **Specs**: 4 CPU / 8GB RAM / 80GB NVMe (preset 2455)
- **Location**: SPB, Russia (ru-1, TimeWeb Cloud)
- **TimeWeb ID**: 6695469 (Polite Hoopoe)

## VPN Server (Germany)
- **IP**: 72.56.121.84
- **Location**: Frankfurt, DE (de-1, TimeWeb Cloud)
- **Purpose**: Amnezia VPN only
- **TimeWeb ID**: 6695569 (Wise Corvus)

## TimeWeb API
- **Token**: stored in chat/Credentials.env (JWT, starts with eyJhbGci...)
- **Account**: gy040287
- **Base URL**: https://api.timeweb.cloud/api/v1
- **Auth**: `Authorization: Bearer $TW_TOKEN`

## Deploy Flow (ALL Projects)
```
Developer → git push → GitHub → CI/CD (GitHub Actions) → SSH to VPS → docker compose up
```

### Step-by-step for NEW project deploy:
1. **Create directory**: `ssh root@94.198.219.232 "mkdir -p /opt/{project}"`
2. **Upload code**: `rsync -az --exclude .git --exclude node_modules --exclude __pycache__ --exclude .env -e ssh ./ root@94.198.219.232:/opt/{project}/`
3. **Fix permissions**: `ssh root@94.198.219.232 "chmod -R 755 /opt/{project}/src/"`
4. **Docker build**: `ssh root@94.198.219.232 "cd /opt/{project} && docker compose build && docker compose up -d"`
5. **Health check**: `ssh root@94.198.219.232 "curl -s http://localhost:{PORT}/health"`

### Nginx config for new domain:
```bash
ssh root@94.198.219.232 'cat > /etc/nginx/sites-available/{project} << EOF
server {
    listen 80;
    server_name {domain};
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 301 https://\$host\$request_uri; }
}
server {
    listen 443 ssl http2;
    server_name {domain};
    ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;
    location / { proxy_pass http://127.0.0.1:{PORT}; proxy_set_header Host \$host; proxy_set_header X-Real-IP \$remote_addr; proxy_set_header X-Forwarded-Proto \$scheme; }
}
EOF
ln -sf /etc/nginx/sites-available/{project} /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx'
```

### SSL:
```bash
ssh root@94.198.219.232 "certbot certonly --webroot -w /var/www/certbot -d {domain} --non-interactive --agree-tos --email gagauzdmitriy@gmail.com"
```

### DNS (reg.ru):
- A record `@` → 94.198.219.232
- A record `www` → 94.198.219.232

## GitHub Actions Template (.github/workflows/deploy.yml)
```yaml
name: Deploy
on:
  push:
    branches: [main, release/*]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: appleboy/ssh-action@v1
        with:
          host: 94.198.219.232
          username: root
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/{project}
            git pull origin {branch}
            chmod -R 755 src/ 2>/dev/null || true
            docker compose build
            docker compose up -d
            sleep 10
            curl -sf http://localhost:{PORT}/health || exit 1
```
**GitHub Secret `SSH_PRIVATE_KEY`**: contents of `~/.ssh/id_ed25519`

## Installed on Server
- Docker 29.3.1 + Compose
- Nginx 1.24 + Certbot (auto-renew)
- UFW (22, 80, 443, 5678, 8000, 8001, 8002, 3001)
- fail2ban (SSH protection)
- SSH watchdog (auto-restart every 5 min)
- QEMU guest agent (TimeWeb API control)
- Swap 4GB

## Active Projects on Server
| Project | Port | Domain | Path |
|---------|------|--------|------|
| Aragant | 8000 | aragant.pro | /opt/aragant |
| Bionovacia | 8002 | bionovacia.ru | /opt/bionovacia |

## Known Issues & Fixes
- **OOM during docker build**: increase swap, stop unused containers during build
- **SSH banner timeout**: `UseDNS no` in sshd_config (ALREADY SET)
- **rsync breaks permissions**: always run `chmod -R 755 src/` after rsync
- **Argon2 not bcrypt**: auth.py uses argon2 for passwords, NOT bcrypt
- **bcrypt 4.0.1**: pinned in requirements.txt for passlib compatibility
