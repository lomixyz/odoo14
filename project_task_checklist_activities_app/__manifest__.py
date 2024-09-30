# -*- coding: utf-8 -*-

{
    'name' : 'Project Task Checklist Activity App',
    'author': "Edge Technologies",
    'version' : '14.0.1.0',
    'live_test_url':'https://youtu.be/TBLyevM228A',
    "images":['static/description/main_screenshot.png'],
    'summary' : 'App create task checklist activities project subtask checklist activities project task checklist activities project checklist activities project tasks checklist activity project subtask checklist activity project task checklist activity project checklist',
    'description' : """This app helps to create task checklist and checklist activities.
    """,
    'depends' : ['base','project'],
    "license" : "OPL-1",
    'data': [
        'security/ir.model.access.csv',
        'security/task_subtask_checklist_security.xml',
        'views/alltask_activity.xml',
        'views/project_task_type_view.xml',
        'views/checklist_activity_stage.xml',
        'views/task_checklist_view.xml',
        'views/project_task_view.xml',
        'views/project_project_view.xml',
        'views/res_config_settings_view.xml',
        'wizard/approve_reject.xml',
        'data/task_subtask_checklist_data.xml',],
    'installable' : True,
    'auto_install' : False,
    'price': 7,
    'currency': "EUR",
    'category' : 'Project',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
