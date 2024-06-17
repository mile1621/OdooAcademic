from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ReportePagos(models.TransientModel):
    _name = 'academic.report.payment'
    _description = 'Reporte de Pagos por Curso y Mes'

    curso_id = fields.Many2one('academic.curso', string='Curso')
    cycle = fields.Integer(string='Ciclo', required=True)
    mounth = fields.Selection([
        ('2', 'Febrero'),
        ('3', 'Marzo'),
        ('4', 'Abril'),
        ('5', 'Mayo'),
        ('6', 'Junio'),
        ('7', 'Julio'),
        ('8', 'Augosto'),
        ('9', 'Septiembre'),
        ('10', 'Octubre'),
        ('11', 'Noviembre')
        ], string='Mes', required=True)
    student_ids = fields.One2many('academic.report.payment.line', 'reporte_id', string='Alumnos')

    @api.onchange('curso_id', 'cycle', 'mounth')
    def _compute_students(self):
        if self.curso_id and self.cycle and self.mounth:
            # Búsqueda de inscripciones
            inscripciones = self.env['academic.inscripcion'].search([
                ('course_id', '=', self.curso_id.id),
                ('cycle', '=', self.cycle)
            ])
            estudiantes = inscripciones.mapped('student_id')

            # Mensaje de depuración
            _logger.debug('Inscripciones encontradas: %s', inscripciones)
            _logger.debug('Estudiantes encontrados: %s', estudiantes)

            # Búsqueda de pagos
            pagos = self.env['academic.payment'].search([
                ('student_id', 'in', estudiantes.ids),
                ('cycle', '=', self.cycle),
                ('mounth', '=', self.mounth)
            ])
            pagos_dict = {pago.student_id.id: True for pago in pagos}

            # Mensaje de depuración
            _logger.debug('Pagos encontrados: %s', pagos)
            _logger.debug('Pagos dict: %s', pagos_dict)

            estudiantes_lines = []
            for estudiante in estudiantes:
                estudiantes_lines.append((0, 0, {
                    'student_id': estudiante.id,
                    'has_paid': pagos_dict.get(estudiante.id, False),
                }))

            # Mensaje de depuración
            _logger.debug('Líneas de estudiantes: %s', estudiantes_lines)

            self.student_ids = estudiantes_lines


class ReportePagosLine(models.TransientModel):
    _name = 'academic.report.payment.line'
    _description = 'Líneas de Reporte de Pagos por Curso y Mes'

    reporte_id = fields.Many2one('academic.report.payment', string='Reporte')
    student_id = fields.Many2one('academic.student', string='Alumno')
    has_paid = fields.Boolean(string='Ha pagado')
