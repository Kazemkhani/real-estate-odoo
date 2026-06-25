# 🧳 Dubai Tourism ERP — Capstone Master Brief & Build-Out Charter

> **One file to rule the build.** This is the single source of truth for the
> Dubai Tourism ERP capstone: what it is, why it's built the way it is, exactly
> how to run it locally against **both** repositories, proof that it matches the
> case study, the Odoo 19 engineering playbook, the live demo script for the
> presentation, and a precision roadmap (with copy‑paste prompts) to take it to
> "world‑class level 11."
>
> **Audience:** the human presenter **and** the next AI build session.
> **Standard:** Steve‑Jobs‑grade perfectionism. Nothing is "done" until it
> **loads, runs, and passes tests on a real Odoo 19 instance.** Claims without a
> green test run are not accepted.

---

## 0. How to use this document

- **Presenter (you):** read §1, §6 (Run it locally), §9 (Demo script). That's
  enough to install and present tomorrow.
- **Next AI session:** read **the whole thing**, then start at §11 (Operating
  Charter) and §10 (Roadmap). Do not write a line of code before reading §8
  (Odoo 19 Playbook) — it encodes bugs already paid for in blood.
- **Everyone:** §4 is the contract. Every requirement in the case study maps to
  a concrete, tested artifact. If you change scope, update §4.

---

## 1. Mission & context

We are building the **Dubai Tourism ERP** as the **capstone** for the Technical
Advanced Odoo Bootcamp, presented **tomorrow**. It is a Tourism Management ERP
on **Odoo 19** for a Dubai tour agency that has outgrown phone‑based bookings and
spreadsheets.

The build is **already substantially complete and validated** (see §4, §7). The
job now is to (a) run it locally on the presenter's machine against the team's
bench, (b) rehearse the demo, and (c) optionally push it to "level 11" using §10.

**Non‑negotiables**
1. It must **install and run on Odoo 19** with demo data, no errors.
2. Every case‑study requirement must be demonstrable **live** (§9).
3. Every behavioural rule must be covered by an **automated test that passes**.
4. The code must read like it belongs in Odoo core — idiomatic, commented where
   intent isn't obvious, no dead code.

---

## 2. The two repositories (and how they relate)

| Repo | Role | Notes |
|---|---|---|
| **`kazemkhani/real-estate-odoo`** | **Our build.** Contains the finished addon modules. | Branch: `claude/workshop-project-portfolio-lpkln6`. Open PR **#2**. This is where `dubai_tourism` + `tourism_accounts` live, plus a Docker `deploy/` stack. |
| **`Reihaneh-rmz/odoo`** | **The team bench / reference.** A full **fork of Odoo 19** (the entire framework + `addons/`). `kazemkhani` is a collaborator. | This is a complete Odoo source tree. Our modules are *dropped into* its `addons/` to run on the team's official bench. |

**Mental model:** `Reihaneh-rmz/odoo` is the *engine* (Odoo 19 itself).
`dubai_tourism` + `tourism_accounts` are our *application modules* that plug into
that engine. They are designed to be path‑independent: copy the two folders into
**any** Odoo 19 `addons` directory and install.

> **Source of truth for the engine:** Reihaneh's fork (branch `19.0`).
> **Source of truth for our app:** the `dubai_tourism` and `tourism_accounts`
> folders in `kazemkhani/real-estate-odoo`.

---

## 3. The case study (verbatim — the contract)

