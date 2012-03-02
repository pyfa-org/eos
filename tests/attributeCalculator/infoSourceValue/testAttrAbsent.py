#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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


from eos.const import State, Location, Context, RunTime, Operator, SourceType
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.fit.attributeCalculator.info.info import Info
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import Fit, IndependentItem


class TestSourceAttrAbsent(AttrCalcTestCase):
    """Test how calculator reacts to source attribute which is absent"""

    def testCombination(self):
        tgtAttr = Attribute(1)
        absAttr = Attribute(2)
        srcAttr = Attribute(3)
        invalidInfo = Info()
        invalidInfo.state = State.offline
        invalidInfo.context = Context.local
        invalidInfo.runTime = RunTime.duration
        invalidInfo.gang = False
        invalidInfo.location = Location.self_
        invalidInfo.filterType = None
        invalidInfo.filterValue = None
        invalidInfo.operator = Operator.postPercent
        invalidInfo.targetAttributeId = tgtAttr.id
        invalidInfo.sourceType = SourceType.attribute
        invalidInfo.sourceValue = absAttr.id
        validInfo = Info()
        validInfo.state = State.offline
        validInfo.context = Context.local
        validInfo.runTime = RunTime.duration
        validInfo.gang = False
        validInfo.location = Location.self_
        validInfo.filterType = None
        validInfo.filterValue = None
        validInfo.operator = Operator.postMul
        validInfo.targetAttributeId = tgtAttr.id
        validInfo.sourceType = SourceType.attribute
        validInfo.sourceValue = srcAttr.id
        effect = Effect(None, EffectCategory.passive)
        effect._infos = (invalidInfo, validInfo)
        fit = Fit({tgtAttr.id: tgtAttr, absAttr.id: absAttr, srcAttr.id: srcAttr})
        holder = IndependentItem(Type(None, effects=(effect,), attributes={srcAttr.id: 1.5, tgtAttr.id: 100}))
        fit.items.append(holder)
        # Invalid source value shouldn't screw whole calculation process
        self.assertNotAlmostEqual(holder.attributes[tgtAttr.id], 100)
        fit.items.remove(holder)
        self.assertBuffersEmpty(fit)
