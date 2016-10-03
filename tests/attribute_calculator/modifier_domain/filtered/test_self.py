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
from tests.attribute_calculator.environment import IndependentItem, CharacterItem, ShipItem


class TestDomainFilterSelf(AttrCalcTestCase):
    """Test domain.self (self-reference) for filtered modifications"""

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute(attribute_id=1)
        src_attr = self.ch.attribute(attribute_id=2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.scope = Scope.local
        modifier.src_attr = src_attr.id
        modifier.operator = Operator.post_percent
        modifier.tgt_attr = self.tgt_attr.id
        modifier.domain = Domain.self_
        modifier.filter_type = FilterType.all_
        modifier.filter_value = None
        effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        effect.modifiers = (modifier,)
        self.influence_source = IndependentItem(self.ch.type_(
            type_id=1061, effects=(effect,), attributes={src_attr.id: 20}))

    def test_ship(self):
        self.fit.ship = self.influence_source
        influence_target = ShipItem(self.ch.type_(type_id=1, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(influence_target)
        self.assertNotAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        self.fit.ship = None
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_character(self):
        self.fit.character = self.influence_source
        influence_target = CharacterItem(self.ch.type_(type_id=1, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(influence_target)
        self.assertNotAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        self.fit.character = None
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_unpositioned_error(self):
        # Here we do not position holder in fit, this way attribute
        # calculator won't know that source is 'owner' of some domain
        # and will log corresponding error
        self.fit.items.add(self.influence_source)
        self.assertEqual(len(self.log), 2)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.fit.attribute_calculator.register')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(
            log_record.msg,
            'malformed modifier on item 1061: invalid reference '
            'to self for filtered modification'
        )
        self.fit.items.remove(self.influence_source)
        self.assert_link_buffers_empty(self.fit)
