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
from eos.const.eos import ModifierDomain, ModifierOperator, ModifierTargetFilter
from eos.const.eve import EffectCategory
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestTgtItemDomainOther(CalculatorTestCase):

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute()
        self.src_attr = self.ch.attribute()
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.other,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr=self.src_attr.id
        )
        self.effect = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier])

    def test_other_domain_container(self):
        influence_source = ModuleHigh(self.ch.type(attributes={self.src_attr.id: 20}, effects=[self.effect]).id)
        influence_target = Charge(self.ch.type(attributes={self.tgt_attr.id: 100}).id)
        influence_source.charge = influence_target
        # Action
        self.fit.modules.high.append(influence_source)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 120)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_other_domain_charge(self):
        influence_source = Charge(self.ch.type(attributes={self.src_attr.id: 20}, effects=[self.effect]).id)
        influence_target = ModuleHigh(self.ch.type(attributes={self.tgt_attr.id: 100}).id)
        self.fit.modules.high.append(influence_target)
        # Action
        influence_target.charge = influence_source
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 120)
        # Action
        influence_target.charge = None
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_self(self):
        # Check that source item isn't modified
        influence_source = ModuleHigh(self.ch.type(
            attributes={self.tgt_attr.id: 100, self.src_attr.id: 20}, effects=[self.effect]
        ).id)
        influence_target = Charge(self.ch.type(attributes={self.tgt_attr.id: 100}).id)
        influence_source.charge = influence_target
        # Action
        self.fit.modules.high.append(influence_source)
        # Verification
        self.assertAlmostEqual(influence_source.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_other_item(self):
        # Here we check some "random" item, w/o linking items
        influence_source = ModuleHigh(self.ch.type(attributes={self.src_attr.id: 20}, effects=[self.effect]).id)
        influence_target = Ship(self.ch.type(attributes={self.tgt_attr.id: 100}).id)
        self.fit.ship = influence_target
        # Action
        self.fit.modules.high.append(influence_source)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
