# -*- coding: utf-8 -*-
# © 2015 Eficent - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from openerp.addons.account_operating_unit.tests import\
    test_account_operating_unit as test_ou


class TestOuSecurity(test_ou.TestAccountOperatingUnit):

    def test_security(self):
        """Test Security of Account Operating Unit"""
        # User 2 is only assigned to Operating Unit B2C, and cannot list
        # Journal Entries from Operating Unit B2B.
        move_ids = self.aml_model.sudo(self.user2_id.id).\
            search([('operating_unit_id', '=', self.b2b.id)])
        self.assertEqual(move_ids, [], 'user_2 should not have access to '
                                       'OU %s' % self.b2b.name)