> **DUBAI TOURISM ERP**
> A rising tourism agency is helping new tourists explore the city easily by
> providing suggestions and buses to them. However, Dubai is always getting
> swarmed by tourists and they are getting overwhelmed by the number of requests
> that they are getting. They have been taking appointments by phone so far but
> now they want a central system to track their services, vehicles, payments and
> manage their bookings easily.
>
> To improve efficiency and support future growth, the agency plans to implement
> a Tourism Management ERP system using Odoo. The system will centralize all
> business operations, including **tour package management, customer bookings,
> transportation scheduling, payment processing, and reporting**. The agency owns
> a **fleet of buses and vans** that are used to transport large tourist groups,
> while transportation for **smaller groups, couples, and families is arranged
> through a partnered local taxi company**. The ERP system must therefore support
> both **internal vehicle allocation and third‑party transportation
> coordination**.
>
> The agency earns revenue through **tour package sales and transportation
> commissions**. To enhance customer satisfaction and remain competitive, it
> offers **special benefits for families traveling with young children** and
> **discounted rates for groups consisting of ten or more tourists**. Management
> also requires **analytical tools** to monitor booking trends, identify the most
> popular destinations and tour packages, evaluate transportation utilization,
> and measure overall business performance.
>
> By integrating reservations, transportation management, customer services,
> financial transactions, and business analytics into a single platform, the
> agency aims to streamline operations, reduce manual workload, improve customer
> experience, and support its continued expansion within Dubai's tourism
> industry.

---

## 4. Requirement → implementation traceability (the alignment proof)

Every clause of §3 maps to a concrete, **tested** artifact. ✅ = built & validated
on Odoo 19. 🔜 = roadmap (see §10).

| # | Case‑study requirement | Implementation | Where | Status |
|---|---|---|---|---|
| 1 | Central system to track services, vehicles, payments, bookings | The `dubai_tourism` application (6 menus, 9 models) | whole module | ✅ |
| 2 | Tour **package management** | `tourism.tour.package` (destinations, pricing, capacity, duration, itinerary, stats, rating) | `models/tourism_tour_package.py` | ✅ |
| 3 | **Customer bookings** | `tourism.booking` (lifecycle, pricing, calendar) | `models/tourism_booking.py` | ✅ |
| 4 | **Transportation scheduling** | `tourism.transport.assignment` + `tourism.departure` (vehicle per departure) | `models/tourism_transport_assignment.py`, `tourism_departure.py` | ✅ |
| 5 | **Payment processing** | payment‑gated state machine + `tourism_accounts` invoice on payment | booking states; `tourism_accounts/` | ✅ |
| 6 | **Reporting / analytics** | Graph + Pivot views; "Booking Analysis" reporting menu | `views/tourism_booking_views.xml`, menus | ✅ |
| 7 | **Fleet of buses and vans** (large groups) | `tourism.vehicle` (type bus/van/car, seats) + internal assignment with **seat checks** | `models/tourism_vehicle.py` | ✅ |
| 8 | **Third‑party taxi** for small groups/couples/families | external assignment to `res.partner.is_taxi_company` | `tourism_transport_assignment.py` | ✅ |
| 9 | Support **both** internal & third‑party | `transport_type` selection internal/external with per‑mode validation | same | ✅ |
| 10 | Revenue from **package sales** | `booking.amount_total` + invoice | booking, bridge | ✅ |
| 11 | Revenue from **transport commissions** | `commission_amount` auto‑computed on third‑party transport | `tourism_transport_assignment.py` | ✅ |
| 12 | **Family** benefit (young children) | configurable family discount (default 5%) when children present | `tourism_booking.py`, Settings | ✅ |
| 13 | **Group** discount (10+) | configurable group discount (default 10%) at threshold | `tourism_booking.py`, Settings | ✅ |
| 14 | Monitor **booking trends** | Graph/Pivot grouped by package, date, state, agent | search + analytics views | ✅ |
| 15 | Most **popular destinations & packages** | destination popularity (travellers), package booking/traveller/revenue/rating | computed fields + smart buttons | ✅ |
| 16 | Evaluate **transportation utilization** | per‑vehicle trip count; commission/cost on assignments | `tourism_vehicle.py`, pivot | ✅ (basic) / 🔜 dedicated fleet‑utilization dashboard |
| 17 | Measure **overall business performance** | revenue analytics, departure revenue, partner spend | pivot/graph, computed | ✅ |
| 18 | Data‑driven marketing / promote high‑demand | ratings + analytics; (recommendation/"featured" flag) | reviews, analytics | ✅ / 🔜 "featured package" + portal suggestions |
| 19 | "Providing **suggestions**" to tourists | destinations + packages catalogue | catalogue | ✅ / 🔜 customer **portal** with suggestions |
| 20 | Reduce manual workload | email automation (confirm/receipt), auto‑cancel cron, sequences | `data/mail_templates.xml`, `data/tourism_cron.xml` | ✅ |

