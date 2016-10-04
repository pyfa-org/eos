# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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

from eos.const.eos import State, Domain, Scope, FilterType, Operator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import Modifier
from tests.attribute_calculator.attrcalc_testcase import AttrCalcTestCase
from tests.attribute_calculator.environment import IndependentItem, ShipItem


class TestDomainFilterUnknown(AttrCalcTestCase):
    """Test reaction to unknown domain specification for filtered modification"""

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute(attribute_id=1)
        self.src_attr = self.ch.attribute(attribute_id=2)
        self.invalid_modifier = invalid_modifier = Modifier()
        invalid_modifier.state = State.offline
        invalid_modifier.scope = Scope.local
        invalid_modifier.src_attr = self.src_attr.id
        invalid_modifier.operator = Operator.post_percent
        invalid_modifier.tgt_attr = self.tgt_attr.id
        invalid_modifier.domain = 1972
        invalid_modifier.filter_type = FilterType.all_
        invalid_modifier.filter_value = None
        self.effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)

    def test_log(self):
        self.effect.modifiers = (self.invalid_modifier,)
        holder = IndependentItem(self.ch.type_(
            type_id=754, effects=(self.effect,), attributes={self.src_attr.id: 20}))
        self.fit.items.add(holder)
        self.assertEqual(len(self.log), 2)
        for log_record in self.log:
            self.assertEqual(log_record.name, 'eos.fit.attribute_calculator.register')
            self.assertEqual(log_record.levelno, logging.WARNING)
            self.assertEqual(
                log_record.msg,
                'malformed modifier on item 754: unsupported target '
                'domain 1972 for filtered modification'
            )
        self.fit.items.remove(holder)
        self.assert_link_buffers_empty(self.fit)

    def test_combination(self):
        valid_modifier = Modifier()
        valid_modifier.state = State.offline
        valid_modifier.scope = Scope.local
        valid_modifier.src_attr = self.src_attr.id
        valid_modifier.operator = Operator.post_percent
        valid_modifier.tgt_attr = self.tgt_attr.id
        valid_modifier.domain = Domain.ship
        valid_modifier.filter_type = FilterType.all_
        valid_modifier.filter_value = None
        self.effect.modifiers = (self.invalid_modifier, valid_modifier)
        influence_source = IndependentItem(self.ch.type_(
            type_id=1, effects=(self.effect,), attributes={self.src_attr.id: 20}))
        self.fit.items.add(influence_source)
        influence_target = ShipItem(self.ch.type_(type_id=2, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(influence_target)
        # Invalid domain in modifier should prevent proper processing of other modifiers
        self.assertNotAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        self.fit.items.remove(influence_target)
        self.fit.items.remove(influence_source)
        self.assertEqual(len(self.log), 5)
        self.assert_link_buffers_empty(self.fit)
