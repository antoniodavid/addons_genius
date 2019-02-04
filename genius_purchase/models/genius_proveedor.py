# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

import requests, json

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

headers = {
    'content-type': 'application/x-www-form-urlencoded',
    'charset': 'utf-8',
}

base_url = 'http://localhost:3000/invoices'


class GeniusProveedor(models.Model):
    _name = 'genius.purchase.proveedor'
    _description = "Genius Proveedor"

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(
        string="Nombre",
        required=True,
    )

    supplierID = fields.Char(string="supplierID", )

    def redirect_proveedores_view(self):
        print('Get all proveedores')

        # Get lead views
        try:
            req = requests.get('{}'.format(base_url), headers=headers)
            print(req.status_code)
            content = json.loads(req.content.decode('utf-8'))
            print(content)

        except requests.exceptions.HTTPError as err:
            raise UserError('{}'.format(err))

        action = self.env.ref(
            'genius_purchase.action_genius_purchase_proveedor').read()[0]
        return action
