from odoo import models, fields, api, exceptions, _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class HotelCheckoutWizard(models.TransientModel):
    _inherit = 'hotel.checkout.wizard'

    def action_confirm_checkout(self):
        """ Override the original method to include other_service_line_ids """
        booking = self.booking_id

        # Find the associated sale order
        sale_order = self.env['sale.order'].search([('origin', '=', booking.booking_code)], limit=1)
        if not sale_order:
            raise exceptions.ValidationError(_('No quotation found for this booking.'))

        existing_product_lines = {line.product_id.id: line for line in sale_order.order_line}
        new_order_lines = []

        # Process standard service lines
        for service in booking.service_line_ids:
            if service.product_id:
                self._update_sale_order_lines(service, existing_product_lines, new_order_lines)

        # Process other service lines if present (from extension module)
        if hasattr(booking, 'other_service_line_ids'):
            for other_service in booking.other_service_line_ids:
                if other_service.product_id:
                    self._update_sale_order_lines(other_service, existing_product_lines, new_order_lines)

        # Add new lines to the sale order
        if new_order_lines:
            sale_order.write({'order_line': new_order_lines})
            _logger.info('Added new services to quotation for booking %s', booking.booking_code)

        # Update booking status and payment info
        booking.write({
            'payment_status': 'paid',
            'payment_date': datetime.now(),
            'payment_amount': self.payment_amount,
            'status': 'done',
        })

        # Set room back to available
        if booking.room_id:
            booking.room_id.status = 'available'

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Payment completed, quotation updated, and booking checked out.',
                'type': 'rainbow_man',
            },
            'type': 'ir.actions.act_window_close',
        }

    def _update_sale_order_lines(self, service_line, existing_lines, new_lines):
        product_id = service_line.product_id.id
        quantity = service_line.quantity
        if product_id in existing_lines:
            line = existing_lines[product_id]
            line.write({'product_uom_qty': line.product_uom_qty + quantity}) 
        else:
            new_lines.append((0, 0, {
                'product_id': product_id,
                'product_uom_qty': quantity,
                'price_unit': service_line.product_id.lst_price,
                'name': service_line.product_id.name,
            }))