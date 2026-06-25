# ▶️ RUN — Dubai Tourism ERP on any laptop

This guide takes someone from **zero** to a running Dubai Tourism ERP in a few
minutes, on macOS, Windows or Linux. No Odoo or Python knowledge required.

---

## 0. Install Docker Desktop (one time)
Download and install: <https://www.docker.com/products/docker-desktop/>
(pick the build for your machine — Apple Silicon, Intel, or Windows). **Launch
it once** and wait until the whale icon stops animating.

## 1. Get the project
```bash
git clone https://github.com/Kazemkhani/dubai-tourism-erp.git
cd dubai-tourism-erp
```
> No git? Download the ZIP from the GitHub page (**Code → Download ZIP**), unzip,
> and `cd` into the folder.

## 2. Start it
```bash
docker compose up -d
```
First run downloads Odoo + PostgreSQL (a few minutes). It's ready when
`docker compose ps` shows both services **Up**.

> **If a Docker Hub pull is rate-limited (403),** use Google's mirror once:
> ```bash
> docker pull mirror.gcr.io/library/odoo:19 && docker tag mirror.gcr.io/library/odoo:19 odoo:19
> docker pull mirror.gcr.io/library/postgres:16 && docker tag mirror.gcr.io/library/postgres:16 postgres:16
> docker compose up -d
> ```

## 3. Open & create the database
Go to **<http://localhost:8069>** and fill in:
- **Master Password:** `admin`
- **Database Name:** `tourism`
- **Email / Password:** your admin login
- ✅ **Load demonstration data** (so packages, departures, fleet and bookings are pre-filled)

Click **Create database**. When it loads, open the apps menu (top-left grid) →
**Dubai Tourism**. (With demo data ticked, the app is already installed.)

## 4. (Optional) Enable invoicing
To bill customers automatically on payment: **Apps** → remove the *Apps* filter →
search **Tourism Accounts** → **Activate** (this installs Odoo Accounting too).

## 5. (Optional) Share a public link
Run Odoo locally and expose it with a free Cloudflare tunnel:
```bash
brew install cloudflared            # macOS (else see cloudflare docs)
cloudflared tunnel --url http://localhost:8069
```
It prints a public `https://…trycloudflare.com` URL — share it. (Live only while
your machine and the tunnel are running.)

---

## Useful commands
```bash
docker compose logs -f odoo         # watch the server log
docker compose restart odoo         # restart after a code change
docker compose down                 # stop
docker compose down -v              # stop AND wipe the database

# Run the automated test suites
docker compose run --rm odoo odoo -d t1 -i dubai_tourism  --test-enable --test-tags=/dubai_tourism  --stop-after-init --without-demo=all
docker compose run --rm odoo odoo -d t2 -i tourism_accounts --test-enable --test-tags=/tourism_accounts --stop-after-init
```

## Troubleshooting
| Symptom | Fix |
|---|---|
| `cd: no such file or directory` | Run `git clone` first, then `cd dubai-tourism-erp`. |
| Port 8069 already in use | Stop the other service, or change the left port in `docker-compose.yml` (e.g. `8070:8069`). |
| Docker Hub `403` / rate limit | Use the `mirror.gcr.io` commands in step 2. |
| Page won't load right after `up` | Give it ~30–60s on first boot; check `docker compose logs -f odoo`. |
| "Database already exists" | Pick a new DB name, or `docker compose down -v` to reset. |

---

## What you'll see
- **Bookings** with family/group discounts and a departures **calendar**
- **Departures** with seat capacity & overbooking prevention
- **Transport** — internal fleet *and* third-party taxi (with commission)
- **Reporting** — Booking Analysis, Package Performance, Destination Popularity, Fleet Utilization
- **Customer portal** at `/my/tours`
- A **Tour Voucher** PDF on any booking

Enjoy exploring Dubai. 🌇
