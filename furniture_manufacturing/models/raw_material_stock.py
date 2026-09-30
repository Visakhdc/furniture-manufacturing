from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RawMaterialStock(models.Model):
    _name = 'furniture.raw.material.stock'
    _description = 'Raw Material (Timber) Stock'
    _rec_name = 'name'

    # ---------------------------------------------------------------
    # Identification
    # ---------------------------------------------------------------
    name = fields.Char(
        string='Reference', required=True, copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'furniture.raw.material.stock') or 'New')

    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company)

    # ---------------------------------------------------------------
    # Sourcing
    # ---------------------------------------------------------------
    vendor_id = fields.Many2one('res.partner', string='Supplier',readonly="True",required=True)
    purchase_date = fields.Date(string='Purchase / Receipt Date',readonly="True")
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order',readonly="True")

    notes = fields.Text(string='Notes')
    wood_stock_line = fields.One2many(
        comodel_name='wood.stock.components',
        inverse_name='frms_id',
        string="Wood Stock")

    # ---------------------------------------------------------------
    # Onchange
    # ---------------------------------------------------------------
    @api.onchange('purchase_order_id')
    def _onchange_product_id(self):
        if self.purchase_order_id:
            self.vendor_id = self.purchase_order_id.partner_id


class WoodStockComponents(models.Model):
    _name = "wood.stock.components"
    _description = "Wood Stock"

    frms_id = fields.Many2one(
        comodel_name='furniture.raw.material.stock',
        required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.template', string="Product",
                                 help='Products')
    rate = fields.Float(string="Rate")
    sub_total = fields.Float(string="Total",compute='_compute_sub_total', store=True)
    quantity = fields.Float(string="CFT")
    worker_time = fields.Float(
        string="Workers Time (Hours)",
        help="Total time spent by workers on this component, in hours.")
    worker_rate = fields.Float(string="Worker's Rate")

    @api.depends('rate', 'quantity')
    def _compute_sub_total(self):
        for rec in self:
            rec.sub_total = rec.quantity * rec.rate
