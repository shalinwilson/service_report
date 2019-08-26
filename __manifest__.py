{
    'name': "KIMS Service Tax Report",
    'author': 'Socius Innovative Global Brains',
    'license': 'AGPL-3',
    'version': '11.0',
    'depends': ['base','sale'],
    'data': ['views/wizard_view.xml',
            'views/report_template.xml',
             'security/ir.model.access.csv',
             ],
    'installable': True,
    'application': True,
    'auto_install': False,
}