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


import logging

from eos import *
from eos.const.eos import ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import DogmaModifier
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestTgtFilterUnknown(CalculatorTestCase):

    def setUp(self):
        super().setUp()
        self.tgt_attr = tgt_attr = self.ch.attribute()
        self.src_attr = src_attr = self.ch.attribute()
        self.invalid_modifier = DogmaModifier(
            tgt_filter=26500,
            tgt_domain=ModifierDomain.self,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr=src_attr.id
        )

    def test_log(self):
        effect = self.ch.effect(category=EffectCategory.passive, modifiers=(self.invalid_modifier,))
        item_eve_type = self.ch.type(effects=(effect,), attributes={self.src_attr.id: 20, self.tgt_attr: 100})
        item = Rig(item_eve_type.id)
        # Action
        self.fit.rigs.add(item)
        # Verification
        self.assertEqual(len(self.log), 2)
        for log_record in self.log:
            self.assertEqual(log_record.name, 'eos.fit.calculator.register')
            self.assertEqual(log_record.levelno, logging.WARNING)
            self.assertEqual(
                log_record.msg, 'malformed modifier on eve type {}: '
                'invalid target filter 26500'.format(item_eve_type.id)
            )
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)

    def test_combination(self):
        valid_modifier = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr=self.src_attr.id
        )
        effect = self.ch.effect(category=EffectCategory.passive, modifiers=(self.invalid_modifier, valid_modifier))
        item = Rig(self.ch.type(effects=(effect,), attributes={self.src_attr.id: 20, self.tgt_attr.id: 100}).id)
        # Action
        self.fit.rigs.add(item)
        # Verification
        # Invalid filter type in modifier should prevent proper processing of other modifiers
        self.assertAlmostEqual(item.attributes[self.tgt_attr.id], 120)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
