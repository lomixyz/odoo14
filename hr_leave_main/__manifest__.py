# -*- coding: utf-8 -*-
{
    'name': "Appness HR: Employee Leaves Management",
    'summary': """Employee Leaves Main """,
    'description': """Employee Leaves Main """,
    'author': "Appness Technology",
    'website': "http://www.appness.net",
    'category': 'HR',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': ['base','hr_holidays','hr_payroll'],
    # always loaded
    'data': [
      'security/ir.model.access.csv',
      'views/holidays_inherit.xml',
      'views/public_holiday.xml',
      # 'views/leave_plan.xml',
      # 'views/leave_transfer.xml',
      # 'views/autoallocate.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
   #     'demo.xml',
    ],
}