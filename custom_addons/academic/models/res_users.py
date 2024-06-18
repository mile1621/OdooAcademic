from odoo import api, fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    fcm_token = fields.Char(string="FCM Token")