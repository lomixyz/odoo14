# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Gym Management',
    'version': '14.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Tools',
    'description':
        """
        This Module add below functionality into odoo

        1.Gym Management\n

odoo app allow Gym Management easily with Membership, Trainer, Gym Management, gym Trainer, Gym member, GYM Session, workout plan, gym Exercises, Diet plan, member activity, membership invoice Attendance

    """,
    'summary': 'odoo app allow Gym Management easily with Membership, Trainer, Gym Management, gym Trainer, Gym member, GYM Session, workout plan, gym Exercises, Diet plan, member activity, membership invoice Attendance',
    'depends': ['account', 'hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/session_arranged_template.xml',
        'data/session_canceled_template.xml',
        'views/main_menus_view.xml',
        'views/trainer_skill_view.xml',
        'views/body_part_view.xml',
        'views/gym_equipment_view.xml',
        'views/workout_day_view.xml',
        'views/member_sequence_view.xml',
        'views/trainer_sequence_view.xml',
        'views/exercise_view.xml',
        'views/workout_plan_view.xml',
        'views/diet_food_view.xml',
        'views/consume_at_view.xml',
        'views/diet_plan_view.xml',
        'views/membership_view.xml',
        'views/trainer_view.xml',
        'views/member_view.xml',
        'wizard/assign_diet_view.xml',
        'wizard/assign_diet_member_view.xml',
        'wizard/assign_workout_view.xml',
        'wizard/assign_workout_member_view.xml',
        'views/gym_activity_view.xml',
        'views/member_attendance_view.xml',
        'views/trainer_attendance_view.xml',
        'wizard/session_cancel_view.xml',
        'views/special_session_view.xml',
        'report/member_card_template.xml',
        'report/member_card_menu.xml',
        'report/trainer_card_template.xml',
        'report/trainer_card_menu.xml',
        'report/member_analysis_view.xml',
        'report/member_pdf_template.xml',
        'report/member_pdf_menu.xml',
        'report/trainer_pdf_template.xml',
        'report/trainer_pdf_menu.xml',
        'report/diet_plan_pdf_template.xml',
        'report/diet_plan_pdf_menu.xml',
        'report/workout_plan_pdf_template.xml',
        'report/workout_plan_pdf_menu.xml',
        'report/gym_exercise_pdf_template.xml',
        'report/gym_exercise_pdf_menu.xml',
        'report/attendance_report_template.xml',
        'report/attendance_report_menu.xml',
        'wizard/attendance_report_window_views.xml',
        'report/activity_report_template.xml',
        'report/activity_report_menu.xml',
        'wizard/activity_report_window_views.xml',
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':39.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
