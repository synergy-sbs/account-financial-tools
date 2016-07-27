# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import api, fields, models, _
from openerp.exceptions import Warning


class account_debt_report_wizard(models.TransientModel):
    _name = 'account.debt.report.wizard'
    _description = 'Account Debt Report Wizard'

    company_id = fields.Many2one(
        'res.company',
        'Company',
        help="If you don't select a company, debt for all companies will be "
        "exported."
    )
    company_type = fields.Selection([
        ('group_by_company', 'Group by Company'),
        ('consolidate', 'Consolidate all Companies'),
    ],
        default='group_by_company',
    )
    result_selection = fields.Selection(
        [('receivable', 'Receivable Accounts'),
         ('payable', 'Payable Accounts'),
         ('all', 'Receivable and Payable Accounts')],
        "Account Type's",
        required=True,
        default='all'
    )
    from_date = fields.Date('From')
    # to_date = fields.Date('To')
    show_invoice_detail = fields.Boolean('Show Invoice Detail')
    # TODO implementar
    # show_receipt_detail = fields.Boolean('Show Receipt Detail')
    # TODO ver si implementamos esta opcion imprimiendo subilistado de o2m
    group_by_move = fields.Boolean(
        'Group By Move',
        default=True)
    unreconciled_lines = fields.Boolean(
        help='Only Unreconciled Lines?')
    financial_amounts = fields.Boolean(
        help='Add columns for financial amounts?')
    secondary_currency = fields.Boolean(
        help='Add columns for secondary currency?')

    @api.constrains
    def check_company_type(self):
        if self.company_type == 'consolidate' and self.company_id:
            raise Warning(_(
                'You can only select "Consolidate all Companies if no company '
                'is selected'))

    @api.multi
    def confirm(self):
        active_ids = self._context.get('active_ids', False)
        if not active_ids:
            return True
        partners = self.env['res.partner'].browse(active_ids)
        return self.env['report'].with_context(
            group_by_move=self.group_by_move,
            secondary_currency=self.secondary_currency,
            financial_amounts=self.financial_amounts,
            result_selection=self.result_selection,
            company_type=self.company_type,
            company_id=self.company_id.id,
            from_date=self.from_date,
            unreconciled_lines=self.unreconciled_lines,
            show_invoice_detail=self.show_invoice_detail,
            # show_receipt_detail=self.show_receipt_detail,
        ).get_action(
            partners, 'account_debt_report')