# models/curso.py
from odoo import api, models, fields

class CursoMateria(models.Model):
    _name = 'academic.curso.materia'
    _description = 'Asignacion de materia y curso'

    curso_id = fields.Many2one('academic.curso', string='Curso')
    materia_id = fields.Many2one('academic.materia', string='Materia')
    name = fields.Char(compute="_compute_name")
    profesor_id = fields.Many2one('hr.employee', string='Profesor')
    schedule = fields.Text(string='Horario')
    aula_id = fields.Many2one('academic.aula', string='Aula')

    @api.depends('curso_id', 'materia_id')
    def _compute_name(self):
        for rec in self:
            rec.name = str(rec.curso_id.name) +" "+ str(rec.materia_id.name)
