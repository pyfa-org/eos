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


from eos.const import State, Location, Context, RunTime, FilterType, Operator, SourceType
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.fit.attributeCalculator.info.info import Info
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, CharacterItem, ShipItem
from eos.tests.eosTestCase import EosTestCase


class TestCalculationChain(EosTestCase):
    """Check that calculation process uses modified attributes as data source"""

    def testCalculation(self):
        attr1 = Attribute(1)
        attr2 = Attribute(2)
        attr3 = Attribute(3)
        attr4 = Attribute(4)
        info1 = Info()
        info1.state = State.offline
        info1.context = Context.local
        info1.runTime = RunTime.duration
        info1.gang = False
        info1.location = Location.self_
        info1.filterType = None
        info1.filterValue = None
        info1.operator = Operator.postMul
        info1.targetAttributeId = attr2.id
        info1.sourceType = SourceType.attribute
        info1.sourceValue = attr1.id
        effect1 = Effect(None, EffectCategory.passive)
        effect1._Effect__infos = {info1}
        info2 = Info()
        info2.state = State.offline
        info2.context = Context.local
        info2.runTime = RunTime.duration
        info2.gang = False
        info2.location = Location.ship
        info2.filterType = None
        info2.filterValue = None
        info2.operator = Operator.postPercent
        info2.targetAttributeId = attr3.id
        info2.sourceType = SourceType.attribute
        info2.sourceValue = attr2.id
        effect2 = Effect(None, EffectCategory.passive)
        effect2._Effect__infos = {info2}
        holder1 = CharacterItem(Type(None, effects={effect1, effect2}, attributes={attr1.id: 5, attr2.id: 20}))
        info3 = Info()
        info3.state = State.offline
        info3.context = Context.local
        info3.runTime = RunTime.duration
        info3.gang = False
        info3.location = Location.ship
        info3.filterType = FilterType.all_
        info3.filterValue = None
        info3.operator = Operator.postPercent
        info3.targetAttributeId = attr4.id
        info3.sourceType = SourceType.attribute
        info3.sourceValue = attr3.id
        effect3 = Effect(None, EffectCategory.passive)
        effect3._Effect__infos = {info3}
        holder2 = IndependentItem(Type(None, effects={effect3}, attributes={attr3.id: 150}))
        holder3 = ShipItem(Type(None, attributes={attr4.id: 12.5}))
        fit = Fit({attr1.id: attr1, attr2.id: attr2, attr3.id: attr3, attr4.id: attr4})
        fit._addHolder(holder1)
        fit.ship = holder2
        fit._addHolder(holder2)
        fit._addHolder(holder3)
        # If everything is processed properly, holder1 will multiply attr2 by attr1
        # on self, resulting in 20 * 5 = 100, then apply it as percentage modifier
        # on ship's (holder2) attr3, resulting in 150 + 100% = 300, then it is applied
        # to all entities assigned to ship, including holder3, to theirs attr4 as
        # percentage modifier again - so final result is 12.5 + 300% = 50
        self.assertAlmostEqual(holder3.attributes[attr4.id], 50)
