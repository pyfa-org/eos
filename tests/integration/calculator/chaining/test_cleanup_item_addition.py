# ==============================================================================
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
# ==============================================================================


from eos import *
from eos.const.eos import ModifierDomain, ModifierOperator, ModifierTargetFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestCleanupChainAddition(CalculatorTestCase):
    """Check that added item "damages" all neccessary attribute values."""

    def test_attribute(self):
        # Setup
        attr1 = self.ch.attr()
        attr2 = self.ch.attr()
        attr3 = self.ch.attr()
        modifier1 = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=attr2.id,
            operator=ModifierOperator.post_mul,
            src_attr=attr1.id)
        effect1 = self.ch.effect(
            category=EffectCategoryId.passive, modifiers=[modifier1])
        modifier2 = self.mod(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=attr3.id,
            operator=ModifierOperator.post_percent,
            src_attr=attr2.id)
        effect2 = self.ch.effect(
            category=EffectCategoryId.passive, modifiers=[modifier2])
        implant_item = Implant(self.ch.type(
            attributes={attr1.id: 5}, effects=[effect1]).id)
        ship_item = Ship(self.ch.type(
            attributes={attr2.id: 7.5}, effects=[effect2]).id)
        rig_item = Rig(self.ch.type(attributes={attr3.id: 0.5}).id)
        self.fit.ship = ship_item
        self.fit.rigs.add(rig_item)
        self.assertAlmostEqual(rig_item.attributes[attr3.id], 0.5375)
        # Action
        self.fit.implants.add(implant_item)
        # Verification
        # Added item must clean all already calculated attributes which are now
        # affected by it, to allow recalculation
        self.assertAlmostEqual(rig_item.attributes[attr3.id], 0.6875)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
