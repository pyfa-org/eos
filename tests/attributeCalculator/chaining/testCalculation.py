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


from eos.const import State, Location, Context, FilterType, Operator
from eos.eve.const import EffectCategory
from eos.fit.attributeCalculator.modifier.modifier import Modifier
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, CharacterItem, ShipItem


class TestCalculationChain(AttrCalcTestCase):
    """Check that calculation process uses modified attributes as data source"""

    def testCalculation(self):
        attr1 = self.ch.attribute(attributeId=1)
        attr2 = self.ch.attribute(attributeId=2)
        attr3 = self.ch.attribute(attributeId=3)
        attr4 = self.ch.attribute(attributeId=4)
        modifier1 = Modifier()
        modifier1.state = State.offline
        modifier1.context = Context.local
        modifier1.sourceAttributeId = attr1.id
        modifier1.operator = Operator.postMul
        modifier1.targetAttributeId = attr2.id
        modifier1.location = Location.self_
        modifier1.filterType = None
        modifier1.filterValue = None
        effect1 = self.ch.effect(effectId=1, categoryId=EffectCategory.passive)
        effect1._modifiers = (modifier1,)
        modifier2 = Modifier()
        modifier2.state = State.offline
        modifier2.context = Context.local
        modifier2.sourceAttributeId = attr2.id
        modifier2.operator = Operator.postPercent
        modifier2.targetAttributeId = attr3.id
        modifier2.location = Location.ship
        modifier2.filterType = None
        modifier2.filterValue = None
        effect2 = self.ch.effect(effectId=2, categoryId=EffectCategory.passive)
        effect2._modifiers = (modifier2,)
        holder1 = CharacterItem(self.ch.type_(typeId=1, effects=(effect1, effect2), attributes={attr1.id: 5, attr2.id: 20}))
        modifier3 = Modifier()
        modifier3.state = State.offline
        modifier3.context = Context.local
        modifier3.sourceAttributeId = attr3.id
        modifier3.operator = Operator.postPercent
        modifier3.targetAttributeId = attr4.id
        modifier3.location = Location.ship
        modifier3.filterType = FilterType.all_
        modifier3.filterValue = None
        effect3 = self.ch.effect(effectId=3, categoryId=EffectCategory.passive)
        effect3._modifiers = (modifier3,)
        holder2 = IndependentItem(self.ch.type_(typeId=2, effects=(effect3,), attributes={attr3.id: 150}))
        holder3 = ShipItem(self.ch.type_(typeId=3, attributes={attr4.id: 12.5}))
        fit = Fit()
        fit.items.append(holder1)
        fit.ship = holder2
        fit.items.append(holder3)
        # If everything is processed properly, holder1 will multiply attr2 by attr1
        # on self, resulting in 20 * 5 = 100, then apply it as percentage modifier
        # on ship's (holder2) attr3, resulting in 150 + 100% = 300, then it is applied
        # to all entities assigned to ship, including holder3, to theirs attr4 as
        # percentage modifier again - so final result is 12.5 + 300% = 50
        self.assertAlmostEqual(holder3.attributes[attr4.id], 50)
        fit.items.remove(holder1)
        fit.ship = None
        fit.items.remove(holder3)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)
