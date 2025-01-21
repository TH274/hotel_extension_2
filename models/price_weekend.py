from odoo import models, fields, api, _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class HotelRoomWeekendPricing(models.Model):
    _inherit = 'hotel.room'

    weekend_price = fields.Float(string='Weekend Price', compute='compute_weekend_price', store=True, tracking=True, help="Price per night for weekends (Saturday and Sunday), calculated as 20% more than the base price.")

    @api.depends('price')
    def compute_weekend_price(self):
        """ Computes the weekend price as 20% more than the regular price. """
        for record in self:
            record.weekend_price = record.price * 1.2 if record.price > 0 else 0

    @api.depends('price', 'weekend_price')
    def get_current_price(self):
        """ Computes the effective price based on whether it's a weekend or a weekday. """
        today = fields.Date.context_today(self)
        weekday = today.weekday()
        is_weekend = weekday in (5, 6)

        for record in self:
            if is_weekend:
                record.current_price = record.weekend_price
            else:
                record.current_price = record.price

    current_price = fields.Float(string='Effective Price', compute='get_current_price', store=True, readonly=True)

    @api.model
    def get_effective_price(self, date):
        """ Returns the price for a specific date, considering weekends. """
        weekday = date.weekday()
        is_weekend = weekday in (5, 6)

        self.ensure_one()
        if is_weekend:
            return self.weekend_price
        return self.price
