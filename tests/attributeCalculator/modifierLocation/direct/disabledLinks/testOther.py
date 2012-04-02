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


from eos.const import State, Location, Context, Operator
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.fit.attributeCalculator.modifier.modifier import Modifier
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import Fit, ItemWithOther


class TestLocationDirectOtherSwitch(AttrCalcTestCase):
    """Test direct modification of "other" (e.g. module's charge) when it's changed"""

    def testOther(self):
        tgtAttr = Attribute(1)
        srcAttr = Attribute(2)
        modifier = Modifier()
        modifier.state = State.offline
        modifier.context = Context.local
        modifier.sourceAttributeId = srcAttr.id
        modifier.operator = Operator.postPercent
        modifier.targetAttributeId = tgtAttr.id
        modifier.location = Location.other
        modifier.filterType = None
        modifier.filterValue = None
        effect = Effect(None, EffectCategory.passive)
        effect._modifiers = (modifier,)
        fit = Fit({tgtAttr.id: tgtAttr, srcAttr.id: srcAttr})
        influenceSource = ItemWithOther(Type(None, effects=(effect,), attributes={srcAttr.id: 20}))
        fit.items.append(influenceSource)
        influenceTarget1 = ItemWithOther(Type(None, attributes={tgtAttr.id: 100}))
        influenceSource.makeOtherLink(influenceTarget1)
        fit.items.append(influenceTarget1)
        self.assertNotAlmostEqual(influenceTarget1.attributes[tgtAttr.id], 100)
        fit.items.remove(influenceTarget1)
        influenceSource.breakOtherLink(influenceTarget1)
        influenceTarget2 = ItemWithOther(Type(None, attributes={tgtAttr.id: 100}))
        influenceSource.makeOtherLink(influenceTarget2)
        fit.items.append(influenceTarget2)
        self.assertNotAlmostEqual(influenceTarget2.attributes[tgtAttr.id], 100)
        fit.items.remove(influenceTarget2)
        influenceSource.breakOtherLink(influenceTarget2)
        fit.items.remove(influenceSource)
        self.assertBuffersEmpty(fit)
