from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _action_done(self):
        res = super()._action_done()

        for picking in self:
            if picking.purchase_id:
                line_vals = []
                orderline_ids = picking.purchase_id.order_line
                for line in orderline_ids:
                    line_vals.append((0, 0, {
                        'product_id': line.product_id.product_tmpl_id.id,
                        'quantity': line.product_qty,
                        'rate': line.price_unit,
                    }))

                if not line_vals:
                    return
                self.env['furniture.raw.material.stock'].create({
                    'vendor_id': self.partner_id.id,
                    'purchase_date': fields.Date.context_today(self),
                    'purchase_order_id': self.purchase_id.id,
                    'wood_stock_line': line_vals,
                })
        return res