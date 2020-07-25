#! /usr/bin/env python
# -*- encoding: utf-8 -*-
import erppeek
from cfg_secret_configuration import odoo_configuration_user


###############################################################################
# Odoo Connection
###############################################################################
def init_openerp(url, login, password, database):
    openerp = erppeek.Client(url)
    uid = openerp.login(login, password=password, database=database)
    user = openerp.ResUsers.browse(uid)
    tz = user.tz
    return openerp, uid, tz, database


openerp, uid, tz, db = init_openerp(
    odoo_configuration_user['url'],
    odoo_configuration_user['login'],
    odoo_configuration_user['password'],
    odoo_configuration_user['database'])

###############################################################################
# Script
###############################################################################


def validate_wrong_pos_picking():
    # Update product_type for stock.quant
    ids = openerp.PosOrder.search([
        ('picking_id.state', 'not in', ['done', 'cancel']),
    ])
    pos_orders = openerp.PosOrder.browse(ids)
    pos_orders.create_job_to_validate_wrong_pos_picking()

    return True


# Run the update function
if not openerp:
    print ">>>>>>>> Cannot connect to Server <<<<<<<<<"
else:
    validate_wrong_pos_picking()
