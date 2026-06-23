# 🚀 Deploying Sporty Summer DXB (Odoo 19)

Goal: get a **public link** you can send to your instructor, running on macOS.

There are two realistic ways to do that. Start with **Option A** — it's free, takes
~10 minutes, and gives you a real `https://…` link. Move to **Option B** when you
want a link that stays up even when your laptop is closed.

---

## Option A — Fastest free public link (run on your Mac + a tunnel) ✅ recommended

You run Odoo locally with Docker, then a Cloudflare tunnel publishes it on a public
HTTPS URL. No account, no credit card.

### 1. Install Docker Desktop
Download from <https://www.docker.com/products/docker-desktop/> (pick the Apple
Silicon or Intel build for your Mac), install it, and **launch it once** so the
whale icon sits in your menu bar.

### 2. Start Odoo
From a Terminal, in the repo folder:
```bash
docker compose -f deploy/docker-compose.yml up -d
```
First run pulls the images (a few minutes). Then open <http://localhost:8069>.

### 3. Create the database
On the first screen:
- **Master Password:** `admin` (from `deploy/odoo.conf` — change it for anything real)
- **Database Name:** `sporty`
- set an email + password for your admin login
- ✅ tick **Load demonstration data** (so the calendar, classes and equipment are pre-filled)

Click **Create database**. When it loads, go to **Apps**, remove the *Apps* filter,
search **Sporty Summer**, and click **Activate**. (Demo data already installs it if
you ticked the box.)

### 4. Publish a public link with Cloudflare Tunnel
In a **second** Terminal tab:
```bash
brew install cloudflared          # one-time (install Homebrew first if needed: https://brew.sh)
cloudflared tunnel --url http://localhost:8069
```
It prints a line like:
```
https://random-words-1234.trycloudflare.com
```
**That is your shareable link.** Send it to your instructor.

> ⚠️ The link works only while both Terminal tabs are running and your Mac is awake.
> Stop with `Ctrl+C`. To stop Odoo: `docker compose -f deploy/docker-compose.yml down`
> (add `-v` to also wipe the database).

---

## Option B — Always-on hosted link (cloud VM)

For a link that stays up 24/7, run the same stack on a small cloud server.

1. Create a tiny Linux VM (2 GB RAM is enough): **DigitalOcean** / **Hetzner**
   (~$5/mo), or **Oracle Cloud Always-Free** (no cost, needs a card to sign up).
2. Install Docker on it, copy this repo up (`git clone …`), then:
   ```bash
   docker compose -f deploy/docker-compose.yml up -d
   ```
3. Open `http://<server-ip>:8069` and create the database as in Option A.
4. (Recommended) Put it behind a domain + HTTPS with Caddy or a Cloudflare Tunnel
   so the URL is `https://…` instead of a bare IP.

The `deploy/Dockerfile` bakes the modules into a single image, which is what
managed hosts (Railway, Render, Fly.io) build from — handy if you'd rather use a
platform than manage a VM. Those platforms need their database env vars wired to
Odoo (`HOST`, `PORT`, `USER`, `PASSWORD`) and Odoo's HTTP port exposed; the VM
route above avoids that fiddliness.

---

## Updating after a code change
```bash
# restart and upgrade just our module
docker compose -f deploy/docker-compose.yml restart odoo
# or force a module upgrade:
docker compose -f deploy/docker-compose.yml run --rm odoo \
  odoo -d sporty -u sporty_summer --stop-after-init
```

## Run the automated tests inside the container
```bash
docker compose -f deploy/docker-compose.yml run --rm odoo \
  odoo -d test_db -i sporty_summer,estate,estate_accounts \
  --test-enable --stop-after-init
```
