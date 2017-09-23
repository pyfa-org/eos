# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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
# ===============================================================================


from eos import *
from eos.const.eos import ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import EffectCategory
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestCap(CalculatorTestCase):
    """Test how capped attribute values are processed"""

    def setUp(self):
        super().setUp()
        self.capping_attr = self.ch.attribute(default_value=5)
        self.capped_attr = self.ch.attribute(max_attribute=self.capping_attr.id)
        self.source_attr = self.ch.attribute()
        # Just to make sure cap is applied to final value, not
        # base, make some basic modification modifier
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.capped_attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=self.source_attr.id
        )
        self.effect = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier])

    def test_cap_default(self):
        # Check that cap is applied properly when item
        # doesn't have base value of capping attribute
        item = Implant(self.ch.type(
            effects=[self.effect], attributes={self.capped_attr.id: 3, self.source_attr.id: 6}
        ).id)
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes[self.capped_attr.id], 5)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_cap_attr_eve_type(self):
        # Make sure that item's own specified attribute
        # value is taken as cap
        item = Implant(self.ch.type(
            effects=[self.effect],
            attributes={self.capped_attr.id: 3, self.source_attr.id: 6, self.capping_attr.id: 2}
        ).id)
        self.fit.implants.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes[self.capped_attr.id], 2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_cap_attr_modified(self):
        # Make sure that item's own specified attribute
        # value is taken as cap, and it's taken with all
        # modifications applied onto it
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.capping_attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=self.source_attr.id
        )
        effect = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier])
        item = Implant(self.ch.type(
            effects=(self.effect, effect),
            attributes={self.capped_attr.id: 3, self.source_attr.id: 6, self.capping_attr.id: 0.1}
        ).id)
        self.fit.implants.add(item)
        # Verification
        # Attr value is 3 * 6 = 18, but cap value is 0.1 * 6 = 0.6
        self.assertAlmostEqual(item.attributes[self.capped_attr.id], 0.6)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_cap_update(self):
        # If cap updates, capped attributes should
        # be updated too
        item = Rig(self.ch.type(
            effects=[self.effect],
            attributes={self.capped_attr.id: 3, self.source_attr.id: 6, self.capping_attr.id: 2}
        ).id)
        self.fit.rigs.add(item)
        # Check attribute vs initial cap
        self.assertAlmostEqual(item.attributes[self.capped_attr.id], 2)
        # Add something which changes capping attribute
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=self.capping_attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=self.source_attr.id
        )
        effect = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier])
        cap_updater = Implant(self.ch.type(effects=[effect], attributes={self.source_attr.id: 3.5}).id)
        self.fit.implants.add(cap_updater)
        # Verification
        # As capping attribute is updated, capped attribute must be updated too
        self.assertAlmostEqual(item.attributes[self.capped_attr.id], 7)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
