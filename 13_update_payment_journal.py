# -*- coding: utf-8 -*-
from cfg_secret_configuration import odoo_configuration_user
import erppeek
import base64
from xlrd import open_workbook


###############################################################################
# Odoo Connection
###############################################################################


def init_openerp(url, login, password, database):
    openerp = erppeek.Client(url)
    uid = openerp.login(login, password=password, database=database)
    user = openerp.ResUsers.browse(uid)
    tz = user.tz
    return openerp, uid, tz


# Enter your server information below
openerp, uid, tz = init_openerp(
    odoo_configuration_user['url'],
    odoo_configuration_user['login'],
    odoo_configuration_user['password'],
    odoo_configuration_user['database'])

payment_files = [
    './payment/account.payment 1.xls',
    './payment/account.payment 2.xls',
    './payment/account.payment 3.xls',
    './payment/account.payment 4.xls',
    './payment/account.payment 5.xls',
    './payment/account.payment 6.xls',
    './payment/account.payment 7.xls',
]


def update_payment_journal(validated_only=True):

    print '==== START UPDATING PAYMENT JOURNAL ===='
    lcr_journal = openerp.AccountJournal.browse([('code', '=', 'LCR')],
                                                limit=1)
    if not lcr_journal:
        print '=== Could not find journal LCR, please check!'
        return

    to_account = openerp.AccountAccount.browse(
        [('code', '=', '403000')])

    if not to_account:
        print "=== Cannot find account 403000"
        return

    deprecated = to_account[0].deprecated
    to_account[0].deprecated = False

    report_data = [
        "ID|Journal|Payment Name|New Payment Name|From Account Code|To Account Code"]

    for f in payment_files:
        print '=== Processing file: %s' % f
        # Read xls file to get the payments
        data_file = open_workbook(f)
        sheet = data_file.sheets()[0]
        payment_ids = []
        for row in range(sheet.nrows):
            if row == 0:
                continue
            value_id = sheet.cell(row, 0).value
            try:
                payment_id = int(value_id.split('_')[-1])
                payment_ids.append(payment_id)
            except ValueError as e:
                print 'ERROR while parsing payment id from file, '\
                      'raw value: %s. Error: %s' % (value_id, str(e))

        if not payment_ids:
            continue

        payments = openerp.AccountPayment.browse([('id', 'in', payment_ids)])
        if len(payments) != len(payment_ids):
            print "=== Some payment missing"
            return

        for payment in payments:
            if not payment.invoice_ids or \
                    payment.journal_id.id == lcr_journal[0].id:
                print "=== Corrected Payment: ", payment

                rdata = [str(payment.id), '',
                         payment.name, payment.name,
                         payment.payment_account_id and payment.payment_account_id.name or '', '403000']

                report_data.append(u"|".join(rdata))

                continue

            print '= Processing payment id: %s' % payment.id

            payment_name = payment.name
            source_account = payment.payment_account_id and payment.payment_account_id.name or ''
            payment_journal = payment.journal_id.name

            if validated_only:
                continue

            try:
                # Step 1: Cancel payment
                payment.cancel_payment()

                # Step 2: Update payment journal
                payment.journal_id = lcr_journal[0].id
                payment.payment_account_id = to_account[0].id

                # Step 3: Confirm payment
                payment.post_payment()

            except:
                print "Cannot process Payment: ", payment.name

            rdata = [str(payment.id), payment_journal,
                     payment_name, payment.name,
                     source_account, '403000']

            report_data.append(u"|".join(rdata))

    to_account[0].deprecated = deprecated

    # Write the reporting data to file
    with open("update_report_journal.csv", "w") as f:
        data = u"\n".join(report_data)

        # write it to file
        f.write(data.encode('utf8'))


update_payment_journal()
