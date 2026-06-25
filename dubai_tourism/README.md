<h1 align="center">🧳 Dubai Tourism — Tourism Management ERP (Odoo 19)</h1>

<p align="center">
  A complete Odoo 19 application for a Dubai tour agency — tour packages, customer
  bookings, fleet &amp; third-party transport, commissions, loyalty discounts and analytics.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Odoo-19.0-714B67?logo=odoo&logoColor=white" alt="Odoo 19"/>
  <img src="https://img.shields.io/badge/tests-36%20passing-success" alt="Tested"/>
  <img src="https://img.shields.io/badge/validated-on%20real%20Odoo-1f9d57" alt="Validated"/>
  <img src="https://img.shields.io/badge/License-LGPL--3.0-blue" alt="License"/>
</p>

---

## 🎯 The case study, requirement by requirement

> *"…a central system to track their services, vehicles, payments and manage their bookings… The agency owns a fleet of buses and vans… transportation for smaller groups… is arranged through a partnered local taxi company… earns revenue through tour package sales and transportation commissions… special benefits for families with young children and discounted rates for groups of ten or more… analytical tools to monitor booking trends…"*

| Requirement | Implementation |
|---|---|
| Tour package management | `tourism.tour.package` — destinations, duration, per-adult/child pricing, capacity, live stats & rating |
| Customer bookings | `tourism.booking` — full lifecycle (draft → confirmed → paid → completed), calendar of departures |
| Internal fleet allocation | `tourism.vehicle` (buses/vans/cars) + internal `tourism.transport.assignment` with seat checks |
| Third-party transport coordination | external assignments to partnered taxi companies (`res.partner.is_taxi_company`) |
| **Transportation commissions** | commission auto-computed on third-party transport — the agency's second revenue stream |
| Payment processing | payment-gated completion (a tour can't be completed until it's paid) |
| Family benefit (young children) | automatic **5%** discount when children travel |
| Group discount (10+) | automatic **10%** discount at the group threshold (stacks with the family benefit) |
| Booking trends & popular packages | **Graph + Pivot** analytics; per-package revenue & traveller counts |
| Popular destinations | destination popularity computed from confirmed travellers |
| Customer satisfaction | `tourism.review` star ratings → package average rating |
| Roles & access | Agent (sees own bookings) vs Manager (sees all) + record rules |
| Productivity | an **"Assign Transport" wizard**, a QWeb **tour-voucher PDF**, and seeded demo data |

### Enterprise extensions

| Capability | Implementation |
|---|---|
| **Scheduled departures** | `tourism.departure` — per-trip seat capacity with **overbooking prevention**, guide & vehicle assignment, seat/revenue tracking, departures calendar |
| **Configurable rules** | a **Settings** page (discount %s, group threshold, default commission, email & auto-cancel toggles) — no code change to retune the business |
| **Day-by-day itinerary** | `tourism.itinerary.line` per package |
| **Tour guides** | guide flag on partners, assignable to departures |
| **Email automation** | confirmation & receipt **mail templates** sent on confirm/pay (toggle in Settings) |
| **Scheduled cleanup** | `ir.cron` cancels overdue unpaid bookings (configurable) |
| **Accounting** | optional [`tourism_accounts`](../tourism_accounts) bridge auto-creates an itemised **customer invoice** (with tax & currency) on payment |
| **Customer portal** | logged-in customers track their bookings at **`/my/tours`** (own-records rule + HttpCase tests) |
| **Featured packages** | `is_featured` + promotional price, kanban ribbon |
| **Fleet utilization** | trips / passengers / avg seat-fill per vehicle + a Fleet Utilization report |
| **Analytics suite** | Package Performance & Destination Popularity reports (graph + pivot) |

---

## 🧱 Data model

```
tourism.destination ─M:N─ tourism.tour.package ─1:N─ tourism.booking ─N:1─ res.partner (customer)
                              │ (price, capacity)        │                      │ (taxi company flag)
                              │                          ├─1:N─ tourism.transport.assignment ─┐
                              └─1:N─ tourism.review       │            (internal | external)   │
                                                          │                                    ├─ tourism.vehicle (fleet)
                                                          └─ commission on third-party ────────┘
```

| Model | Purpose |
|---|---|
| `tourism.destination` | A place tours visit; popularity from confirmed travellers |
| `tourism.tour.package` | A sellable tour (pricing, capacity, revenue, rating) |
| `tourism.booking` | A customer reservation — pricing, discounts, lifecycle |
| `tourism.vehicle` | The agency's own fleet |
| `tourism.transport.assignment` | Internal-fleet or third-party transport + commission |
| `tourism.review` | Customer star rating feeding package ratings |
| `res.partner` *(extended)* | Taxi-company flag + tour-booking history & spend |

---

## ✅ Tested & validated

**31** `TransactionCase` tests (pricing, family + group discounts, configurable
rules, capacity, the payment-gated state machine, scheduled-departure
overbooking, internal seat limits, third-party commission, the transport wizard,
email/cron automation, package stats and ratings) — plus **2** more in the
accounting bridge — **all green on a real Odoo 19 instance**, with demo data
loading cleanly.

```bash
# core module
./odoo-bin -c odoo.conf -d test_db -i dubai_tourism --test-enable --stop-after-init
# accounting bridge (needs the accounting app)
./odoo-bin -c odoo.conf -d test_db -i tourism_accounts --test-enable --stop-after-init
```

## 🚀 Run it

```bash
docker compose -f deploy/docker-compose.yml up -d   # then http://localhost:8069 → Dubai Tourism
```

<p align="center"><sub>Built for the Technical Advanced Bootcamp · Odoo 19</sub></p>
