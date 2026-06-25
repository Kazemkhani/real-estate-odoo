<h1 align="center">🏟️ Sporty Summer DXB — Sports Facility Management ERP</h1>

<p align="center">
  A complete Odoo 19 application for the <b>Sporty Summer DXB (Summer 2026)</b> bootcamp case study —
  court bookings, coaching classes, equipment loans, payments and loyalty, in one platform.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Odoo-19.0-714B67?logo=odoo&logoColor=white" alt="Odoo 19"/>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python 3.12"/>
  <img src="https://img.shields.io/badge/tests-20%20cases-success" alt="Tested"/>
  <img src="https://img.shields.io/badge/License-LGPL--3.0-blue" alt="License"/>
</p>

---

## 🎯 The case study, requirement by requirement

> *"Sporty Summer DXB … is experiencing operational challenges, including double-booked courts, overcrowded game sessions, unpaid reservations, and difficulties tracking sports equipment…"*

Every requirement in the brief maps to a concrete, tested feature:

| Case-study requirement | How it's implemented |
|---|---|
| **Centralized court availability & bookings** | `sport.court` + `sport.booking` with a **calendar view** (week/day) for real-time schedules |
| **Prevent double-booked courts** | `@api.constrains` rejects any overlapping live booking on the same court (interval-overlap test) |
| **Enforce participant limits per sport** | each `sport.type` sets `max_participants`; a constraint blocks oversized sessions |
| **Payments settled before participation** | a `draft → confirmed → paid → played` state machine; `Mark as Played` is blocked until **paid** |
| **First-come-first-served class registration** | `sport.coaching.class` with capacity + `sport.class.registration`; a constraint enforces FCFS seat limits |
| **Loyalty for frequent visitors** | `res.partner` computes visits → `is_frequent_visitor` → an automatic **10% loyalty discount** on bookings |
| **Track equipment loaned to customers** | `sport.equipment` (live stock) + `sport.equipment.loan` with on-loan / returned / **lost** / **damaged** states |
| **Record losses & damages** | loan states + `penalty_amount`; lost/damaged units leave the available stock automatically |
| **Real-time visibility & analytics** | **Graph + Pivot** views (revenue by sport, utilisation by court & status) |
| **Roles & access control** | `Staff` (reception) vs `Manager` security groups + access rules; Configuration menu is manager-only |
| **Documentation** | a QWeb **PDF booking confirmation** in the Print menu |

---

## 🧱 Data model

```
sport.type ──1:N── sport.court ──1:N── sport.booking ──N:1── res.partner (customer)
   │  (max_participants, price)              │                     │ (loyalty)
   │                                         └──1:N── sport.equipment.loan ──N:1── sport.equipment
   └──1:N── sport.coaching.class ──1:N── sport.class.registration ──N:1── res.partner
                  (coach, capacity)            (first-come, first-served)
```

| Model | Purpose |
|---|---|
| `sport.type` | A sport and its rules (per-session participant limit, default duration) |
| `sport.court` | A bookable court; price per hour; availability/maintenance |
| `sport.booking` | A reservation — the operational core (state machine, pricing, guards) |
| `sport.coaching.class` | A summer coaching program with limited seats |
| `sport.class.registration` | A customer's seat in a class (FCFS, payment-tracked) |
| `sport.equipment` | Loanable stock with live available/loaned/lost quantities |
| `sport.equipment.loan` | Equipment issued to a customer; return/loss/damage tracking |
| `res.partner` *(extended)* | Adds coach flag + loyalty (frequent-visitor discount) |

---

## ✅ Tests

20 `TransactionCase` tests verify the business rules, not just the screens:

- **Bookings** — auto reference, duration & pricing, date validation, **participant limit**, **double-booking rejection**, adjacent slots allowed, drafts don't block the calendar, **payment-gated participation**, and the **loyalty discount**.
- **Coaching** — seat tracking, **first-come-first-served capacity**, drafts don't consume seats, duplicate-registration guard.
- **Equipment** — stock tracking, returns replenish stock, lost items leave circulation, **over-loan prevention**.

```bash
./odoo-bin -c odoo.conf -d test_db -i sporty_summer --test-enable --stop-after-init
```

---

## 🚀 Install

```bash
cp -R sporty_summer /path/to/your/addons/
./odoo-bin -c odoo.conf -d mydb -i sporty_summer
#   http://localhost:8069  →  Sporty Summer
```

Install with demo data to land on a populated calendar, classes and equipment.

---

<p align="center"><sub>Built for the Technical Advanced Bootcamp · Odoo 19 · Summer 2026</sub></p>
