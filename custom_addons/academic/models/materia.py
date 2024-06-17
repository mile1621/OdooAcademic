# models/materia.py
from odoo import models, fields

class Materia(models.Model):
    _name = 'academic.materia'
    _description = 'Materias de la escuela'

    name = fields.Char(string='Nombre de la Materia', required=True)
    course_ids = fields.Many2many('academic.curso', 'curso_materia', 'materia_id', 'curso_id', string='Cursos')
