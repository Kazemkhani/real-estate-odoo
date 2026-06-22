<h1 align="center">🏡 Real Estate — Odoo 19</h1>

<p align="center">
  A complete, production-grade property-management module for Odoo 19 —<br/>
  listings, offers, a full sale lifecycle, automatic invoicing, analytics, and role-based security.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Odoo-19.0-714B67?logo=odoo&logoColor=white" alt="Odoo 19"/>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python 3.12"/>
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL 16"/>
  <img src="https://img.shields.io/badge/License-LGPL--3.0-blue" alt="License LGPL-3.0"/>
  <img src="https://img.shields.io/badge/status-demo--ready-1f9d57" alt="Demo ready"/>
</p>

<p align="center">
  <img src="docs/demo.gif" width="760" alt="Real Estate module demo"/>
</p>

---

## ✨ Overview

This project turns the official Odoo *“Server Framework 101”* tutorial into a polished, end-to-end application. A property moves through a clean state machine — **New → Offer Received → Offer Accepted → Sold** (or Cancelled) — and a sale automatically raises a **customer invoice** in Odoo Accounting. It ships with a visual Kanban board, built-in analytics, a PDF brochure, sample data, and an Agent/Manager security model.

It is built as **two modules**:

| Module | Responsibility |
|---|---|
| [`estate`](estate/) | The core domain — properties, types, tags, amenities, offers, views, security, reporting |
| [`estate_accounts`](estate_accounts/) | Thin bridge that bills the buyer (creates an invoice) when a property is sold |

---

## 🎯 Features

**Lifecycle & business logic**
- 🔄 Status-bar state machine with **Sell** / **Cancel** actions and guards
- 🤝 Offers with **Accept / Refuse** — accepting one locks the selling price and **auto-refuses the rest**
- 🧮 Computed fields — total area, best offer, offer count
- ✅ Validation — `models.Constraint` (price > 0), `@api.constrains` (selling ≥ 90% of expected), delete-guard

**Interface**
- 🗂️ **Kanban** board (grouped by type, colour-coded, ribbons), List, rich Form
- 📊 **Graph + Pivot** analytics out of the box
- 🖼️ Property images, monetary pricing, smart **“Offers”** button, many2many tags & checkboxes

**Accounting**
- 🧾 Selling a property **auto-creates a customer invoice** (6% commission + admin fee) via Odoo `account`

**Security**
- 👥 **Agent** vs **Manager** roles (`res.groups.privilege`) — agents see only their own listings; managers see all

**Reporting & data**
- 📄 QWeb **PDF “Property Sheet”** in the Print menu
- 🌱 Sample data (properties in multiple states, 3 types, tags, **28 amenities**)

---

## 📸 Screenshots

| Kanban pipeline | Property form |
|:--:|:--:|
| ![Kanban](docs/screenshots/kanban.png) | ![Form](docs/screenshots/form.png) |
| **Analytics (Graph)** | **Auto-generated invoices** |
| ![Analytics](docs/screenshots/analytics.png) | ![Invoices](docs/screenshots/invoices.png) |
| **Offers & negotiation** | **Validation** |
| ![Offers](docs/screenshots/offers.png) | ![Constraint](docs/screenshots/constraint.png) |

▶️ Full demo video: [`docs/demo.mp4`](docs/demo.mp4)

---

## 🧱 Data model

```
res.partner ──┐                         estate.property.type ──1:N── estate.property
              │ (buyer)                 estate.property.tag  ──M:N── estate.property
res.users  ───┤ (salesperson)           estate.property.amenity M:N─ estate.property
              │                                                       │ 1:N
              └─────────────── estate.property.offer ◄────────────────┘ (offers)
```

| Model | Purpose | Key relations |
|---|---|---|
| `estate.property` | A property listing | `Many2one` type/buyer/agent · `One2many` offers · `Many2many` tags & amenities |
| `estate.property.type` | Category (House, Apartment…) | `One2many` properties |
| `estate.property.tag` | Marketing labels | `Many2many` |
| `estate.property.amenity` | Feature catalogue (28 items) | `Many2many` |
| `estate.property.offer` | A buyer’s bid | `Many2one` property & partner |
| `res.users` *(extended)* | Adds the agent’s properties | `One2many` |

---

## 🚀 Installation

> Requires Odoo 19, Python 3.12+, PostgreSQL 12+.

```bash
# 1. Put both modules on your Odoo addons path
cp -R estate estate_accounts /path/to/your/addons/

# 2. Install (estate_accounts pulls in Accounting automatically)
./odoo-bin -c odoo.conf -d mydb -i estate,estate_accounts

# 3. Open the app
#    http://localhost:8069  →  Real Estate
```

Then enable Developer Mode to explore the Graph/Pivot views and the PDF report.

---

## 🗂️ Project structure

```
real-estate-odoo/
├── estate/                      # core module
│   ├── models/                  #   property, type, tag, amenity, offer, res.users
│   ├── views/                   #   kanban, list, form, graph, pivot, search, menus
│   ├── security/                #   groups, record rules, access rights
│   ├── report/                  #   QWeb PDF property sheet
│   └── data/                    #   sample types, tags, amenities, listings
├── estate_accounts/             # invoicing bridge (depends on `account`)
│   └── models/estate_property.py#   overrides sell → creates account.move
└── docs/                        # demo video, gif, screenshots
```

---

## 🛠️ Tech stack

**Odoo 19.0** · **Python 3.12** · **PostgreSQL 16** · QWeb · Owl/Kanban

Demonstrates: ORM models & relations, computed/related fields, `@api.depends` / `@api.onchange` / `@api.constrains`, `models.Constraint`, action methods, view inheritance (`xpath`), cross-module model inheritance, record rules & groups, and QWeb reporting.

---

## 📝 License

Released under the **LGPL-3.0** license — see [`LICENSE`](LICENSE).

<p align="center"><sub>Built during an advanced Odoo bootcamp · Odoo 19</sub></p>
