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


def compute_shift_type():
    # Update product_type for stock.quant
    ids = openerp.ResPartner.search([('is_associated_people', '=', True)])
    partners = openerp.ResPartner.browse(ids)
    partners.update_shift_type()
    return True


# Run the update function
if not openerp:
    print ">>>>>>>> Cannot connect to Server <<<<<<<<<"
else:
    compute_shift_type()
