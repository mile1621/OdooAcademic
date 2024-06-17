# models/nota.py
from odoo import models, fields

class Nota(models.Model):
    _name = 'academic.nota'
    _description = 'Notas de la escuela'

    curso_id = fields.Many2one('academic.curso', string='Curso', required=True)
    materia_id = fields.Many2one('academic.materia', string='Materia', required=True)
    nro_bimestre = fields.Integer(string='Nro Bimestre', required=True)
    student_id = fields.Many2one('academic.student', string='Estudiante', required=True)
    nota = fields.Float(string='Nota', required=True)
    boletin_id = fields.Many2one('academic.boletin', string='Boletin')
    libreta_id = fields.Many2one('academic.libreta', string='Libreta')