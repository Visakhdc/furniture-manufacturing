from odoo import api, fields, models


class FurnitureManagement(models.Model):
    _name = "furniture.management"
    _description = "Furniture Management"
    _order = 'id desc'

    name = fields.Char(
        string='Reference', required=True, copy=False, readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'furniture.management') or 'New')

    product_id = fields.Many2one('product.template', string="Product Name",
                                  help='Products')
    uom_id = fields.Many2one('uom.uom', string="UoM")
    on_hand = fields.Float(string="Manufacturing Quantity")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assembly', 'production & Assembly'),
        ('polishing', 'Polishing & Finishing'),
        ('upholstery', 'Upholstery & Cushioning'),
        ('quality_check', 'Quality Check'),
        ('done', 'Despatch')], string='Status', default='draft', tracking=True)
    date = fields.Datetime(string="Start Date", default=fields.Date.today(),readonly=True)
    color = fields.Integer('Color Index')
    components_line = fields.One2many(
        comodel_name='manufacturing.components',
        inverse_name='fm_id',
        string="Components")

    def action_assembly(self):
        self._reduce_component_stock()
        self.write({
            "state": "assembly",
        })

    def action_polishing(self):
        self.write({
            "state": "polishing",
        })

    def action_upholstery(self):
        self.write({
            "state": "upholstery",
        })

    def action_quality_check(self):
        self.write({
            "state": "quality_check",
        })

    def action_done(self):
        print("haiiiiii")
        for rec in self:
            if rec.product_id and rec.on_hand:
                print("////",rec.product_id.name)
                rec._update_product_stock()
        self.write({
            "state": "done",
        })

    def _reduce_component_stock(self):
        StockQuant = self.env['stock.quant']
        location = self.env.ref('stock.stock_location_stock')

        for rec in self:
            for line in rec.components_line:
                if not line.product_id or line.quantity <= 0:
                    continue

                variant = line.product_id.product_variant_id
                StockQuant._update_available_quantity(
                    variant, location, -line.quantity
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'furniture.management') or 'New'
        return super().create(vals_list)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id

    def _update_product_stock(self):
        self.ensure_one()
        product = self.product_id.product_variant_ids[:1]

        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)

        self.env['stock.quant']._update_available_quantity(product, warehouse.lot_stock_id, self.on_hand)
        self.env.cr.commit()

        product.invalidate_recordset()

class ManufacturingComponents(models.Model):
    _name = "manufacturing.components"
    _description = "Components"

    fm_id = fields.Many2one(
        comodel_name='furniture.management',
        required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.template', string="Product",
                                 help='Products')
    availability_status = fields.Selection([
        ('available', 'Available'),
        ('not_available', 'Not Available'),
    ], string="Availability", default='available', required=True,
        compute='_compute_availability_status', store=True, readonly=True)
    quantity = fields.Float(string="Quantity")
    uom_id = fields.Many2one('uom.uom', string="UoM", readonly=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id

    @api.depends('product_id', 'quantity', 'uom_id')
    def _compute_availability_status(self):
        for rec in self:
            if rec.product_id:
                on_hand_qty = rec.product_id.qty_available
                rec.availability_status = (
                    'available' if on_hand_qty > 0 else 'not_available'
                )