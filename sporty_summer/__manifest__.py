{
    'name': "Sporty Summer DXB",
    'version': '1.0',
    'category': 'Services/Sports',
    'summary': "Sports facility management: court bookings, coaching classes, equipment loans, loyalty",
    'description': """
        Sports Facility Management ERP for Sporty Summer DXB (Summer 2026).

        Centralises court availability and bookings (with double-booking
        prevention and per-sport participant limits), payment tracking that
        gates participation, first-come-first-served coaching-class registration,
        equipment loan / return / loss tracking, and loyalty discounts for
        frequent visitors — plus calendar, kanban and pivot analytics.
    """,
    'depends': ['base', 'mail'],
    # Order matters: security first, then sequences, views (actions) before the
    # menus that reference them, the report, and finally demo data.
    'data': [
        'security/sporty_security.xml',
        'security/ir.model.access.csv',
        'data/sporty_sequence.xml',
        'views/sport_type_views.xml',
        'views/sport_court_views.xml',
        'views/sport_booking_views.xml',
        'views/sport_coaching_class_views.xml',
        'views/sport_class_registration_views.xml',
        'views/sport_equipment_views.xml',
        'views/sport_equipment_loan_views.xml',
        'views/res_partner_views.xml',
        'report/sport_booking_report.xml',
        'views/sporty_menus.xml',
    ],
    'demo': [
        'demo/sporty_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sporty_summer/static/src/scss/sporty.scss',
        ],
    },
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
