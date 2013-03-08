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
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import Fit, IndependentItem


class TestTargetAttribute(AttrCalcTestCase):
    """Test that only targeted attributes are modified"""

    def testTargetAttributes(self):
        tgtAttr1 = self.ch.attribute(attributeId=1)
        tgtAttr2 = self.ch.attribute(attributeId=2)
        tgtAttr3 = self.ch.attribute(attributeId=3)
        srcAttr = self.ch.attribute(attributeId=4)
        modifier1 = Modifier()
        modifier1.state = State.offline
        modifier1.context = Context.local
        modifier1.sourceAttributeId = srcAttr.id
        modifier1.operator = Operator.postPercent
        modifier1.targetAttributeId = tgtAttr1.id
        modifier1.location = Location.self_
        modifier1.filterType = None
        modifier1.filterValue = None
        modifier2 = Modifier()
        modifier2.state = State.offline
        modifier2.context = Context.local
        modifier2.sourceAttributeId = srcAttr.id
        modifier2.operator = Operator.postPercent
        modifier2.targetAttributeId = tgtAttr2.id
        modifier2.location = Location.self_
        modifier2.filterType = None
        modifier2.filterValue = None
        effect = self.ch.effect(effectId=1, categoryId=EffectCategory.passive)
        effect.modifiers = (modifier1, modifier2)
        fit = Fit()
        holder = IndependentItem(self.ch.type_(typeId=1, effects=(effect,), attributes={tgtAttr1.id: 50, tgtAttr2.id: 80,
                                                                                        tgtAttr3.id: 100, srcAttr.id: 20}))
        fit.items.append(holder)
        # First attribute should be modified by modifier1
        self.assertAlmostEqual(holder.attributes[tgtAttr1.id], 60)
        # Second should be modified by modifier2
        self.assertAlmostEqual(holder.attributes[tgtAttr2.id], 96)
        # Third should stay unmodified
        self.assertAlmostEqual(holder.attributes[tgtAttr3.id], 100)
        fit.items.remove(holder)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)
