#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
#===============================================================================


from eos.const.eos import State, Location, Context, Operator
from eos.const.eve import EffectCategory
from eos.data.cache.object.modifier import Modifier
from eos.tests.attribute_calculator.attrcalc_testcase import AttrCalcTestCase
from eos.tests.attribute_calculator.environment import IndependentItem, ItemWithOther


class TestLocationDirectOther(AttrCalcTestCase):
    """Test location.other for direct modifications"""

    def setUp(self):
        AttrCalcTestCase.setUp(self)
        self.tgt_attr = self.ch.attribute(attribute_id=1)
        src_attr = self.ch.attribute(attribute_id=2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.context = Context.local
        modifier.source_attribute_id = src_attr.id
        modifier.operator = Operator.post_percent
        modifier.target_attribute_id = self.tgt_attr.id
        modifier.location = Location.other
        modifier.filter_type = None
        modifier.filter_value = None
        effect = self.ch.effect(effect_id=1, category_id=EffectCategory.passive)
        effect.modifiers = (modifier,)
        # We added target attribute to influence source for testSelf;
        # currently, eos cannot calculate attributes which are originally
        # missing on item
        self.influence_source = ItemWithOther(self.ch.type_(type_id=1, effects=(effect,),
                                                            attributes={self.tgt_attr.id: 100, src_attr.id: 20}))
        self.fit.items.add(self.influence_source)

    def test_other_location(self):
        influence_target = ItemWithOther(self.ch.type_(type_id=2, attributes={self.tgt_attr.id: 100}))
        self.influence_source.make_other_link(influence_target)
        self.fit.items.add(influence_target)
        self.assertNotAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        self.fit.items.remove(self.influence_source)
        self.influence_source.break_other_link(influence_target)
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_self(self):
        # Check that source holder isn't modified
        influence_target = ItemWithOther(self.ch.type_(type_id=2, attributes={self.tgt_attr.id: 100}))
        self.influence_source.make_other_link(influence_target)
        self.fit.items.add(influence_target)
        self.assertAlmostEqual(self.influence_source.attributes[self.tgt_attr.id], 100)
        self.fit.items.remove(influence_target)
        self.influence_source.break_other_link(influence_target)
        self.fit.items.remove(self.influence_source)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)

    def test_other_holder(self):
        # Here we check some "random" holder, w/o linking holders
        influence_target = IndependentItem(self.ch.type_(type_id=2, attributes={self.tgt_attr.id: 100}))
        self.fit.items.add(influence_target)
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        self.fit.items.remove(self.influence_source)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_link_buffers_empty(self.fit)
