# models/curso.py
from odoo import models, fields

class Curso(models.Model):
    _name = 'academic.curso'
    _description = 'Cursos de la escuela'

    name = fields.Char(string='Nombre del Curso', required=True)
    student_ids = fields.One2many('academic.student', 'curso_id', string='Estudiantes')
    materia_ids = fields.Many2many('academic.materia', 'curso_materia', 'curso_id', 'materia_id', string='Materias')
    inscription_ids = fields.One2many('academic.inscripcion', 'course_id', string='Inscripciones')
    report_ids = fields.One2many('academic.report.payment', 'curso_id', string='Reportes de Pagos')