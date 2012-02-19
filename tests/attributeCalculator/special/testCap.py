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
from eos.tests.attributeCalculator.environment import Fit, IndependentItem
from eos.tests.eosTestCase import EosTestCase


class TestCap(EosTestCase):
    """Test return value when requesting attribute which isn't set"""

    def testValue(self):
        srcAttr = Attribute(1)
        tgtAttr = Attribute(2, maxAttributeId=3)
        capAttr = Attribute(3, defaultValue=5.2)
        # Just to make sure cap is applied to final value, not
        # base, make some basic modification info
        info = Info()
        info.state = State.offline
        info.context = Context.local
        info.runTime = RunTime.duration
        info.gang = False
        info.location = Location.self_
        info.filterType = None
        info.filterValue = None
        info.operator = Operator.postMul
        info.targetAttributeId = tgtAttr.id
        info.sourceType = SourceType.attribute
        info.sourceValue = srcAttr.id
        effect = Effect(None, EffectCategory.passive)
        effect._Effect__infos = {info}
        fit = Fit({srcAttr.id: srcAttr, tgtAttr.id: tgtAttr, capAttr.id: capAttr})
        holder = IndependentItem(Type(None, effects={effect}, attributes={tgtAttr.id: 3, srcAttr.id: 6}))
        fit._addHolder(holder)
        # Attribute should be capped at 5.2
        self.assertAlmostEqual(holder.attributes[tgtAttr.id], 5.2)
