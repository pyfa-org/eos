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


class TestTgtItemDomainUnknown(CalculatorTestCase):

    def test_combination(self):
        tgt_attr = self.ch.attribute()
        src_attr = self.ch.attribute()
        invalid_modifier = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=1972,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr=src_attr.id)
        valid_modifier = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr=src_attr.id)
        effect = self.ch.effect(
            category=EffectCategoryId.passive,
            modifiers=(invalid_modifier, valid_modifier))
        item = Ship(self.ch.type(
            attributes={src_attr.id: 20, tgt_attr.id: 100},
            effects=[effect]).id)
        # Action
        self.fit.ship = item
        # Verification
        self.assertAlmostEqual(item.attributes[tgt_attr.id], 120)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
