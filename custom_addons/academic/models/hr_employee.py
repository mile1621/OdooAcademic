from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # profesor_id = fields.Many2one('academic.profesor', string='Profesor')
    # area_especializacion = fields.Char(string='Área de Especialización')
    curso_materia_ids = fields.One2many('academic.curso.materia', 'profesor_id', string='Cursos Materias')
    
    user_id = fields.Many2one('res.users', string='Usuario')

    @api.model
    def create(self, vals):
        # Primero, creamos el empleado
        employee = super().create(vals)

        # Luego, creamos un usuario para el empleado, pero sólo si se proporcionó un correo electrónico
        if employee.work_email:
            # Verificamos si ya existe un usuario con el mismo correo electrónico
            user = self.env['res.users'].sudo().search([('login', '=', employee.work_email)], limit=1)
            if not user:
                # Si no existe, creamos un nuevo usuario
                user = self.env['res.users'].create({
                    'name': employee.name,
                    'login': employee.work_email,
                    'password': 'password',  # Deberías generar o pedir una contraseña segura
                    'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],  # Asigna al grupo de usuarios internos
                })

            # Asignamos el usuario al empleado
            employee.user_id = user

        return employee

    def write(self, vals):
        # Primero, actualizamos el empleado
        super().write(vals)

        # Luego, si se proporcionó un correo electrónico y el empleado no tiene un usuario asociado,
        # creamos un usuario para el empleado
        if self.work_email and not self.user_id:
            # Verificamos si ya existe un usuario con el mismo correo electrónico
            user = self.env['res.users'].sudo().search([('login', '=', self.work_email)], limit=1)
            if not user:
                # Si no existe, creamos un nuevo usuario
                user = self.env['res.users'].create({
                    'name': self.name,
                    'login': self.work_email,
                    'password': 'password',  # Deberías generar o pedir una contraseña segura
                    'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],  # Asigna al grupo de usuarios internos
                })

            # Asignamos el usuario al empleado
            self.user_id = user

        return True