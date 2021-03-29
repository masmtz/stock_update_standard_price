# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        if self.picking_type_id.code == 'incoming':
            for line in self.move_ids_without_package:
                if line.purchase_line_id and line.purchase_line_id.product_id:
                    po_line = line.purchase_line_id
                    if po_line.product_id.type == 'product':
                        product = po_line.product_id
                        product.update({'standard_price': po_line.price_unit})
        else:
            if self.picking_type_id.code == 'outgoing':
                origin = 'Retorno de '
                if origin in self.origin:
                    for move in self.move_ids_without_package:
                        move_line_ids = self.env['stock.move.line'].search(
                            [('product_id', '=', move.product_id.id),
                             ('state', '=', 'done')], order='date desc')
                        cost = 0
                        for line in move_line_ids.filtered(
                                lambda l: l.picking_id.picking_type_id.code
                                == 'incoming').sorted(key=lambda l: l.date):

                            reference = (origin + line.reference)
                            picking = self.env['stock.picking'].search(
                                [('origin', '=', reference)])
                            if not picking:
                                cost = line.move_id.purchase_line_id.price_unit
                                # line.product_id.update(
                                #     {'standard_price': cost})
                        move.product_id.update({'standard_price': cost})
        return res
