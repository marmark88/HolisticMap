# Deploy Holistic Map: Supabase (Postgres) + Linux VM

The app connects to Postgres over the network. Django runs behind **Gunicorn**; **nginx** serves HTTPS and proxies to Gunicorn. Static files come from **`collectstatic`** (WhiteNoise is also enabled as a fallback).

Paths below assume code lives at **`/srv/holisticmap`** with a venv at **`/srv/holisticmap/venv`**.

---

## Part 1 — Supabase (database only)

1. Create a project at [supabase.com](https://supabase.com): choose region, set the database password, wait until healthy.
2. Open **Project Settings → Database**.
3. Copy the **PostgreSQL URI** (“direct” connection, port **5432**).  
   - Append `?sslmode=require` if it is missing.  
   - URL-encode special characters in the password if needed.
4. **Session mode pooling** (`6543`): optional if you tune many Gunicorn workers; start with **direct** for fewer surprises with migrations.

You do **not** create Django tables manually. `python manage.py migrate` creates them.

---

## Part 2 — Google Compute Engine VM (Ubuntu 22.04 LTS suggested)

### Firewall / VPC

Allow inbound **SSH (22)**, **HTTP (80)**, **HTTPS (443)** to the VM. Restrict SSH source IP if possible.

Reserve a **static external IP**. Point your DNS **A** record at that IP.

### Install system packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx git certbot python3-certbot-nginx
```

### App user and directories

```bash
sudo mkdir -p /srv/holisticmap
sudo chown www-data:www-data /srv/holisticmap
```

Deploy code into `/srv/holisticmap` (repo root contains `manage.py` and `config/`):

```bash
cd /srv/holisticmap
sudo -u www-data git clone https://github.com/YOU/HolisticMap.git .
sudo -u www-data python3 -m venv venv
sudo -u www-data ./venv/bin/pip install --upgrade pip
sudo -u www-data ./venv/bin/pip install -r requirements.txt
```

### Environment file

```bash
sudo cp deploy/env.example /etc/holisticmap.env
sudo chmod 640 /etc/holisticmap.env
sudo chown root:www-data /etc/holisticmap.env
sudo nano /etc/holisticmap.env
```

Fill in **`SECRET_KEY`**, **`DATABASE_URL`** (Supabase), **`DJANGO_ALLOWED_HOSTS`**, **`DJANGO_CSRF_TRUSTED_ORIGINS`** (`https://...` after TLS), and **`DJANGO_USE_X_FORWARDED_PROTO=1`**.

Generate a secret key locally:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Local dev keeps using **SQLite** when **`DATABASE_URL` is unset**. On the VM **`DATABASE_URL` must be set**.

### Migrate and collect static

```bash
cd /srv/holisticmap
sudo -u www-data env $(grep -v '^#' /etc/holisticmap.env | xargs) ./venv/bin/python manage.py migrate
sudo -u www-data env $(grep -v '^#' /etc/holisticmap.env | xargs) ./venv/bin/python manage.py collectstatic --noinput
sudo -u www-data ./venv/bin/python manage.py createsuperuser
```

(Run `createsuperuser` with env loaded like `migrate`; use your domain in `ALLOWED_HOSTS` before testing forms.)

### Gunicorn (systemd)

```bash
sudo cp deploy/systemd/holisticmap.service /etc/systemd/system/holisticmap.service
sudo systemctl daemon-reload
sudo systemctl enable --now holisticmap
sudo systemctl status holisticmap
```

### nginx

```bash
sudo cp deploy/nginx/holisticmap.conf /etc/nginx/sites-available/holisticmap
sudo sed -i 's/YOUR_DOMAIN_HERE/your.domain.com/' /etc/nginx/sites-available/holisticmap
sudo ln -sf /etc/nginx/sites-available/holisticmap /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### TLS (Let’s Encrypt)

```bash
sudo certbot --nginx -d your.domain.com
```

Certbot adjusts nginx for HTTPS redirects.

---

## Part 3 — Updates after `git pull`

```bash
cd /srv/holisticmap
sudo systemctl stop holisticmap   # optional; minimizes race during migrations
sudo -u www-data git pull
sudo -u www-data ./venv/bin/pip install -r requirements.txt
sudo -u www-data env $(grep -v '^#' /etc/holisticmap.env | xargs) ./venv/bin/python manage.py migrate
sudo -u www-data env $(grep -v '^#' /etc/holisticmap.env | xargs) ./venv/bin/python manage.py collectstatic --noinput
sudo systemctl start holisticmap
```

---

## Troubleshooting

| Symptom | Check |
|---------|--------|
| `disallowed host` | `DJANGO_ALLOWED_HOSTS` matches the Host header exactly. |
| CSRF failures on HTTPS | Set `DJANGO_CSRF_TRUSTED_ORIGINS` and `DJANGO_USE_X_FORWARDED_PROTO=1`. |
| Postgres SSL errors | Ensure `DATABASE_URL` uses `sslmode=require` or `DATABASE_SSL_REQUIRE=True`. |
| 502 from nginx | `journalctl -u holisticmap`; socket path matches nginx `proxy_pass`; `sudo ls -la /run/holisticmap/`. |
| Static/CSS missing | `collectstatic`; nginx `alias` for `/static/`; restart `holisticmap`. |

---

## Security notes

- Do not commit `/etc/holisticmap.env` or real `DATABASE_URL` to git.
- Rotate **`SECRET_KEY`** only with care (sessions invalidate).
- Keep the VM patched: `sudo apt upgrade` regularly.
