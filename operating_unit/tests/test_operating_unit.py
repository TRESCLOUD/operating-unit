# © 2017-TODAY ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo.exceptions import AccessError
from odoo.tests import Form, tagged

from .common import OperatingUnitCommon


@tagged("post_install", "-at_install")
class TestOperatingUnit(OperatingUnitCommon):
    def test_01_operating_unit(self):
        # User 1 tries to create and modify an OU
        # Create
        self._create_operating_unit(self.user1.id, "Test", "TEST")
        # Write
        self.b2b.with_user(self.user1.id).write({"code": "B2B_changed"})
        # Read list of OU available by User 1
        operating_unit_list_1 = (
            self.env["operating.unit"]
            .with_user(self.user1.id)
            .search([])
            .mapped("code")
        )
        nou = self.env["operating.unit"].search(
            [
                "|",
                ("company_id", "=", False),
                ("company_id", "in", self.user1.company_ids.ids),
            ]
        )
        self.assertEqual(
            len(operating_unit_list_1),
            len(nou),
            "User 1 should have access to all the OU",
        )

        # User 2 tries to create and modify an OU
        with self.assertRaises(AccessError):
            # Create
            self._create_operating_unit(self.user2.id, "Test", "TEST")
        with self.assertRaises(AccessError):
            # Write
            self.b2b.with_user(self.user2.id).write({"code": "B2B_changed"})

        # Read list of OU available by User 2
        operating_unit_list_2 = (
            self.env["operating.unit"]
            .with_user(self.user2.id)
            .search([])
            .mapped("code")
        )
        self.assertEqual(
            len(operating_unit_list_2), 1, "User 2 should have access to one OU"
        )
        self.assertEqual(
            operating_unit_list_2[0],
            "B2C",
            f"User 2 should have access to {self.b2c.name}",
        )

    def test_02_operating_unit(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "base_setup.default_user_rights", "True"
        )
        user_form = Form(self.env["res.users"])
        user_form.name = "Test Customer"
        user_form.login = "test"
        user = user_form.save()
        default_user = self.env.ref("base.default_user")
        self.assertEqual(
            user.default_operating_unit_id, default_user.default_operating_unit_id
        )
        nou = self.env["operating.unit"].search(
            [
                "|",
                ("company_id", "=", False),
                ("company_id", "in", self.user1.company_ids.ids),
            ],
            limit=1,
        )
        partner = self.env["res.partner"].search([], limit=1)
        with Form(self.env["res.users"], view="base.view_users_form") as user_form:
            user_form.default_operating_unit_id = nou[0]
            with user_form.operating_unit_ids.new() as line:
                line.partner_id = partner
                line.name = "Test Unit"
                line.code = "007"
            user_form.name = "Test Customer"
            user_form.login = "test2"

    def test_find_operating_unit_by_name_or_code(self):
        ou = self._create_operating_unit(self.user1.id, "name", "code")
        expected_result = [(ou.id, "[code] name")]
        self.assertEqual(ou.name_search("nam"), expected_result)
        self.assertEqual(ou.name_search("cod"), expected_result)
        self.assertEqual(ou.name_search("dummy"), [])

    def test_03_operating_unit(self):
        """
        The method _get_default_operating_unit should not return
        operating units belonging to a company that is not active
        """
        self.assertEqual(
            self.res_users_model._get_default_operating_unit(uid2=self.user1.id),
            self.ou1,
        )
        self.assertEqual(
            self.res_users_model.with_company(
                self.company_2
            )._get_default_operating_unit(uid2=self.user1.id),
            False,
        )

        self.user1.company_ids += self.company_2
        ou_company_2 = self._create_operating_unit(
            self.user1.id, "Test Company", "TESTC", self.company_2
        )
        self.user1.assigned_operating_unit_ids += ou_company_2
        self.assertEqual(
            self.res_users_model.with_company(
                self.company_2
            )._get_default_operating_unit(uid2=self.user1.id),
            ou_company_2,
        )

    def test_create_multi_operating_unit(self):
        res = (
            self.env["operating.unit"]
            .with_user(self.user1.id)
            .create(
                [
                    {"name": "Test 0", "code": "TEST0", "partner_id": self.company.id},
                    {"name": "Test 1", "code": "TEST1", "partner_id": self.company.id},
                    {"name": "Test 2", "code": "TEST2", "partner_id": self.company.id},
                ]
            )
        )
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0].user_ids, self.user1)
        self.assertEqual(res[1].user_ids, self.user1)
        self.assertEqual(res[2].user_ids, self.user1)
