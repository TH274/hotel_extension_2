from odoo import models, fields, api

class HotelPOSLine(models.Model):
    _name = 'hotel.pos.line'
    _description = 'POS Line for Hotel Customers'

    customer_id = fields.Many2one('hotel.customer', string="Customer", required=True, ondelete='cascade')
    product_id = fields.Many2one(
        'product.product', string="POS Product",
        domain="[('available_in_pos', '=', True)]", required=True,
        help="Select a POS product."
    )
    quantity = fields.Float(string="Quantity", default=1.0, required=True)
    price_unit = fields.Float(string="Unit Price", required=True)
    total_cost = fields.Float(string="Total Cost", compute="_compute_total_cost", store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_total_cost(self):
        for line in self:
            line.total_cost = line.quantity * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.price_unit = line.product_id.lst_price


class HotelCustomer(models.Model):
    _inherit = 'hotel.customer'

    pos_line_ids = fields.One2many(
        'hotel.pos.line', 'customer_id',
        string="POS Products",
        help="List of POS products added to the customer's bill."
    )

    @api.depends('room_id.price', 'check_in_date', 'check_out_date', 'service_line_ids.total_cost', 'pos_line_ids.total_cost')
    def _compute_total_amount(self):
        for record in self:
            total_service_cost = sum(service.total_cost for service in record.service_line_ids)
            total_pos_cost = sum(pos.total_cost for pos in record.pos_line_ids)
            room_cost = 0
            if record.check_in_date and record.check_out_date and record.room_id:
                duration = (record.check_out_date - record.check_in_date).days
                room_cost = duration * record.room_id.price

            record.total_amount = room_cost + total_service_cost + total_pos_cost

class ProductProduct(models.Model):
    _inherit = 'product.product'

    available_in_pos = fields.Boolean(
        string="Available in POS", 
        default=False,
        help="Check this box if the product should be available in POS."
    )