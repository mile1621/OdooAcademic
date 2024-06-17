# models/libreta.py
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Libreta(models.Model):
    _name = 'academic.libreta'
    _description = 'Libretas de la escuela'

    name = fields.Char(compute="_compute_name")
    curso_id = fields.Many2one('academic.curso', string='Curso', required=True)
    student_id = fields.Many2one('academic.student', string='Estudiante')
    fecha = fields.Date(string='Fecha', default=fields.Date.today)
    nota_ids = fields.One2many('academic.nota', 'libreta_id', string='Notas', order='nro_bimestre, materia_id')
    nota_total = fields.Float(string='Nota Total', compute='_compute_nota_total')

    @api.depends('nota_ids.nota')
    def _compute_nota_total(self): 
        try:
            for libreta in self:
                notas = libreta.nota_ids
                if len(notas) > 0:
                    total = sum(nota.nota for nota in notas)
                    libreta.nota_total = total / len(notas)
                    if libreta.nota_total < 1:
                        raise ValidationError(_('Agregue las notas'))
                else:
                    libreta.nota_total = 0.0
        except ZeroDivisionError:
            self.nota_total = 0.0

    def action_generate_libreta(self):
        for record in self:
            nota = self.env['academic.nota'].search([
                ('curso_id', '=', record.curso_id.id),
                ('student_id', '=', record.student_id.id),
            ])
            record.nota_ids = [(6, 0, nota.ids)]

    @api.depends('curso_id', 'student_id')
    def _compute_name(self):
        for rec in self:
            rec.name = "Libreta de " + str(rec.student_id.name) +" - "+ str(rec.curso_id.name)

    def get_notas_por_bimestre_y_materia(self):
        data = {}
        for nota in self.nota_ids:
            materia = nota.materia_id.name
            bimestre = nota.nro_bimestre
            if materia not in data:
                data[materia] = {}
            data[materia][bimestre] = nota.nota
        return data