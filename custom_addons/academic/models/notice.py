from odoo import api, models, fields

class Notice(models.Model):
    _name = 'academic.notice'
    _description = 'Academic Notice'

    title = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    curso_materia_id = fields.Many2one('academic.curso.materia', string='Curso Materia', required=True)
    fecha_inicio = fields.Date(string="Start Date")
    fecha_fin = fields.Date(string="End Date")
    student_ids = fields.Many2many('academic.student', string='Students')
    apoderado_ids = fields.Many2many('academic.apoderado', string='Apoderados')

    profesor = fields.Char(string="Profesor", compute='_compute_profesor', store=True)
    curso = fields.Char(string="Curso", compute='_compute_curso', store=True)
    materia = fields.Char(string="Materia", compute='_compute_materia', store=True)

    @api.depends('curso_materia_id')
    def _compute_profesor(self):
        for record in self:
            record.profesor = record.curso_materia_id.profesor_id.name if record.curso_materia_id.profesor_id else ''

    @api.depends('curso_materia_id')
    def _compute_curso(self):
        for record in self:
            record.curso = record.curso_materia_id.curso_id.name if record.curso_materia_id.curso_id else ''

    @api.depends('curso_materia_id')
    def _compute_materia(self):
        for record in self:
            record.materia = record.curso_materia_id.materia_id.name if record.curso_materia_id.materia_id else ''

