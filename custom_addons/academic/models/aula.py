# models/aula.py
from odoo import models, fields

class Aula(models.Model):
    _name = 'academic.aula'
    _description = 'Aulas de la escuela'

    name = fields.Char(string='Numero de Aula', required=True)
    curso_materia_ids = fields.One2many('academic.curso.materia', 'aula_id', string='Cursos Materias')