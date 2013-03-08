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


from eos.const.eos import State, Location, Context, FilterType, Operator
from eos.const.eve import EffectCategory
from eos.eve.modifier import Modifier
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, CharacterItem, ShipItem


class TestCleanupChainAddition(AttrCalcTestCase):
    """Check that added item damages all attributes which are now relying on its attributes"""

    def testAttribute(self):
        attr1 = self.ch.attribute(attributeId=1)
        attr2 = self.ch.attribute(attributeId=2)
        attr3 = self.ch.attribute(attributeId=3)
        modifier1 = Modifier()
        modifier1.state = State.offline
        modifier1.context = Context.local
        modifier1.sourceAttributeId = attr1.id
        modifier1.operator = Operator.postMul
        modifier1.targetAttributeId = attr2.id
        modifier1.location = Location.ship
        modifier1.filterType = None
        modifier1.filterValue = None
        effect1 = self.ch.effect(effectId=1, categoryId=EffectCategory.passive)
        effect1.modifiers = (modifier1,)
        holder1 = CharacterItem(self.ch.type_(typeId=1, effects=(effect1,), attributes={attr1.id: 5}))
        modifier2 = Modifier()
        modifier2.state = State.offline
        modifier2.context = Context.local
        modifier2.sourceAttributeId = attr2.id
        modifier2.operator = Operator.postPercent
        modifier2.targetAttributeId = attr3.id
        modifier2.location = Location.ship
        modifier2.filterType = FilterType.all_
        modifier2.filterValue = None
        effect2 = self.ch.effect(effectId=2, categoryId=EffectCategory.passive)
        effect2.modifiers = (modifier2,)
        holder2 = IndependentItem(self.ch.type_(typeId=2, effects=(effect2,), attributes={attr2.id: 7.5}))
        holder3 = ShipItem(self.ch.type_(typeId=3, attributes={attr3.id: 0.5}))
        fit = Fit()
        fit.ship = holder2
        fit.items.append(holder3)
        self.assertAlmostEqual(holder3.attributes[attr3.id], 0.5375)
        fit.items.append(holder1)
        # Added holder must clean all already calculated attributes
        # which are now affected by it, to allow recalculation
        self.assertAlmostEqual(holder3.attributes[attr3.id], 0.6875)
        fit.items.remove(holder1)
        fit.ship = None
        fit.items.remove(holder3)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(fit)
