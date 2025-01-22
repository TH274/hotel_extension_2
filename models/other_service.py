from odoo import models, fields, api, _

class HotelCustomer(models.Model):
    _inherit = 'hotel.customer'

    other_service_line_ids = fields.One2many(
        'other.hotel.service.line', 'customer_id', string="Services Availed",
        help="List of services availed by the customer."
    )

class HotelServiceLine(models.Model):
    _name = 'other.hotel.service.line'
    _description = 'Service Line for Hotel Customers (Service Products)'

    customer_id = fields.Many2one(
        'hotel.customer',
        string="Customer",
        required=True,
        ondelete='cascade',
        help="The customer who availed the service."
    )
    product_id = fields.Many2one(
        'product.product',
        string="Service Product",
        domain="[('detailed_type', '=', 'service')]",
        required=True,
        help="Select an existing service product."
    )
    description = fields.Char(string="Description")
    quantity = fields.Float(string="duration", default=1.0, required=True)
    price_unit = fields.Float(string="Unit Price")
    total_cost = fields.Float(string="Total Cost", compute="_compute_total_cost", store=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.description = line.product_id.description_sale or line.product_id.name
                line.price_unit = line.product_id.lst_price

    @api.depends('quantity', 'price_unit')
    def _compute_total_cost(self):
        for line in self:
            line.total_cost = line.quantity * line.price_unit

