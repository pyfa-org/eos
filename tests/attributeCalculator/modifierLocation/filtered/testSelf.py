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
from eos.tests.environment import Logger


class TestLocationFilterSelf(AttrCalcTestCase):
    """Test location.self (self-reference) for massive filtered modifications"""

    def setUp(self):
        AttrCalcTestCase.setUp(self)
        self.tgtAttr = self.ch.attribute(attributeId=1)
        srcAttr = self.ch.attribute(attributeId=2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.context = Context.local
        modifier.sourceAttributeId = srcAttr.id
        modifier.operator = Operator.postPercent
        modifier.targetAttributeId = self.tgtAttr.id
        modifier.location = Location.self_
        modifier.filterType = FilterType.all_
        modifier.filterValue = None
        effect = self.ch.effect(effectId=1, categoryId=EffectCategory.passive)
        effect._modifiers = (modifier,)
        self.fit = Fit()
        self.influenceSource = IndependentItem(self.ch.type_(typeId=1061, effects=(effect,), attributes={srcAttr.id: 20}))

    def testShip(self):
        self.fit.ship = self.influenceSource
        influenceTarget = ShipItem(self.ch.type_(typeId=1, attributes={self.tgtAttr.id: 100}))
        self.fit.items.append(influenceTarget)
        self.assertNotAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.ship = None
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(influenceTarget)
        self.assertBuffersEmpty(self.fit)

    def testCharacter(self):
        self.fit.character = self.influenceSource
        influenceTarget = CharacterItem(self.ch.type_(typeId=1, attributes={self.tgtAttr.id: 100}))
        self.fit.items.append(influenceTarget)
        self.assertNotAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.character = None
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(influenceTarget)
        self.assertBuffersEmpty(self.fit)

    def testUnpositionedError(self):
        # Here we do not position holder in fit, this way attribute
        # calculator won't know that source is 'owner' of some location
        # and will log corresponding error
        self.fit.items.append(self.influenceSource)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.attributeCalculator")
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, "malformed modifier on item 1061: invalid reference to self for filtered modification")
        self.fit.items.remove(self.influenceSource)
        self.assertBuffersEmpty(self.fit)
