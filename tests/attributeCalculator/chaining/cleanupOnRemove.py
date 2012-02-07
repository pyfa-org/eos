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


from unittest import TestCase

from eos.const import State, Location, Context, RunTime, FilterType, Operator, SourceType
from eos.fit.attributeCalculator.info.info import Info
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, CharacterItem, ShipItem


class TestCleanupChainRemoval(TestCase):
    """Check that removed item damages all attributes which were relying on its attributes"""

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
        fit = Fit(lambda attrId: {attr1.id: attr1, attr2.id: attr2,
                                  attr3.id: attr3}[attrId])
        fit._addHolder(holder1)
        fit.ship = holder2
        fit._addHolder(holder2)
        fit._addHolder(holder3)
        expValue = 0.6875
        self.assertAlmostEqual(holder3.attributes[attr3.id], expValue, msg="value must be {}".format(expValue))
        fit._removeHolder(holder1)
        # When holder1 is removed, attr2 of holder2 and attr3 of holder3
        # must be cleaned to allow recalculation of attr3 based on new data
        expValue = 0.5375
        self.assertAlmostEqual(holder3.attributes[attr3.id], expValue, msg="value must be {}".format(expValue))

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
        fit = Fit(lambda attrId: {attr1.id: attr1, attr2.id: attr2}[attrId])
        fit._addHolder(holder1)
        fit.ship = holder2
        fit._addHolder(holder2)
        fit._addHolder(holder3)
        expValue = 0.6875
        self.assertAlmostEqual(holder3.attributes[attr2.id], expValue, msg="value must be {}".format(expValue))
        fit._removeHolder(holder1)
        # This test is almost the same as previous, but holder1 uses info itself
        # as data source; we need to check this special case to avoid attribute
        # "damaging" based on attributes of holder being removed; if it were the
        # case, target attribute on holder3 wouldn't be damaged. Proper way is to
        # rely on affectors of holder removed.
        expValue = 0.5375
        self.assertAlmostEqual(holder3.attributes[attr2.id], expValue, msg="value must be {}".format(expValue))
