from odoo import models, fields, api, exceptions, _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class HotelCheckoutWizardEnhanced(models.TransientModel):
    _name = 'hotel.checkout.wizard.enhanced'
    _description = 'Enhanced Hotel Checkout Wizard'

    booking_id = fields.Many2one('hotel.customer', string='Booking', required=True, readonly=True)
    hotel_id = fields.Many2one('hotel.hotel', string='Hotel', readonly=True)
    room_id = fields.Many2one('hotel.room', string='Room', readonly=True)
    payment_amount = fields.Float(string='Total Payment Amount', required=True)

    @api.constrains('payment_amount')
    def _check_payment_amount(self):
        for record in self:
            if record.payment_amount <= 0:
                raise exceptions.ValidationError(_('Payment amount must be greater than 0.'))

    def action_confirm_checkout(self):
        booking = self.booking_id

        # Retrieve or create sale order linked to the booking
        sale_order = self.env['sale.order'].search([('origin', '=', booking.booking_code)], limit=1)
        if not sale_order:
            raise exceptions.ValidationError(_('No quotation found for this booking.'))

        # Organize existing order lines by product for easy updating
        existing_product_lines = {line.product_id.id: line for line in sale_order.order_line}
        new_order_lines = []

        # Process main service lines
        for service in booking.service_line_ids:
            if service.product_id:
                self._process_service_line(service, existing_product_lines, new_order_lines)

        # Process additional service lines
        for other_service in booking.other_service_line_ids:
            if other_service.product_id:
                self._process_service_line(other_service, existing_product_lines, new_order_lines)

        # Add new lines to the sale order
        if new_order_lines:
            sale_order.write({'order_line': new_order_lines})
            _logger.info('Added new services to quotation during checkout for booking %s', booking.booking_code)

        # Update booking and room status
        booking.write({
            'payment_status': 'paid',
            'payment_date': datetime.now(),
            'payment_amount': self.payment_amount,
            'status': 'done',
        })

        if booking.room_id:
            booking.room_id.write({'status': 'available'})

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Payment successfully completed, quotation updated, and the booking is checked out.',
                'type': 'rainbow_man',
            },
            'type': 'ir.actions.act_window_close',
        }

    def _process_service_line(self, service, existing_product_lines, new_order_lines):
        product_id = service.product_id.id
        quantity = service.quantity
        if product_id in existing_product_lines:
            line = existing_product_lines[product_id]
            line.write({
                'product_uom_qty': line.product_uom_qty + quantity,
            })
        else:
            new_order_lines.append((0, 0, {
                'product_id': product_id,
                'product_uom_qty': quantity,
                'price_unit': service.product_id.lst_price,
                'name': service.description or service.product_id.name,
            }))
