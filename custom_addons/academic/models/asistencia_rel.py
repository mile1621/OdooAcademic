from odoo import models, fields

class AsistenciaRel(models.Model):
    _name = 'academic.asistencia.rel'
    _description = 'Relación de Asistencia'
    _rec_name = 'student_id'

    lista_id = fields.Many2one('academic.lista.asistencia', string='Lista de Asistencia', required=True, ondelete='cascade')
    student_id = fields.Many2one('academic.student', string='Estudiante', required=True, ondelete='cascade')
    estado = fields.Selection([
        ('Presente', 'Presente'),
        ('Falta', 'Falta'),
        ('Tarde', 'Tarde')
    ], string='Estado', required=True)
    observacion = fields.Text(string='Observación')