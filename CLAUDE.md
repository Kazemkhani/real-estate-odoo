# CLAUDE.md — operating rules for this repo

**Read [`CAPSTONE.md`](CAPSTONE.md) in full before doing anything.** It is the
single source of truth for the Dubai Tourism ERP capstone (context, alignment to
the case study, run instructions, Odoo 19 playbook, demo script, and the
level‑11 roadmap with task prompts).

## The five rules that matter most
1. **Validate on a real Odoo 19 instance before claiming "done."** Acceptable
   evidence = a test run printing `0 failed, 0 error(s)` **and** a clean
   `--without-demo=False` load. Paste the exact result lines. (See CAPSTONE §6–§7.)
2. **Don't break what works.** Re‑run the module test commands after every change.
3. **Every new behaviour gets a `("post_install","-at_install")` test.**
4. **Mount new modules** in `docker-compose.yml` *and* `deploy/Dockerfile`,
   or `-i` silently installs nothing and tests run on an empty module.
5. **Honor the Odoo 19 playbook** in CAPSTONE §8 (declarative `models.Constraint`,
   `<list>` not `<tree>`, `aggregator=`, `<chatter/>`, settings without
   `target="inline"`, `store=True` before searching a computed field, etc.).

## Project at a glance
- App modules: **`dubai_tourism`** (core) + **`tourism_accounts`** (invoicing bridge).
- Validated on Odoo 19: `dubai_tourism` **31 tests** + `tourism_accounts` **2 tests**, all green; demo loads clean.
- Branch: `claude/workshop-project-portfolio-lpkln6` (repo `kazemkhani/real-estate-odoo`, PR #2).
- Team bench (reference engine, kazemkhani is collaborator): `Reihaneh-rmz/odoo` @ `19.0` — drop the two addon folders into its `addons/`.
- Stack: Odoo 19 · Python 3.12 · PostgreSQL 16. Run with `docker compose -f docker-compose.yml up -d` → http://localhost:8069.

## Workflow per task
`plan → implement → py_compile + XML check → boot Odoo & install with demo →
run module tests → fix → re‑run → commit → push`. Then update CAPSTONE §4
(traceability) and §9 (demo) if scope changed.
