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
from eos.tests.attributeCalculator.environment import ItemWithOther


class TestLocationDirectOtherSwitch(AttrCalcTestCase):
    """Test direct modification of "other" (e.g. module's charge) when it's changed"""

    def testOther(self):
        tgtAttr = self.ch.attribute(attributeId=1)
        srcAttr = self.ch.attribute(attributeId=2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.context = Context.local
        modifier.sourceAttributeId = srcAttr.id
        modifier.operator = Operator.postPercent
        modifier.targetAttributeId = tgtAttr.id
        modifier.location = Location.other
        modifier.filterType = None
        modifier.filterValue = None
        effect = self.ch.effect(effectId=1, categoryId=EffectCategory.passive)
        effect.modifiers = (modifier,)
        influenceSource = ItemWithOther(self.ch.type_(typeId=1, effects=(effect,), attributes={srcAttr.id: 20}))
        self.fit.items.add(influenceSource)
        item = self.ch.type_(typeId=2, attributes={tgtAttr.id: 100})
        influenceTarget1 = ItemWithOther(item)
        influenceSource.makeOtherLink(influenceTarget1)
        self.fit.items.add(influenceTarget1)
        self.assertNotAlmostEqual(influenceTarget1.attributes[tgtAttr.id], 100)
        self.fit.items.remove(influenceTarget1)
        influenceSource.breakOtherLink(influenceTarget1)
        influenceTarget2 = ItemWithOther(item)
        influenceSource.makeOtherLink(influenceTarget2)
        self.fit.items.add(influenceTarget2)
        self.assertNotAlmostEqual(influenceTarget2.attributes[tgtAttr.id], 100)
        self.fit.items.remove(influenceTarget2)
        influenceSource.breakOtherLink(influenceTarget2)
        self.fit.items.remove(influenceSource)
        self.assertEqual(len(self.log), 0)
        self.assertBuffersEmpty(self.fit)
