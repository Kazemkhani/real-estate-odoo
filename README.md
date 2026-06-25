<h1 align="center">🧳 Dubai Tourism ERP</h1>

<p align="center">
  A production-grade <b>Tourism Management ERP</b> for a Dubai tour agency, built on <b>Odoo 19</b>.<br/>
  Tour packages · bookings · fleet & third-party transport with commissions · family/group discounts ·
  customer portal · invoicing · analytics.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Odoo-19.0-714B67?logo=odoo&logoColor=white" alt="Odoo 19"/>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python 3.12"/>
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL 16"/>
  <img src="https://img.shields.io/badge/tests-39%20passing-success" alt="Tested"/>
  <img src="https://img.shields.io/badge/validated-on%20real%20Odoo-1f9d57" alt="Validated"/>
  <img src="https://img.shields.io/badge/License-LGPL--3.0-blue" alt="License"/>
</p>

---

## ⚡ Run it in 60 seconds

> Requires **Docker Desktop**. Full step-by-step (incl. a free public link) is in **[`RUN.md`](RUN.md)**.

```bash
docker compose up -d        # starts Odoo 19 + PostgreSQL
# open http://localhost:8069 → create DB (master pwd: admin), ✅ load demo data → app "Dubai Tourism"
```

---

## 🎯 What it does (the case study, covered A–Z)

| Requirement | Implementation |
|---|---|
| Tour **package management** | `tourism.tour.package` — destinations, pricing, capacity, itinerary, rating, stats |
| **Customer bookings** | `tourism.booking` — full lifecycle + departures **calendar** |
| **Scheduled departures** | `tourism.departure` — per-trip seat capacity with **overbooking prevention**, guide & vehicle |
| **Internal fleet** (buses/vans) | `tourism.vehicle` + internal transport with **seat checks** |
| **Third-party taxi** coordination | external transport to partnered taxi companies |
| **Transport commissions** | auto-computed on third-party transport (2nd revenue stream) |
| **Family** benefit / **group** discount | configurable 5% (children) + 10% (10+), stacking |
| **Payment processing** | payment-gated lifecycle + invoice on payment (with tax & currency) |
| **Customer portal** | logged-in customers track their bookings at `/my/tours` |
| **Analytics** | Booking Analysis, Package Performance, Destination Popularity, Fleet Utilization (graph + pivot) |
| **Automation** | confirmation/receipt emails + a scheduled auto-cancel of overdue unpaid bookings |
| **Roles** | Agent (sees own) vs Manager (sees all) + record rules |

Two modules:

| Module | Purpose | Depends |
|---|---|---|
| **`dubai_tourism`** | The Tourism ERP application | `base`, `mail`, `portal` |
| **`tourism_accounts`** | Invoicing bridge — invoice on payment | `dubai_tourism`, `account` |

---

## ✅ Tested & validated on real Odoo 19

```bash
# Core app (36 tests)
docker compose run --rm odoo odoo -d test -i dubai_tourism --test-enable --test-tags=/dubai_tourism --stop-after-init --without-demo=all
# Invoicing bridge (3 tests, installs Accounting)
docker compose run --rm odoo odoo -d testb -i tourism_accounts --test-enable --test-tags=/tourism_accounts --stop-after-init
```

`dubai_tourism` **36 tests** + `tourism_accounts` **3 tests**, all green; demo data loads cleanly.

---

## 📚 Documentation

- **[`RUN.md`](RUN.md)** — run it on any laptop (Docker), publish a public link, troubleshoot.
- **[`CAPSTONE.md`](CAPSTONE.md)** — the full capstone brief: requirement traceability, Odoo 19 playbook, demo script, roadmap.
- **[`CLAUDE.md`](CLAUDE.md)** — operating rules for continuing the build with an AI session.

---

<p align="center"><sub>Built for the Technical Advanced Odoo Bootcamp · Odoo 19</sub></p>
