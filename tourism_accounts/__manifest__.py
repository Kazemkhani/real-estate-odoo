{
    'name': "Tourism Accounts",
    'version': '1.0',
    'category': 'Services/Tourism',
    'summary': "Bills the customer when a tour booking is paid (links Dubai Tourism to Invoicing)",
    # Depends on 'account' so we can raise customer invoices (account.move).
    'depends': ['dubai_tourism', 'account'],
    'data': [
        'views/tourism_booking_views.xml',
    ],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
