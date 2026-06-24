# Self-contained image with the custom modules baked in — used by cloud hosts
# that build from a Dockerfile (a VM, Railway, Render, Fly.io, etc.).
#
# Build context must be the REPO ROOT, e.g.:
#   docker build -f deploy/Dockerfile -t sporty-odoo .
FROM odoo:19

# Copy the three custom modules onto Odoo's extra-addons path.
COPY ./estate /mnt/extra-addons/estate
COPY ./estate_accounts /mnt/extra-addons/estate_accounts
COPY ./sporty_summer /mnt/extra-addons/sporty_summer
COPY ./dubai_tourism /mnt/extra-addons/dubai_tourism
COPY ./deploy/odoo.conf /etc/odoo/odoo.conf

# Odoo serves HTTP on 8069 (and 8072 for longpolling).
EXPOSE 8069
