# models/estudiante.py
from odoo import models, fields, api

class Student(models.Model):
    _name = 'academic.student'
    _description = 'Modelo de Estudiantes'

    name = fields.Char(string='Nombre', required=True)
    enrollment_number = fields.Char(string='Número de Matrícula', required=True, unique=True)
    birth_date = fields.Date(string='Fecha de Nacimiento')
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro')
    ], string='Género')
    address = fields.Text(string='Dirección')
    phone = fields.Char(string='Teléfono')
    email = fields.Char(string='Correo Electrónico')
    curso_id = fields.Many2one('academic.curso', string='Curso')
    apoderado_ids = fields.Many2many('academic.apoderado', string='Apoderados')
    nota_ids = fields.One2many('academic.nota', 'student_id', string='Notas')
    user_id = fields.Many2one('res.users', string='Usuario')
    inscription_ids = fields.One2many('academic.inscripcion', 'student_id', string='Inscripciones')
    report_line_ids = fields.One2many('academic.report.payment.line', 'student_id', string='Reportes de Pagos')
    notice_ids = fields.Many2many('academic.notice', string='Notices')
    attendance_ids = fields.Many2many('academic.lista.asistencia', 'academic_asistencia_rel', 'student_id', 'lista_id', string='Asistencias')

    @api.model
    def create(self, vals):
        # Primero, creamos el estudiante
        student = super().create(vals)

        # Luego, creamos un usuario para el estudiante, pero sólo si se proporcionó un correo electrónico
        if student.email:
            # Verificamos si ya existe un usuario con el mismo correo electrónico
            user = self.env['res.users'].sudo().search([('login', '=', student.email)], limit=1)
            if not user:
                # Si no existe, creamos un nuevo usuario
                user = self.env['res.users'].create({
                    'name': student.name,
                    'login': student.email,
                    'password': 'password',  # Deberías generar o pedir una contraseña segura
                    'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],  # Asigna al grupo de portal
                })

            # Asignamos el usuario al estudiante
            student.user_id = user

        return student

    def write(self, vals):
        # Primero, actualizamos el estudiante
        super().write(vals)

        # Luego, si se proporcionó un correo electrónico y el estudiante no tiene un usuario asociado,
        # creamos un usuario para el estudiante
        if self.email and not self.user_id:
            # Verificamos si ya existe un usuario con el mismo correo electrónico
            user = self.env['res.users'].sudo().search([('login', '=', self.email)], limit=1)
            if not user:
                # Si no existe, creamos un nuevo usuario
                user = self.env['res.users'].create({
                    'name': self.name,
                    'login': self.email,
                    'password': 'password',  # Deberías generar o pedir una contraseña segura
                    'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],  # Asigna al grupo de portal
                })

            # Asignamos el usuario al estudiante
            self.user_id = user

        return True