**Roadmap delivered (all validated on Odoo 19):**
- ✅ **Customer portal** for self‑service — logged‑in customers see their bookings at `/my/tours` (R1).
- ✅ **Fleet utilization** — trips/passengers/avg seat‑fill per vehicle + a Fleet Utilization report (R3).
- ✅ **Featured/recommended packages** with a promotional price (R4).
- ✅ **Taxes & currency** on invoices via the bridge (R5).
- ✅ **Analytics suite** — Package Performance + Destination Popularity reports (R2).

**Remaining (deliberately deferred — call out as "next iteration"):**
- **SMS/WhatsApp** confirmations (R6) — needs an IAP/SMS gateway, so it isn't
  demoable offline; left as a toggle‑ready future item.

---

## 5. Current architecture

### 5.1 Modules in `kazemkhani/real-estate-odoo`
| Module | Purpose | Depends |
|---|---|---|
| **`dubai_tourism`** | The Tourism ERP application | `base`, `mail` |
| **`tourism_accounts`** | Invoicing bridge (invoice on payment) | `dubai_tourism`, `account` |
| `sporty_summer` | (Sister capstone) Sports Facility ERP | `base`, `mail` |
| `estate`, `estate_accounts` | Tutorial baseline + tests/CI | `base`, `mail`, `account` |
| `deploy/` | One‑command Docker stack + Dockerfile + guide | — |

### 5.2 `dubai_tourism` models (the application)
```
tourism.destination ─M:N─ tourism.tour.package ─1:N─ tourism.booking ─N:1─ res.partner (customer)
        (popularity)        │  price, capacity,        │  lifecycle, pricing,    │  is_taxi_company
                            │  itinerary, rating       │  discounts              │  is_tour_guide
                            │                          ├─1:N─ tourism.transport.assignment ─┐
        tourism.itinerary.line ◄─1:N─┘                 │        internal | external          │
        tourism.review ◄─────1:N──────┘                │        + commission                 ├─ tourism.vehicle (fleet)
        tourism.departure ──1:N───────────────────────-┘  (seat capacity, overbooking guard) ┘
                 (guide, vehicle, seats)
res.config.settings  → discount %s, threshold, commission, email/cron toggles
```
| Model | File | Heart of it |
|---|---|---|
| `tourism.tour.package` | `tourism_tour_package.py` | product: pricing, capacity, stats, rating |
| `tourism.destination` | `tourism_destination.py` | popularity from confirmed travellers |
| `tourism.itinerary.line` | `tourism_itinerary_line.py` | day‑by‑day plan |
| `tourism.departure` | `tourism_departure.py` | scheduled trip + **overbooking guard** |
| `tourism.booking` | `tourism_booking.py` | lifecycle, discounts, payment gate, emails, cron |
| `tourism.transport.assignment` | `tourism_transport_assignment.py` | internal/external + commission |
| `tourism.vehicle` | `tourism_vehicle.py` | fleet (bus/van/car), seats, state |
| `tourism.review` | `tourism_review.py` | star rating → package average |
| `res.partner` (ext) | `res_partner.py` | taxi‑company & guide flags, spend |
| `res.config.settings` | `res_config_settings.py` | configurable business rules |

### 5.3 Key non‑model files
- `security/tourism_security.xml` — Agent/Manager groups + record rules (agents see own bookings).
- `security/ir.model.access.csv` — 17 access rules.
- `data/tourism_sequence.xml` — `TB`/`TA` reference sequences.
- `data/mail_templates.xml` — confirmation + receipt emails.
- `data/tourism_cron.xml` — auto‑cancel overdue unpaid bookings.
- `report/tourism_booking_report.xml` — QWeb **tour voucher** PDF.
- `demo/tourism_demo.xml` — destinations, packages, fleet, taxi co, guide, bookings, departures, reviews.
- `wizard/tourism_assign_transport_wizard.py` — "Assign Transport" dialog.

---

## 6. Run it locally — A‑to‑Z (your device)

> Prereqs on your Mac/PC: **Docker Desktop** (recommended path), or a native
> Odoo 19 + PostgreSQL setup. You have full Git access to both repos.

