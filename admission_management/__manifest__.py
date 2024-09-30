# -*- coding: utf-8 -*-
{
    'name': "Admission_Management",

    'summary': """
       module to manage Admissions (contract and Rent workers) """,

    'description': """
        module to manage Admissions (contract and Rent workers) 
    """,

    'author': "Eng. Ibrahim Omer Ibrahim",
    'website': "www.linkedin.com/in/ibrahim-omer-b75091178",

    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'price': 533, 
    'currency': 'USD',
    # any module necessary for this one to work correctly
    'depends': ['base','mail','hr_expense','hr','website'],

    # always loaded
    'data': [
        'data/ir_sequence_data.xml',
        'data/rent_scheduler.xml',
        'views/views.xml',
        'views/workers_details_page.xml',
        #'views/admission_report.xml',
        'views/report_template.xml',

        'security/ir.model.access.csv',
        'reports/admission_contract_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}