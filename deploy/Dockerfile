# Self-contained image with the modules baked in — for cloud hosts that build
# from a Dockerfile. Build context must be the REPO ROOT:
#   docker build -f deploy/Dockerfile -t dubai-tourism .
FROM odoo:19

COPY ./dubai_tourism /mnt/extra-addons/dubai_tourism
COPY ./tourism_accounts /mnt/extra-addons/tourism_accounts
COPY ./deploy/odoo.conf /etc/odoo/odoo.conf

EXPOSE 8069