### Option A — Docker, from our repo (fastest, recommended for the demo)
```bash
# 1. Get our build
git clone https://github.com/Kazemkhani/real-estate-odoo.git
cd real-estate-odoo
git checkout claude/workshop-project-portfolio-lpkln6

# 2. Start Odoo 19 + Postgres (mounts all our modules read-only)
docker compose -f deploy/docker-compose.yml up -d

# 3. Open http://localhost:8069 → create DB:
#    Master Password: admin   |   Database: tourism   |   ✅ Load demonstration data
#    Then Apps → search "Dubai Tourism" → Activate (already installed if demo ticked)
```
> If image pulls are rate‑limited on Docker Hub, pull via Google's mirror then retag:
> ```bash
> docker pull mirror.gcr.io/library/odoo:19 && docker tag mirror.gcr.io/library/odoo:19 odoo:19
> docker pull mirror.gcr.io/library/postgres:16 && docker tag mirror.gcr.io/library/postgres:16 postgres:16
> ```

### Option B — On the team bench (`Reihaneh-rmz/odoo`)  ← use this to present "on our fork"
```bash
# 1. Clone the team's Odoo 19 fork (the engine)
git clone https://github.com/Reihaneh-rmz/odoo.git odoo-bench
cd odoo-bench && git checkout 19.0

# 2. Bring our two modules into its addons path
git clone https://github.com/Kazemkhani/real-estate-odoo.git /tmp/ourbuild
git -C /tmp/ourbuild checkout claude/workshop-project-portfolio-lpkln6
cp -R /tmp/ourbuild/dubai_tourism   addons/dubai_tourism
cp -R /tmp/ourbuild/tourism_accounts addons/tourism_accounts

# 3. Run it (native) — needs Python 3.12 + PostgreSQL running locally
pip install -r requirements.txt
./odoo-bin -d tourism --addons-path=addons -i dubai_tourism --without-demo=False
# open http://localhost:8069
```
> **Committing back to the bench:** because `kazemkhani` is a collaborator on
> `Reihaneh-rmz/odoo`, you can branch on the fork and PR the two addon folders
> into its `addons/`. Keep the addon code identical to our repo — our repo stays
> the canonical source; the fork is where it's demoed on the shared engine.

### Run the automated tests (proof for the panel)
```bash
# Core app (fast, no accounting needed)
docker compose -f deploy/docker-compose.yml run --rm odoo \
  odoo -d testdb -i dubai_tourism --test-enable --test-tags=/dubai_tourism --stop-after-init --without-demo=all
# Expect: "0 failed, 0 error(s) of 31 tests"

# Accounting bridge (installs the Accounting app)
docker compose -f deploy/docker-compose.yml run --rm odoo \
  odoo -d testbridge -i tourism_accounts --test-enable --test-tags=/tourism_accounts --stop-after-init
# Expect: "0 failed, 0 error(s) of 2 tests"
```

---

## 7. Validation evidence (already achieved on Odoo 19)

| Suite | Result | What it proves |
|---|---|---|
| `dubai_tourism` | **31 tests, 0 failed** | pricing, configurable family/group discounts, capacity, payment‑gated lifecycle, **departure overbooking guard**, internal seat limits, third‑party commission, transport wizard, email + cron automation, package/destination stats, ratings |
| `tourism_accounts` | **2 tests, 0 failed** | invoice raised on payment, itemised lines, invoice origin |
| Module + demo load | **clean, exit 0** | all views/security/data/reports parse and load on Odoo 19 |

> Reproduce any time with the commands in §6. **Do not trust green claims without
> re‑running these.** This is the project's definition of truth.

---

## 8. Odoo 19 engineering playbook (read before coding — paid‑for lessons)

These are real gotchas already hit and solved. Honor them.

