# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Academic System',
    'author' : 'Group 10',
    'version': '1.0',
    'category': 'Education',
    'summary': 'Manage academic administration',
    'description': """
        Module to manage academic administration of a school.
    """,
    'depends' : ['mail', 'account', 'base', 'hr', 'web'],
    'data' : [
        'views/menu.xml',
        'views/student.xml',
        'views/apoderado.xml',
        'views/aula.xml',
        'views/curso_materia.xml',
        'views/curso.xml',
        'views/materia.xml',
        'views/nota.xml',
        'views/mensualidad.xml',
        'views/inscripcion.xml',
        'report/report_boletin.xml',
        'report/report_libreta.xml',
        'report/report_payment.xml',
        'views/libreta.xml',
        'views/boletin.xml',
        'views/report_payment.xml',
        'data/curso.xml',
        'data/materia.xml',
        'data/profesor.xml',
        
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True
}
