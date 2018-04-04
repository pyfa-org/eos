# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
#
# This file is part of Eos.
#
# Eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Eos. If not, see <http://www.gnu.org/licenses/>.
# ==============================================================================


from eos import Implant
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.testcase import CalculatorTestCase


class TestRounding(CalculatorTestCase):

    def test_cpu_down(self):
        attr = self.mkattr(attr_id=AttrId.cpu)
        item = Implant(self.mktype(attrs={attr.id: 2.3333}).id)
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attrs[attr.id], 2.33)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_cpu_up(self):
        attr = self.mkattr(attr_id=AttrId.cpu)
        item = Implant(self.mktype(attrs={attr.id: 2.6666}).id)
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attrs[attr.id], 2.67)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_cpu_modified(self):
        src_attr = self.mkattr()
        tgt_attr = self.mkattr(attr_id=AttrId.cpu)
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr.id)
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive, modifiers=[modifier])
        item = Implant(self.mktype(
            attrs={src_attr.id: 20, tgt_attr.id: 1.9444}, effects=[effect]).id)
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 2.33)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_cpu_output(self):
        attr = self.mkattr(attr_id=AttrId.cpu_output)
        item = Implant(self.mktype(attrs={attr.id: 2.6666}).id)
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attrs[attr.id], 2.67)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_power(self):
        attr = self.mkattr(attr_id=AttrId.power)
        item = Implant(self.mktype(attrs={attr.id: 2.6666}).id)
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attrs[attr.id], 2.67)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_power_output(self):
        attr = self.mkattr(attr_id=AttrId.power_output)
        item = Implant(self.mktype(attrs={attr.id: 2.6666}).id)
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attrs[attr.id], 2.67)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_other(self):
        attr = self.mkattr()
        item = Implant(self.mktype(attrs={attr.id: 2.6666}).id)
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attrs[attr.id], 2.6666)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
