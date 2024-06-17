# models/apoderado.py
from odoo import api, models, fields

class Apoderado(models.Model):
    _name = 'academic.apoderado'
    _description = 'Modelo de Padres o Apoderados'

    name = fields.Char(string='Nombre', required=True)
    birth_date = fields.Date(string='Fecha de Nacimiento')
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro')
    ], string='Género')
    address = fields.Text(string='Dirección')
    phone = fields.Char(string='Teléfono')
    email = fields.Char(string='Correo Electrónico')
    student_ids = fields.Many2many('academic.student', string='Hijos')
    user_id = fields.Many2one('res.users', string='Usuario')
    notice_ids = fields.Many2many('academic.notice', string='Notices')

    @api.model
    def create(self, vals):
        # Primero, creamos el apoderado
        apoderado = super().create(vals)

        # Luego, creamos un usuario para el apoderado, pero sólo si se proporcionó un correo electrónico
        if apoderado.email:
            # Verificamos si ya existe un usuario con el mismo correo electrónico
            user = self.env['res.users'].sudo().search([('login', '=', apoderado.email)], limit=1)
            if not user:
                # Si no existe, creamos un nuevo usuario
                user = self.env['res.users'].create({
                    'name': apoderado.name,
                    'login': apoderado.email,
                    'password': 'password',  # Deberías generar o pedir una contraseña segura
                    'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],  # Asigna al grupo de usuarios que corresponda
                })

            # Asignamos el usuario al apoderado
            apoderado.user_id = user

        return apoderado

    def write(self, vals):
        # Primero, actualizamos el apoderado
        super().write(vals)

        # Luego, si se proporcionó un correo electrónico y el apoderado no tiene un usuario asociado,
        # creamos un usuario para el apoderado
        if self.email and not self.user_id:
            # Verificamos si ya existe un usuario con el mismo correo electrónico
            user = self.env['res.users'].sudo().search([('login', '=', self.email)], limit=1)
            if not user:
                # Si no existe, creamos un nuevo usuario
                user = self.env['res.users'].create({
                    'name': self.name,
                    'login': self.email,
                    'password': 'password',  # Deberías generar o pedir una contraseña segura
                    'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],  # Asigna al grupo de usuarios internos
                })

            # Asignamos el usuario al apoderado
            self.user_id = user

        return True
