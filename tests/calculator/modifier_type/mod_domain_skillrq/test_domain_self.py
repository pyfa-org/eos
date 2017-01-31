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

from eos.const.eos import ModifierTargetFilter, ModifierDomain, ModifierOperator, State
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import DogmaModifier
from tests.calculator.calculator_testcase import CalculatorTestCase
from tests.calculator.environment import IndependentItem, CharDomainItem, ShipDomainItem


class TestModDomainSkillrqDomainSelf(CalculatorTestCase):

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute(attribute_id=1)
        src_attr = self.ch.attribute(attribute_id=2)
        modifier = DogmaModifier()
        modifier.tgt_filter = ModifierTargetFilter.domain_skillrq
        modifier.tgt_domain = ModifierDomain.self
        modifier.state = State.offline
        modifier.src_attr = src_attr.id
        modifier.operator = ModifierOperator.post_percent
        modifier.tgt_attr = self.tgt_attr.id
        modifier.tgt_filter_extra_arg = 56
        effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        effect.modifiers = (modifier,)
        self.influence_source = IndependentItem(self.ch.type(
            type_id=322, effects=(effect,),
            attributes={src_attr.id: 20}
        ))

    def test_ship(self):
        eve_type = self.ch.type(type_id=2, attributes={self.tgt_attr.id: 100})
        eve_type.required_skills = {56: 1}
        influence_target = ShipDomainItem(eve_type)
        self.fit.items.add(influence_target)
        # Action
        self.fit.ship = self.influence_source
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 120)
        # Action
        self.fit.ship = None
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_character(self):
        eve_type = self.ch.type(type_id=2, attributes={self.tgt_attr.id: 100})
        eve_type.required_skills = {56: 1}
        influence_target = CharDomainItem(eve_type)
        self.fit.items.add(influence_target)
        # Action
        self.fit.character = self.influence_source
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 120)
        # Cleanup
        self.fit.character = None
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)

    def test_unpositioned_error(self):
        # Action
        # Here we do not position item in fit, this way attribute
        # calculator won't know that source is 'owner' of some domain
        # and will log corresponding error
        self.fit.items.add(self.influence_source)
        # Verification
        self.assertEqual(len(self.log), 2)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.fit.calculator.register.dogma')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(
            log_record.msg,
            'malformed modifier on eve type 322: invalid reference '
            'to self for filtered modification'
        )
        # Cleanup
        self.fit.items.remove(self.influence_source)
        self.assert_calculator_buffers_empty(self.fit)
