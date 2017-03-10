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


class TestOperatorUnknown(CalculatorTestCase):

    def test_log_other(self):
        # Check how unknown operator value influences
        # attribute calculator
        tgt_attr = self.ch.attribute()
        src_attr = self.ch.attribute()
        invalid_modifier = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=tgt_attr.id,
            operator=1008,
            src_attr=src_attr.id
        )
        effect = self.ch.effect(category=EffectCategory.passive, modifiers=(invalid_modifier,))
        item_eve_type = self.ch.type(effects=(effect,), attributes={src_attr.id: 1.2, tgt_attr.id: 100})
        item = Rig(item_eve_type.id)
        # Action
        self.fit.rigs.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes[tgt_attr.id], 100)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.fit.calculator.map')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(
            log_record.msg, 'malformed modifier on eve type {}: unknown operator 1008'.format(item_eve_type.id)
        )
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)

    def test_log_unorderable_combination(self):
        # Check how non-orderable operator value influences
        # attribute calculator. Previously, bug in calculation
        # method made it to crash
        tgt_attr = self.ch.attribute()
        src_attr = self.ch.attribute()
        invalid_modifier = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=tgt_attr.id,
            operator=None,
            src_attr=src_attr.id
        )
        valid_modifier = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr.id
        )
        effect = self.ch.effect(category=EffectCategory.passive, modifiers=(invalid_modifier, valid_modifier))
        item_eve_type = self.ch.type(effects=(effect,), attributes={src_attr.id: 1.2, tgt_attr.id: 100})
        item = Rig(item_eve_type.id)
        # Action
        self.fit.rigs.add(item)
        # Verification
        self.assertAlmostEqual(item.attributes[tgt_attr.id], 120)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.fit.calculator.map')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(
            log_record.msg, 'malformed modifier on eve type {}: unknown operator None'.format(item_eve_type.id)
        )
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)

    def test_combination(self):
        tgt_attr = self.ch.attribute()
        src_attr = self.ch.attribute()
        invalid_modifier = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=tgt_attr.id,
            operator=1008,
            src_attr=src_attr.id
        )
        valid_modifier = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr.id
        )
        effect = self.ch.effect(category=EffectCategory.passive, modifiers=(invalid_modifier, valid_modifier))
        item = Rig(self.ch.type(effects=(effect,), attributes={src_attr.id: 1.5, tgt_attr.id: 100}).id)
        # Action
        self.fit.rigs.add(item)
        # Verification
        # Make sure presence of invalid operator doesn't prevent
        # from calculating value based on valid modifiers
        self.assertAlmostEqual(item.attributes[tgt_attr.id], 150)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(self.fit)
