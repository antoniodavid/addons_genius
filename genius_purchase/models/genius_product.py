# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

import requests, json

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class GeniusProduct(models.Model):
    """ The summary line for a class docstring should fit on one line.

    Fields:
      name (Char): Human readable name which will identify each record.

    """

    _name = 'genius.purchase.product'
    _description = "Genius Producto"

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(
        string="Descrpción",
        required=True,
    )

    gtin = fields.Char(
        string="gtin",
    )


   
    


