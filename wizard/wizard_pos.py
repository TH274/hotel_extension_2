from odoo import models, fields, api, exceptions, _
from datetime import datetime
import logging

class AddPOSProductWizard(models.TransientModel):
    _name = 'add.pos.product.wizard'
    _description = 'Add POS Product Wizard'

    customer_id = fields.Many2one('hotel.customer', string="Customer", required=True)
    product_id = fields.Many2one(
        'product.product', string="POS Product",
        domain="[('available_in_pos', '=', True)]", required=True
    )
    quantity = fields.Float(string="Quantity", default=1.0, required=True)

    def add_product(self):
        if self.customer_id and self.product_id:
            self.env['hotel.pos.line'].create({
                'customer_id': self.customer_id.id,
                'product_id': self.product_id.id,
                'quantity': self.quantity,
                'price_unit': self.product_id.lst_price,
            })

class HotelCustomer(models.Model):
    _inherit = 'hotel.customer'

    def action_add_pos_product(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add POS Product',
            'res_model': 'add.pos.product.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_customer_id': self.id},
        }