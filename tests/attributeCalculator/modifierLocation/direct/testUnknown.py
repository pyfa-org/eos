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


from eos.const.eos import State, Location, Context, Operator
from eos.const.eve import EffectCategory
from eos.data.cache.object.modifier import Modifier
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import Fit, IndependentItem
from eos.tests.environment import Logger


class TestLocationDirectUnknown(AttrCalcTestCase):
    """Test reaction to unknown location specification for direct modification"""

    def setUp(self):
        AttrCalcTestCase.setUp(self)
        self.tgtAttr = self.ch.attribute(attributeId=1)
        self.srcAttr = self.ch.attribute(attributeId=2)
        self.invalidModifier = invalidModifier = Modifier()
        invalidModifier.state = State.offline
        invalidModifier.context = Context.local
        invalidModifier.sourceAttributeId = self.srcAttr.id
        invalidModifier.operator = Operator.postPercent
        invalidModifier.targetAttributeId = self.tgtAttr.id
        invalidModifier.location = 1972
        invalidModifier.filterType = None
        invalidModifier.filterValue = None
        self.effect = self.ch.effect(effectId=1, categoryId=EffectCategory.passive)
        self.fit = Fit()

    def testLog(self):
        self.effect.modifiers = (self.invalidModifier,)
        holder = IndependentItem(self.ch.type_(typeId=754, effects=(self.effect,), attributes={self.srcAttr.id: 20}))
        self.fit.items.add(holder)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.attributeCalculator')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, 'malformed modifier on item 754: unsupported target location 1972 for direct modification')
        self.fit.items.remove(holder)
        self.assertBuffersEmpty(self.fit)

    def testCombination(self):
        validModifier = Modifier()
        validModifier.state = State.offline
        validModifier.context = Context.local
        validModifier.sourceAttributeId = self.srcAttr.id
        validModifier.operator = Operator.postPercent
        validModifier.targetAttributeId = self.tgtAttr.id
        validModifier.location = Location.self_
        validModifier.filterType = None
        validModifier.filterValue = None
        self.effect.modifiers = (self.invalidModifier, validModifier)
        holder = IndependentItem(self.ch.type_(typeId=1, effects=(self.effect,), attributes={self.srcAttr.id: 20, self.tgtAttr.id: 100}))
        self.fit.items.add(holder)
        # Invalid location in modifier should prevent proper processing of other modifiers
        self.assertNotAlmostEqual(holder.attributes[self.tgtAttr.id], 100)
        self.fit.items.remove(holder)
        self.assertEqual(len(self.log), 1)
        self.assertBuffersEmpty(self.fit)
