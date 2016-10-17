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
from tests.attribute_calculator.environment import ChargeHolder, ContainerHolder, IndependentItem


class TestDomainDirectOther(AttrCalcTestCase):
    """Test domain.other for direct modifications"""

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute(attribute_id=1)
        self.src_attr = self.ch.attribute(attribute_id=2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.scope = Scope.local
        modifier.src_attr = self.src_attr.id
        modifier.operator = Operator.post_percent
        modifier.tgt_attr = self.tgt_attr.id
        modifier.domain = Domain.other
        modifier.filter_type = None
        modifier.filter_value = None
        self.effect = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        self.effect.modifiers = (modifier,)

    def test_other_domain_container(self):
        influence_source = ContainerHolder(
            self.ch.type_(type_id=1, effects=(self.effect,), attributes={self.src_attr.id: 20}))
        self.fit.items.add(influence_source)
        influence_target = ChargeHolder(self.ch.type_(type_id=2, attributes={self.tgt_attr.id: 100}))
        influence_source.charge = influence_target
        influence_target.container = influence_source
        self.fit.items.add(influence_target)
        self.assertNotAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        self.fit.items.remove(influence_source)
        influence_source.charge = None
        influence_target.container = None
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_other_domain_charge(self):
        influence_source = ChargeHolder(
            self.ch.type_(type_id=1, effects=(self.effect,), attributes={self.src_attr.id: 20}))
        self.fit.items.add(influence_source)
        influence_target = ContainerHolder(self.ch.type_(type_id=2, attributes={self.tgt_attr.id: 100}))
        influence_source.container = influence_target
        influence_target.charge = influence_source
        self.fit.items.add(influence_target)
        self.assertNotAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        self.fit.items.remove(influence_source)
        influence_source.container = None
        influence_target.charge = None
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_self(self):
        # Check that source holder isn't modified
        influence_source = ContainerHolder(self.ch.type_(
            type_id=1, effects=(self.effect,), attributes={self.tgt_attr.id: 100, self.src_attr.id: 20}))
        self.fit.items.add(influence_source)
        influence_target = ChargeHolder(self.ch.type_(type_id=2, attributes={self.tgt_attr.id: 100}))
        influence_source.charge = influence_target
        influence_target.container = influence_source
        self.fit.items.add(influence_target)
        self.assertAlmostEqual(influence_source.attributes[self.tgt_attr.id], 100)
        self.fit.items.remove(influence_target)
        influence_source.charge = None
        influence_target.container = None
        self.fit.items.remove(influence_source)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_other_holder(self):
        # Here we check some "random" holder, w/o linking holders
        influence_source = ContainerHolder(self.ch.type_(
            type_id=1, effects=(self.effect,), attributes={self.src_attr.id: 20}))
        self.fit.items.add(influence_source)
        influence_target = IndependentItem(self.ch.type_(type_id=2, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(influence_target)
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        self.fit.items.remove(influence_source)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)
