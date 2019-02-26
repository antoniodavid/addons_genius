# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

import requests, json
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

headers = {
    'accept': 'application/json',
    'content-type': 'application/json',
    'charset': 'utf-8',
}


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    uniqueOrderID = fields.Char(string="Uid")


class GeniusPurchaseOrder(models.Model):
    _name = 'genius.purchase.order'
    _inherit = ['mail.thread']
    _description = "Genius Orden de Compra"

    name = fields.Char(string="Nombre", compute="_compute_get_name", track_visibility=True)
    uniqueOrderID = fields.Char(string=_("Uid"))
    orderID = fields.Integer(string=_("Order ID"))
    storeID = fields.Integer(string=_("Store ID"))
    storeName = fields.Char(string=_("Store Name"))
    storePONumber = fields.Char(string=_("Store Number"))
    supplierID = fields.Char(string=_("Supplier ID"))
    supplierName = fields.Char(string=_("Supplier Name"))
    dateCreated = fields.Datetime(string=_("Created Date"))
    orderTotal = fields.Float(string=_("Total Amount"))
    orderSource = fields.Integer(string=_("Order Source"))
    orderStatus = fields.Integer(string=_("Order Status"))
    accountNumber = fields.Char(string=_("Account Number"))
    message = fields.Html(string=_("Message"))
    state = fields.Selection(
        string=_('State'),
        selection=[('draft', 'Draft'), ('done', 'Done')],
        default='draft',
    )
    

    order_line_ids = fields.One2many(
        comodel_name='genius.purchase.order.line',
        inverse_name='purchase_id',
        ondelete='cascade',
        string=_("Purchase Order Lines"))

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'name' in init_values:
            return 'mail.mt_comment'
        return False

    @api.multi
    def action_oc_draft(self):
        for rec in self:

            order = self.env['purchase.order'].search([('uniqueOrderID', '=', rec.uniqueOrderID)] )
            if order.exists():
                return 
            
            supplier = self.env['res.partner'].search([('supplier', '=', True), ('name', '=', rec.supplierName)], limit=1)

            if supplier.exists():
                order_lines = []
                order_vals = {
                    'partner_id': supplier.id,
                    'state': 'draft',
                    'date_order': rec.dateCreated,
                    'uniqueOrderID': rec.uniqueOrderID,
                    'order_line': order_lines
                }

                product_obj = self.env['product.product']
                for order_line in rec.order_line_ids:
                    product = product_obj.search([('barcode', '=', order_line.gtin)], limit=1)
                    if product.exists():
                        order_line_vals = {
                            'product_id': product.id,
                            'name': product.name,
                            'product_uom': product.uom_id.id,
                            'date_planned': rec.dateCreated,
                            'price_unit': order_line.cost,
                            'product_qty': order_line.quantity
                        }
                        order_lines.append((0, 0, order_line_vals))

                self.env['purchase.order'].create(order_vals)
                rec.state = 'done'
            else:
                raise Warning('No existe el proveedor')

    @api.model
    def create(self, vals):
        order_id = super(
            GeniusPurchaseOrder,
            self.with_context(mail_create_nolog=True)).create(vals)

        #Create  a purchase.order
        # Get a Supplier
        supplier = self.env['res.partner'].search(
            [('supplier', '=', True), ('name', '=', vals.get('supplierName'))],
            limit=1)

        if supplier.exists():
            order_lines = []
            order_vals = {
                'partner_id': supplier.id,
                'state': 'draft',
                'date_order': vals.get('dateCreated', fields.Datetime.today),
                'uniqueOrderID': vals.get('uniqueOrderID'),
                'order_line': order_lines
            }

            product_obj = self.env['product.product']
            for order_line in vals.get('order_line_ids'):
                line = order_line[2]
                product = product_obj.search(
                    [('barcode', '=', line.get('gtin'))], limit=1)
                if product.exists():
                    order_line_vals = {
                        'product_id':
                        product.id,
                        'name':
                        product.name,
                        'product_uom':
                        product.uom_id.id,
                        'date_planned':
                        vals.get('dateCreated', fields.Datetime.today),
                        'price_unit':
                        line.get('cost'),
                        'product_qty':
                        line.get('quantity')
                    }
                    order_lines.append((0, 0, order_line_vals))

            self.env['purchase.order'].create(order_vals)
            order_id.write({'state': 'done'})

        return order_id

    @api.depends('storeName', 'supplierName')
    def _compute_get_name(self):
        for rec in self:
            rec.name = "{} - {}".format(rec.storeName, rec.supplierName)

    @api.model
    def requests(self, connection=None, store_id=None, endpoints=''):

        req = None
        headers['Authorization'] = connection.access_token
        payload = {'previouslyExportedOrders': 'false'}
        base_url = "{}/stores/{}/{}".format(connection.base_url, store_id,
                                            endpoints)

        req = requests.get('{}'.format(base_url), headers=headers, params=payload, timeout=5)

        if req.status_code != 200 and connection.get_access_token():
            headers['Authorization'] = connection.access_token
            req = requests.get('{}'.format(base_url), headers=headers, params=payload, timeout=5)

        return req

    @api.model
    def get_purchase_orders(self):
        connection = self.env['genius.swagger.connection'].search(
            [('type', '=', 'pro')], limit=1)

        if not connection.exists():
            # raise UserError(_("Ud. debe configurar la conexión a Swagger"))
            return

        uniqueOrder_List = [item.uniqueOrderID for item in self.search([])]

        for store in connection.store_ids:
            req = self.requests(
                connection=connection,
                store_id=store.store_id,
                endpoints='orders')
            
            print(req.text)
            print(req.json())
            orders = json.loads(req.content.decode('utf-8'))

            print(orders)

            if len(orders.get('orders')):
                orders_list = [
                    orders for orders in orders.get('orders') if
                    not orders['header']['uniqueOrderID'] in uniqueOrder_List
                ]
                # if len(orders_list):
                #     self.env.user.notify_info(
                #         message="Se han añadido {} nuevas órdenes de compras".
                #         format(len(orders_list)))

                for order in orders_list:
                    uniqueOrderID = order['header'].get('uniqueOrderID')
                    if not uniqueOrderID in uniqueOrder_List:
                        order_lines = []
                        order_vals = {
                            'uniqueOrderID': uniqueOrderID,
                            'orderID': order['header'].get('orderID'),
                            'storeID': order['header'].get('storeID'),
                            'storeName': order['header'].get('storeName'),
                            'storePONumber':
                            order['header'].get('storePONumber'),
                            'supplierID': order['header'].get('supplierID'),
                            'supplierName':
                            order['header'].get('supplierName'),
                            'dateCreated': order['header'].get('dateCreated'),
                            'orderTotal': order['header'].get('orderTotal'),
                            'orderSource': order['header'].get('orderSource'),
                            'orderStatus': order['header'].get('orderStatus'),
                            'accountNumber':
                            order['header'].get('accountNumber'),
                            'message': order['header'].get('message'),
                            'order_line_ids': order_lines
                        }

                        for item in order.get('details'):
                            vals = {
                                'supplierSKU':
                                item.get('supplierSKU'),
                                'itemDescription':
                                item.get('itemDescription'),
                                'cost':
                                item.get('cost'),
                                'quantity':
                                item.get('quantity'),
                                'uom':
                                item.get('uom'),
                                'amount':
                                int(item.get('quantity')) * float(
                                    item.get('cost')),
                                'gtin':
                                item.get('gtin')
                            }
                            order_lines.append((0, 0, vals))

                        self.create(order_vals)

        # return orders

    def redirect_purchases_orders_view(self):
        # Get lead views
        # self.get_purchase_orders()
        body ="Message has been approved on {}".format(datetime.now())
        self.message_post(body=body, subject="Subject", subtype="mt_note")
        
        action = self.env.ref(
            'genius_purchase.action_genius_purchase_order').read()[0]
        return action


class GeniusPurchaseOrderLine(models.Model):
    _name = 'genius.purchase.order.line'

    supplierSKU = fields.Char(string=_("SKU Supplier"))
    itemDescription = fields.Char(string=_("Product"))
    cost = fields.Float(string=_("Cost"))
    quantity = fields.Integer(string=_("Quantity"))
    uom = fields.Char(string=_("Uom"))
    gtin = fields.Char()
    amount = fields.Float(
        compute="_compute_get_amount", store=True, string=_("Amount"))
    purchase_id = fields.Many2one(
        comodel_name='genius.purchase.order', string=_("Órden de Compra"))

    @api.depends('quantity', 'cost')
    def _compute_get_amount(self):
        for rec in self:
            rec.amount = rec.quantity * rec.amount