1. **Views use `<list>`, not `<tree>`.** Odoo 19 renamed the element.
2. **SQL constraints are declarative:** `_check_x = models.Constraint("CHECK(...)", "msg")`. No `_sql_constraints` list.
3. **Aggregation attr is `aggregator=`,** not `group_operator=` (renamed).
4. **Chatter is `<chatter/>`** (self‑closing), not the old `<div class="oe_chatter">` block.
5. **Kanban cards use `<templates><t t-name="card">…`** (new card API). Fields used in the template are auto‑fetched.
6. **Lists:** hide columns with `column_invisible="1"`; a `monetary` widget needs its `currency_id` field present in the view.
7. **Settings actions must not use `target="inline"`** (removed) — omit target. Settings UI uses `<app>` / `<block>` / `<setting>` inside `base.res_config_settings_view_form`.
8. **`res.config.settings` Boolean stored as the string `"True"/"False"`** in `ir.config_parameter` — when reading via `get_param`, guard: `str(val).lower() not in ("false","0","","none")`.
9. **Searching a non‑stored computed field throws.** If a cron/domain filters on a computed field, give it `store=True` (this exact bug bit the sports module's expiry cron).
10. **Every non‑stored compute should declare `@api.depends(...)`** or Odoo logs a registry warning. Keep logs clean.
11. **Stored computed Monetary needs a currency field** on the record (`currency_id`), even if related.
12. **Behavioural tests:** tag `("post_install", "-at_install")`. Run a single module's tests with `--test-tags=/<module>`.
13. **Invoice tests:** subclass `odoo.addons.account.tests.common.AccountTestInvoicingCommon` (sets up a chart of accounts + journals). If the test user lacks your app's groups, **create your app records with `.sudo()`**.
14. **SQL `UNIQUE`/`CHECK` violations poison the cursor** in tests — wrap the expecting block in `with self.assertRaises(Exception), self.env.cr.savepoint():` and `@mute_logger("odoo.sql_db")`.
15. **Docker: a module not mounted = silently not installed** (`-i` is a no‑op, "0 tests" runs). Always add new modules to `deploy/docker-compose.yml` volumes **and** `deploy/Dockerfile` COPY lines.
16. **Manifest `data` order matters:** security → sequences → data → views (actions before the menus that reference them) → report → menus. Demo goes in `demo`.
17. **`res.users` group field is `group_ids`** in Odoo 19 (renamed from `groups_id`). Using `groups_id` in a `create()` raises `ValueError: Invalid field 'groups_id'`. (Bit the portal tests — fixed.)
18. **Portal pages** (`type='http', auth='user', website=True`) work with only the `portal` dependency (no `website` needed). Use `CustomerPortal._document_check_access(...)` for per-record access, render related fields on `.sudo()` records, and test with `HttpCase` + `self.authenticate(...)`.
19. **Validate before claiming done:** `-i <module> --test-enable --stop-after-init` and grep for `0 failed, 0 error`. Also do a `--without-demo=False` load to prove demo + views parse.

---

## 9. Capstone demo script (live click‑path for the panel)

Goal: hit **every** requirement in ~6 minutes. Log in as admin (a Manager).

1. **The catalogue (suggestions).** Open **Dubai Tourism → Packages → Tour Packages**
   (kanban). Show categories, prices, ratings, "Luxury Dubai Experience." Open one
   → **Itinerary** tab (day‑by‑day) and **Reviews**. *(Req 2, 15, 18, 19)*
2. **Scheduled departures.** **Departures** (calendar) → open a departure → show
   **seats booked / capacity**, assigned **guide**, vehicle. *(Req 4, 16)*
3. **Create a booking — family.** **Bookings → New.** Pick a departure, customer,
   **2 adults + 1 child** → watch the **family discount** appear; **Total** updates.
   Save → reference `TB00006` auto‑assigned. *(Req 3, 12)*
4. **Group discount.** New booking, **10 adults** → **group discount** kicks in
   automatically. *(Req 13)*
5. **Overbooking guard.** Try to add a booking that exceeds a departure's seats →
   **validation error**. "No double‑selling a full trip." *(Req 4, 16)*
6. **Transport — both modes.** On a booking click **Assign Transport** (wizard):
   first **Internal Fleet** (bus, seat check), then a second booking **Third‑Party
   Taxi** → **commission** auto‑computed (agency's 2nd revenue stream). *(Req 7, 8, 9, 11)*
7. **Payment + invoice.** **Register Payment** → state → Paid, a **receipt email**
   is queued, and (with `tourism_accounts`) an **itemised customer invoice** is
   created — open it via the **Invoice** smart button. *(Req 5, 10)*
8. **Automation & config.** **Configuration → Settings**: change the family % live
   → reopen a booking, discount recomputes. Mention the **auto‑cancel cron** for
   unpaid bookings. *(Req 12, 13, 20)*
9. **Analytics.** **Reporting → Booking Analysis** (pivot): revenue by package;
   switch to **Graph**; show **destination popularity** and **package revenue**.
   *(Req 6, 14, 15, 17)*
10. **Security.** Switch to an **Agent** user → they see **only their own
    bookings** (record rule). *(centralization & control)*
11. **Customer self‑service portal.** Log in as a **portal customer** (or open
    `/my`) → **Tour Bookings** card → `/my/tours` → open a booking. "No more phone
    calls — the tourist tracks their own trip." *(the phone‑to‑digital leap)*
12. **Reporting.** **Reporting → Package Performance / Destination Popularity /
    Fleet Utilization** (graph + pivot). *(data‑driven marketing)*
13. **Voucher PDF.** Print → **Tour Voucher** (now with guide + itinerary). *(documentation)*

> Have the **test output** (§7) on a terminal tab as the closing slide: "every
> rule you just saw is covered by an automated test — here's the green run."

---

## 10. Roadmap to "world‑class level 11" (prioritized, with prompts)

Each item is scoped so the next AI session can pick it up and **finish + validate
it** in one pass. Copy the prompt verbatim. **Definition of done for every item:
loads on Odoo 19, demo data still loads, and new tests pass (`0 failed`).**

### ✅ R1 — Customer Portal — **DONE**
Logged‑in customers get a "Tour Bookings" card on `/my`, a `/my/tours` list and
`/my/tours/<id>` detail, with an own‑bookings record rule and HttpCase tests.
*Next iteration:* a public **website** storefront (depend on `website`) where
anonymous visitors browse published packages and request a booking online.

### ✅ R2 — Analytics suite — **DONE (graph/pivot)**
Package Performance (revenue/travellers/rating by category) and Destination
Popularity reports under **Reporting**, alongside Booking Analysis & Fleet
Utilization. *Next iteration:* a single OWL/`spreadsheet_dashboard` KPI board.

### ✅ R3 — Fleet utilization — **DONE**
`trips_done`, `passengers_transported`, avg seat‑fill on `tourism.vehicle`;
graph/pivot/search on transport; a **Fleet Utilization** report. Tested.

### ✅ R4 — Featured/recommended packages — **DONE**
`is_featured` + `promo_price`, kanban "Featured" ribbon, promo applied to
bookings. Tested + demo.

### ✅ R5 — Taxes & currency on invoices — **DONE**
`tourism_accounts` applies the company default sale tax and sets invoice
currency. Tested with `AccountTestInvoicingCommon`.

### R6 — SMS/WhatsApp confirmations *(deferred — needs IAP gateway)*
> **Prompt:** "Behind a Settings toggle, send an SMS (depend on `sms`) on booking
> confirmation in addition to email. Test the trigger path. Validate."

### R7 — Polish pass (Jobs‑level finish)
> **Prompt:** "Audit every view for spacing, labels, empty‑state messages, and
> kanban aesthetics; add package cover images to demo; ensure the voucher PDF is
> beautiful. No functional regressions; demo + tests stay green."

---

## 11. Operating charter for the next AI session (the master prompt)

**Role.** You are a **senior Odoo 19 engineer** building a capstone‑grade ERP.
You write idiomatic, production‑quality Odoo. You are obsessed with correctness
and finish — Steve Jobs would not ship your work until it is effortless to use
and provably correct.

**Prime directives**
1. **Read this whole file first.** Then §8 (playbook) and §4 (contract). Never
   contradict §4 without updating it.
2. **Validate on a real Odoo 19 instance before saying "done."** The only
   acceptable evidence is a test run printing `0 failed, 0 error(s)` plus a clean
   `--without-demo=False` load. Paste the exact result lines.
3. **Don't break what works.** Re‑run the full §6 test commands after each change.
   Regressions are unacceptable.
4. **Every new behaviour gets a test.** Tag `("post_install","-at_install")`.
5. **Mount new modules** in `deploy/docker-compose.yml` *and* `deploy/Dockerfile`
   (see playbook #15) or your tests silently run nothing.
6. **Keep the contract green.** If you add scope, add a §4 row and a demo step.
7. **Commit in coherent units** with clear messages; push to
   `claude/workshop-project-portfolio-lpkln6` (our repo). Mirror the two addon
   folders into `Reihaneh-rmz/odoo/addons/` on a branch and open a PR there too
   (you're a collaborator) — keep the code byte‑identical between repos.
8. **Communicate like an engineer:** state what you changed, the validation
   command, and the green result. No hand‑waving.

**Workflow per task**
`plan → implement → static‑check (py_compile + XML well‑formed) → boot Odoo,
install with demo → run module tests → fix → re‑run → commit → push`.

**House style.** Match the existing modules: declarative constraints, computed
fields with `@api.depends`, action methods on the model, view inheritance via
`xpath`, comments only where intent isn't obvious. Reuse `sporty_summer` and
`dubai_tourism` as the reference for "how we do it here."

---

## 12. Definition of Done (acceptance criteria)

A change is **done** only when **all** are true:
- [ ] `python -m compileall <module>` clean; all XML well‑formed.
- [ ] `odoo -i <module> --without-demo=False --stop-after-init` → `Modules loaded`, no ERROR/Traceback.
- [ ] `odoo -i <module> --test-enable --test-tags=/<module> --stop-after-init` → **`0 failed, 0 error(s)`**.
- [ ] New/changed behaviour has a passing test.
- [ ] New modules are mounted in `deploy/` (compose + Dockerfile).
- [ ] §4 traceability and §9 demo script updated if scope changed.
- [ ] Committed and pushed; CI (static checks) green on the PR.

---

## 13. Appendix

### 13.1 Command cheat‑sheet
```bash
# Boot stack / open app
docker compose -f deploy/docker-compose.yml up -d      # http://localhost:8069
# Upgrade a module after code change
docker compose -f deploy/docker-compose.yml run --rm odoo odoo -d tourism -u dubai_tourism --stop-after-init
# Tests (core / bridge)
docker compose -f deploy/docker-compose.yml run --rm odoo odoo -d t1 -i dubai_tourism --test-enable --test-tags=/dubai_tourism --stop-after-init --without-demo=all
docker compose -f deploy/docker-compose.yml run --rm odoo odoo -d t2 -i tourism_accounts --test-enable --test-tags=/tourism_accounts --stop-after-init
# Tear down (and wipe data)
docker compose -f deploy/docker-compose.yml down -v
```

### 13.2 Troubleshooting
| Symptom | Cause / Fix |
|---|---|
| `-i dubai_tourism` runs "0 tests", module absent | Module not mounted — add to compose volumes + Dockerfile (playbook #15). |
| Docker Hub `403` / rate limit on pull | Use `mirror.gcr.io/library/...` then `docker tag` (see §6 Option A note). |
| `Searching on non-stored field` | Add `store=True` to the computed field (playbook #9). |
| Settings page won't load | Remove `target="inline"`; use `<app>/<block>/<setting>` (playbook #7). |
| Invoice test `AccessError` | Create tourism records with `.sudo()` in the test (playbook #13). |
| `cd: no such file or directory` on your machine | You're not inside the cloned repo folder — `git clone` then `cd real-estate-odoo` first. |

### 13.3 Coordinates
- Our repo / branch: `kazemkhani/real-estate-odoo` @ `claude/workshop-project-portfolio-lpkln6` (PR **#2**).
- Team bench: `Reihaneh-rmz/odoo` @ `19.0` (kazemkhani is collaborator).
- Stack: **Odoo 19.0 · Python 3.12 · PostgreSQL 16**.
- App modules: **`dubai_tourism`** (core) + **`tourism_accounts`** (invoicing bridge).

---

<p align="center"><b>Build it so the demo feels inevitable.</b> Validate everything. Ship nothing unproven.</p>
