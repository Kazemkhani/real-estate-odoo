{
    'name': "Dubai Tourism",
    'version': '1.0',
    'category': 'Services/Tourism',
    'summary': "Tourism agency ERP: tour packages, bookings, transport, commissions, analytics",
    'description': """
Tourism Management ERP for a Dubai tour agency.

Centralises tour package management, customer bookings (with family and group
discounts), internal fleet plus third-party taxi coordination and the commission
the agency earns on it, payment tracking, customer reviews, and booking/revenue
analytics.
""",
    'depends': ['base', 'mail', 'portal'],
    'data': [
        'security/tourism_security.xml',
        'security/ir.model.access.csv',
        'data/tourism_sequence.xml',
        'data/mail_templates.xml',
        'data/tourism_cron.xml',
        'views/tourism_destination_views.xml',
        'views/tourism_tour_package_views.xml',
        'views/tourism_departure_views.xml',
        'views/tourism_booking_views.xml',
        'views/tourism_vehicle_views.xml',
        'views/tourism_transport_assignment_views.xml',
        'views/tourism_review_views.xml',
        'views/res_partner_views.xml',
        'views/tourism_assign_transport_wizard_views.xml',
        'views/res_config_settings_views.xml',
        'views/portal_templates.xml',
        'report/tourism_booking_report.xml',
        'views/tourism_menus.xml',
    ],
    'demo': [
        'demo/tourism_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dubai_tourism/static/src/scss/tourism.scss',
        ],
    },
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
