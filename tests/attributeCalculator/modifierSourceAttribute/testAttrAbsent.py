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


from eos.const import State, Location, Context, Operator
from eos.eve.const import EffectCategory
from eos.fit.attributeCalculator.modifier.modifier import Modifier
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import Fit, IndependentItem


class TestSourceAttrAbsent(AttrCalcTestCase):
    """Test how calculator reacts to source attribute which is absent"""

    def testCombination(self):
        tgtAttr = self.ch.attribute(attributeId=1)
        absAttr = self.ch.attribute(attributeId=2)
        srcAttr = self.ch.attribute(attributeId=3)
        invalidModifier = Modifier()
        invalidModifier.state = State.offline
        invalidModifier.context = Context.local
        invalidModifier.sourceAttributeId = absAttr.id
        invalidModifier.operator = Operator.postPercent
        invalidModifier.targetAttributeId = tgtAttr.id
        invalidModifier.location = Location.self_
        invalidModifier.filterType = None
        invalidModifier.filterValue = None
        validModifier = Modifier()
        validModifier.state = State.offline
        validModifier.context = Context.local
        validModifier.sourceAttributeId = srcAttr.id
        validModifier.operator = Operator.postMul
        validModifier.targetAttributeId = tgtAttr.id
        validModifier.location = Location.self_
        validModifier.filterType = None
        validModifier.filterValue = None
        effect = self.ch.effect(effectId=1, categoryId=EffectCategory.passive)
        effect._modifiers = (invalidModifier, validModifier)
        fit = Fit()
        holder = IndependentItem(self.ch.type_(typeId=1, effects=(effect,), attributes={srcAttr.id: 1.5, tgtAttr.id: 100}))
        fit.items.append(holder)
        # Invalid source value shouldn't screw whole calculation process
        self.assertNotAlmostEqual(holder.attributes[tgtAttr.id], 100)
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)
