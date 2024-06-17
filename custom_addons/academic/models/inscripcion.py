# models/inscripcion.py
from odoo import models, fields

class Inscripcion(models.Model):
    _name = 'academic.inscripcion'
    _description = 'Modelo de Inscripción'

    student_id = fields.Many2one('academic.student', string='Estudiante', required=True)
    course_id = fields.Many2one('academic.curso', string='Curso', required=True)
    cycle = fields.Integer(string='Ciclo', required=True)
    enrollment_date = fields.Date(string='Fecha de Inscripción', default=fields.Date.today)
