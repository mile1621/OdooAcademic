# models/lista_asistencia.py
from odoo import models, fields

class ListaAsistencia(models.Model):
    _name = 'academic.lista.asistencia'
    _description = 'Lista de Asistencia'

    fecha = fields.Date(string='Fecha', required=True, default=fields.Date.today)
    curso_id = fields.Many2one('academic.curso', string='Curso', required=True)
    student_ids = fields.Many2many('academic.student', 'asistencia_rel', 'lista_id', 'student_id', string='Estudiantes', 
        help="Estudiantes que forman parte de esta lista de asistencia", 
        context="{'default_state': 'present'}")