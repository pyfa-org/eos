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


class TestCleanupChainAddition(EosTestCase):
    """Check that added item damages all attributes which are now relying on its attributes"""

    def testAttribute(self):
        attr1 = Attribute(1)
        attr2 = Attribute(2)
        attr3 = Attribute(3)
        info1 = Info()
        info1.state = State.offline
        info1.context = Context.local
        info1.runTime = RunTime.duration
        info1.gang = False
        info1.location = Location.ship
        info1.filterType = None
        info1.filterValue = None
        info1.operator = Operator.postMul
        info1.targetAttributeId = attr2.id
        info1.sourceType = SourceType.attribute
        info1.sourceValue = attr1.id
        effect1 = Effect(None, EffectCategory.passive)
        effect1._Effect__infos = {info1}
        holder1 = CharacterItem(Type(None, effects={effect1}, attributes={attr1.id: 5}))
        info2 = Info()
        info2.state = State.offline
        info2.context = Context.local
        info2.runTime = RunTime.duration
        info2.gang = False
        info2.location = Location.ship
        info2.filterType = FilterType.all_
        info2.filterValue = None
        info2.operator = Operator.postPercent
        info2.targetAttributeId = attr3.id
        info2.sourceType = SourceType.attribute
        info2.sourceValue = attr2.id
        effect2 = Effect(None, EffectCategory.passive)
        effect2._Effect__infos = {info2}
        holder2 = IndependentItem(Type(None, effects={effect2}, attributes={attr2.id: 7.5}))
        holder3 = ShipItem(Type(None, attributes={attr3.id: 0.5}))
        fit = Fit({attr1.id: attr1, attr2.id: attr2, attr3.id: attr3})
        fit.ship = holder2
        fit._addHolder(holder2)
        fit._addHolder(holder3)
        self.assertAlmostEqual(holder3.attributes[attr3.id], 0.5375)
        fit._addHolder(holder1)
        # Added holder must clean all already calculated attributes
        # which are now affected by it, to allow recalculation
        self.assertAlmostEqual(holder3.attributes[attr3.id], 0.6875)

    def testValue(self):
        attr1 = Attribute(1)
        attr2 = Attribute(2)
        info1 = Info()
        info1.state = State.offline
        info1.context = Context.local
        info1.runTime = RunTime.duration
        info1.gang = False
        info1.location = Location.ship
        info1.filterType = None
        info1.filterValue = None
        info1.operator = Operator.postMul
        info1.targetAttributeId = attr1.id
        info1.sourceType = SourceType.value
        info1.sourceValue = 5
        effect1 = Effect(None, EffectCategory.passive)
        effect1._Effect__infos = {info1}
        holder1 = CharacterItem(Type(None, effects={effect1}))
        info2 = Info()
        info2.state = State.offline
        info2.context = Context.local
        info2.runTime = RunTime.duration
        info2.gang = False
        info2.location = Location.ship
        info2.filterType = FilterType.all_
        info2.filterValue = None
        info2.operator = Operator.postPercent
        info2.targetAttributeId = attr2.id
        info2.sourceType = SourceType.attribute
        info2.sourceValue = attr1.id
        effect2 = Effect(None, EffectCategory.passive)
        effect2._Effect__infos = {info2}
        holder2 = IndependentItem(Type(None, effects={effect2}, attributes={attr1.id: 7.5}))
        holder3 = ShipItem(Type(None, attributes={attr2.id: 0.5}))
        fit = Fit({attr1.id: attr1, attr2.id: attr2})
        fit.ship = holder2
        fit._addHolder(holder2)
        fit._addHolder(holder3)
        self.assertAlmostEqual(holder3.attributes[attr2.id], 0.5375)
        fit._addHolder(holder1)
        # Added holder must clean all attributes depending on its affectors,
        # not only attributes; affectors may use both attributes and 'hardcoded'
        # into them values as data source
        self.assertAlmostEqual(holder3.attributes[attr2.id], 0.6875)
