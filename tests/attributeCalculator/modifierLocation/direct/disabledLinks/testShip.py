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


class TestLocationDirectShipSwitch(AttrCalcTestCase):
    """Test direct modification of ship when it's changed"""

    def testShip(self):
        tgtAttr = self.ch.attribute(attributeId=1)
        srcAttr = self.ch.attribute(attributeId=2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.context = Context.local
        modifier.sourceAttributeId = srcAttr.id
        modifier.operator = Operator.postPercent
        modifier.targetAttributeId = tgtAttr.id
        modifier.location = Location.ship
        modifier.filterType = None
        modifier.filterValue = None
        effect = self.ch.effect(effectId=1, categoryId=EffectCategory.passive)
        effect._modifiers = (modifier,)
        fit = Fit()
        influenceSource = IndependentItem(self.ch.type_(typeId=1, effects=(effect,), attributes={srcAttr.id: 20}))
        fit.items.append(influenceSource)
        item = self.ch.type_(typeId=None, attributes={tgtAttr.id: 100})
        influenceTarget1 = IndependentItem(item)
        fit.ship = influenceTarget1
        self.assertNotAlmostEqual(influenceTarget1.attributes[tgtAttr.id], 100)
        fit.ship = None
        influenceTarget2 = IndependentItem(item)
        fit.ship = influenceTarget2
        self.assertNotAlmostEqual(influenceTarget2.attributes[tgtAttr.id], 100)
        fit.items.remove(influenceSource)
        fit.ship = None
        self.assertBuffersEmpty(fit)
