# -*- coding: utf-8 -*-

import requests, json
from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, Warning

headers = {
    'accept': 'application/json',
    'content-type': 'application/x-www-form-urlencoded',
    'charset': 'utf-8',
}

data = {'scope': 'posClient', 'grant_type': 'client_credentials'}


class SwaggerConnection(models.Model):
    _name = 'genius.swagger.connection'
    _description = 'Conexion a la Rest APi Swagger'

    name = fields.Char(compute="_default_get_name", string="Nombre")
    type = fields.Selection(
        string="Tipo",
        selection=[('dev', 'Desarrollo'), ('pro', 'Producción')],
        default='pro')
    base_url = fields.Char(
        string="Base Url",
        default="https://posapi.geniuscentral.com",
        required=True)
    token_url = fields.Char(
        string="Token Url",
        default="https://idsrv.geniuscentral.com/connect/token",
        required=True)
    client_id = fields.Char(
        string="Cliente ID", required=True, default="ParadiseHealth-ID")
    client_secret = fields.Char(string="Cliente Contraseña", required=True)
    store_ids = fields.One2many(
        comodel_name="genius.swagger.store",
        inverse_name="connection_id",
        string="Stores")
    access_token = fields.Text(string="Token")
    expires = fields.Integer(string="Expira")
    token_type = fields.Char(string="Tipo de Token")
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[('c', "Conectado"), ('d', "Desconectado")],
        default='d',
    )
    endpoints = fields.Selection(
        selection=[('v', 'swagger/vendor'), ('r', 'swagger/retailer'),
                   ('i', 'swagger/internal'), ('n', 'swagger/in-network')],
        default='r')

    _sql_constraints = [('unique_connection_type', 'UNIQUE(type)',
                         'La conexión debe ser única por cada tipo')]

    @api.depends('client_id')
    def _default_get_name(self):
        for rec in self:
            rec.name = "Swagger %s" % (rec.client_id)

    @api.one
    def get_access_token(self):
        """ Get Access TOken """
        print('get access token')
        data['client_id'] = self.client_id
        data['client_secret'] = self.client_secret

        req = requests.post(self.token_url, headers=headers, data=data)
        print(req.status_code)
        if req.status_code == 200:
            res = req.json()
            self.write({
                'access_token':
                'Bearer {}'.format(res.get('access_token')),
                'expires':
                res.get('expires_in'),
                'token_type':
                res.get('token_type')
            })
            return True
        return False


class SwaggerStore(models.Model):
    _name = 'genius.swagger.store'

    store_id = fields.Integer(string="Store ID", default="100331")
    store_name = fields.Char(string="Nombre del Store")

    connection_id = fields.Many2one(
        string="Conexión a Swagger",
        comodel_name='genius.swagger.connection',
        ondelete='set null',
    )
