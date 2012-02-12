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
from eos.fit.attributeCalculator.info.info import Info
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.tests.attributeCalculator.environment import Fit, IndependentItem
from eos.tests.eosTestCase import EosTestCase


class TestTargetAttribute(EosTestCase):
    """Test that only targeted attributes are modified"""

    def testTargetAttributes(self):
        tgtAttr1 = Attribute(1)
        tgtAttr2 = Attribute(2)
        tgtAttr3 = Attribute(3)
        srcAttr = Attribute(4)
        info1 = Info()
        info1.state = State.offline
        info1.context = Context.local
        info1.runTime = RunTime.duration
        info1.gang = False
        info1.location = Location.self_
        info1.filterType = None
        info1.filterValue = None
        info1.operator = Operator.postPercent
        info1.targetAttributeId = tgtAttr1.id
        info1.sourceType = SourceType.attribute
        info1.sourceValue = srcAttr.id
        info2 = Info()
        info2.state = State.offline
        info2.context = Context.local
        info2.runTime = RunTime.duration
        info2.gang = False
        info2.location = Location.self_
        info2.filterType = None
        info2.filterValue = None
        info2.operator = Operator.postPercent
        info2.targetAttributeId = tgtAttr2.id
        info2.sourceType = SourceType.attribute
        info2.sourceValue = srcAttr.id
        effect = Effect(None, EffectCategory.passive)
        effect._Effect__infos = {info1, info2}
        fit = Fit({tgtAttr1.id: tgtAttr1, tgtAttr2.id: tgtAttr2, tgtAttr3.id: tgtAttr3, srcAttr.id: srcAttr})
        holder = IndependentItem(Type(None, effects={effect}, attributes={tgtAttr1.id: 50, tgtAttr2.id: 80,
                                                                          tgtAttr3.id: 100, srcAttr.id: 20}))
        fit._addHolder(holder)
        # First attribute should be modified by info1
        expValue = 60
        self.assertAlmostEqual(holder.attributes[tgtAttr1.id], expValue, msg="value must be {}".format(expValue))
        # Second should be modified by info2
        expValue = 96
        # Third should stay unmodified
        self.assertAlmostEqual(holder.attributes[tgtAttr2.id], expValue, msg="value must be {}".format(expValue))
        expValue = 100
        self.assertAlmostEqual(holder.attributes[tgtAttr3.id], expValue, msg="value must be {}".format(expValue))
