# models/boletin.py
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Boletin(models.Model):
    _name = 'academic.boletin'
    _description = 'Boletines de la escuela'

    curso_id = fields.Many2one('academic.curso', string='Curso', required=True)
    nro_bimestre = fields.Integer(string='Nro Bimestre', required=True)
    student_id = fields.Many2one('academic.student', string='Estudiante')
    fecha = fields.Date(string='Fecha', default=fields.Date.today)
    nota_ids = fields.One2many('academic.nota', 'boletin_id', string='Notas', order='materia_id')
    nota_total = fields.Float(string='Nota Total', compute='_compute_nota_total', store=True)

    @api.depends('nota_ids.nota')
    def _compute_nota_total(self): 
        try:
            for boletin in self:
                notas = boletin.nota_ids
                if len(notas) > 0:
                    total = sum(nota.nota for nota in notas)
                    boletin.nota_total = total / len(notas)
                    if boletin.nota_total < 1:
                        raise ValidationError(_('Agregue las notas'))
                else:
                    boletin.nota_total = 0.0
        except ZeroDivisionError:
            self.nota_total = 0.0

    def action_generate_boletin(self):
        for record in self:
            nota = self.env['academic.nota'].search([
                ('curso_id', '=', record.curso_id.id),
                ('student_id', '=', record.student_id.id),
                ('nro_bimestre', '=', record.nro_bimestre)
            ])
            record.nota_ids = [(6, 0, nota.ids)]