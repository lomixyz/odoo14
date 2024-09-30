# -*- encoding: utf-8 -*-
{
    'name' : 'SW - HR Payroll Enhancement',
    'version' : '13.0.1.0',
    'category' : 'Human Resources',
    'author' : 'Smart Way Business Solutions',
    'website' : 'https://www.smartway.co',
    'license' : 'Other proprietary',
    'summary' : 'Enhancement on Payroll Workflow',
    'description': """
        - In payslip page, we make some enhancement on the workflow:
        - On confirmation, in Salary Computation page we have changed the name of Net Salary rule to Net For [employee name].
        - Refunded Slip.
        - Prevent compute slip on refunding.
        - Make salary structure and salary journal fields company dependent.
        - Add chatter to payslip for tracking the changes of status.
        - Add record rules for payslip, payslips batches and salary structure.
        - Add new field company in payslip batches object.
        - Add record rules on hr.employee and hr.contract.
        """,
    'data': [
            'view/hr_payslip.xml',
            'security/rules.xml'
            ],
    'depends' : ['base', 'hr_payroll_account_community', 'hr_payroll_community'],
    'installable': True,
    'auto_install': False,
}
