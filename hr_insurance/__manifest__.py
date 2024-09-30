# -*- coding: utf-8 -*-

{
    'name': 'WAY HR: Employee Insurance',
    'summary': """Employee Insurance Management for WAY HR.""",
    'description': """Manages insurance amounts for employees to be deducted from salary""",
    'category': 'HR',
    'version': '14.0.1',
    'sequence': 15,
    'author': 'WAY For IST',
    'maintainer': 'WAY For IST',
    'company': 'WAY For IST',
    'website': 'https://www.w-ist.com',
    'depends': ['base', 'hr', 'hr_payroll',],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_insurance_security.xml',
        'views/employee_insurance_view.xml',
        'views/insurance_salary_stucture.xml',
        'views/policy_management.xml',
              ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
