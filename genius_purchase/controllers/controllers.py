# -*- coding: utf-8 -*-
from odoo import http

# class GeniusPurchase(http.Controller):
#     @http.route('/genius_purchase/genius_purchase/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/genius_purchase/genius_purchase/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('genius_purchase.listing', {
#             'root': '/genius_purchase/genius_purchase',
#             'objects': http.request.env['genius_purchase.genius_purchase'].search([]),
#         })

#     @http.route('/genius_purchase/genius_purchase/objects/<model("genius_purchase.genius_purchase"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('genius_purchase.object', {
#             'object': obj
#         })