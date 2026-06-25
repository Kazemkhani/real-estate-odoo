from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class TourismPortal(CustomerPortal):
    """Self-service portal: a logged-in customer can see their own tour bookings."""

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "tour_booking_count" in counters:
            partner = request.env.user.partner_id
            values["tour_booking_count"] = request.env["tourism.booking"].search_count(
                [("customer_id", "=", partner.id)]
            )
        return values

    @http.route(["/my/tours", "/my/tours/page/<int:page>"], type="http", auth="user", website=True)
    def portal_my_tours(self, page=1, **kw):
        partner = request.env.user.partner_id
        Booking = request.env["tourism.booking"]
        domain = [("customer_id", "=", partner.id)]
        total = Booking.search_count(domain)
        pager = portal_pager(url="/my/tours", total=total, page=page, step=10)
        bookings = Booking.search(domain, limit=10, offset=pager["offset"], order="departure_date desc")
        values = {
            "bookings": bookings.sudo(),  # sudo only for rendering related fields
            "pager": pager,
            "page_name": "tour_booking",
            "default_url": "/my/tours",
        }
        return request.render("dubai_tourism.portal_my_tours", values)

    @http.route(["/my/tours/<int:booking_id>"], type="http", auth="user", website=True)
    def portal_my_tour(self, booking_id, access_token=None, **kw):
        try:
            booking_sudo = self._document_check_access("tourism.booking", booking_id, access_token)
        except (AccessError, MissingError):
            return request.redirect("/my")
        return request.render("dubai_tourism.portal_my_tour", {
            "booking": booking_sudo,
            "page_name": "tour_booking",
        })
