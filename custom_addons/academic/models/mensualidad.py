from odoo import models, fields, api

class Mensualidad(models.Model):
    _name = 'academic.payment'
    _description = 'Student Payment'

    student_id = fields.Many2one('academic.student', string='Student', required=True)
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
    date = fields.Date(string='Payment Date', required=True, default=fields.Date.today)
    amount = fields.Float(string='Amount', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('invoiced', 'Invoiced')
    ], string='Status', default='draft')

    def action_create_invoice(self):
        invoice_obj = self.env['account.move']
        invoice_line_obj = self.env['account.move.line']
        
        for payment in self:
            invoice = invoice_obj.create({
                'partner_id': payment.student_id.id,
                'move_type': 'out_invoice',
                'invoice_date': payment.date,
                'invoice_line_ids': [(0, 0, {
                    'name': f'Mensualidad de {payment.student_id.name} del mes {payment.mounth}',
                    'quantity': 1,
                    'price_unit': payment.amount,
                })]
            })
            payment.state = 'invoiced'
