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


from eos.const.eos import State, Domain, Scope, Operator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import Modifier
from tests.attribute_calculator.attrcalc_testcase import AttrCalcTestCase
from tests.attribute_calculator.environment import IndependentItem


class TestDomainDirectShipSwitch(AttrCalcTestCase):
    """Test direct modification of ship when it's changed"""

    def test_ship(self):
        tgt_attr = self.ch.attribute(attribute_id=1)
        src_attr = self.ch.attribute(attribute_id=2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.scope = Scope.local
        modifier.src_attr = src_attr.id
        modifier.operator = Operator.post_percent
        modifier.tgt_attr = tgt_attr.id
        modifier.domain = Domain.ship
        modifier.filter_type = None
        modifier.filter_value = None
        effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        effect.modifiers = (modifier,)
        influence_source = IndependentItem(self.ch.type_(
            type_id=1, effects=(effect,), attributes={src_attr.id: 20}))
        self.fit.items.add(influence_source)
        item = self.ch.type_(type_id=None, attributes={tgt_attr.id: 100})
        influence_target1 = IndependentItem(item)
        self.fit.ship = influence_target1
        self.assertNotAlmostEqual(influence_target1.attributes[tgt_attr.id], 100)
        self.fit.ship = None
        influence_target2 = IndependentItem(item)
        self.fit.ship = influence_target2
        self.assertNotAlmostEqual(influence_target2.attributes[tgt_attr.id], 100)
        self.fit.items.remove(influence_source)
        self.fit.ship = None
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)
