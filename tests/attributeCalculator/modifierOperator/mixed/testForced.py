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
from eos.data.cache.object.modifier import Modifier
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import IndependentItem, ShipItem


class TestOperatorForcedValue(AttrCalcTestCase):
    """Test that post-assignment forces value of attribute"""

    def testForcedValue(self):
        tgtAttr = self.ch.attribute(attributeId=1)
        srcAttr = self.ch.attribute(attributeId=2)
        modifierPreAss = Modifier()
        modifierPreAss.state = State.offline
        modifierPreAss.context = Context.local
        modifierPreAss.sourceAttributeId = srcAttr.id
        modifierPreAss.operator = Operator.preAssignment
        modifierPreAss.targetAttributeId = tgtAttr.id
        modifierPreAss.location = Location.ship
        modifierPreAss.filterType = FilterType.all_
        modifierPreAss.filterValue = None
        effectPreAss = self.ch.effect(effectId=1, categoryId=EffectCategory.passive)
        effectPreAss.modifiers = (modifierPreAss,)
        influenceSourcePreAss = IndependentItem(self.ch.type_(typeId=1, effects=(effectPreAss,), attributes={srcAttr.id: 5}))
        self.fit.items.add(influenceSourcePreAss)
        modifierPreMul = Modifier()
        modifierPreMul.state = State.offline
        modifierPreMul.context = Context.local
        modifierPreMul.sourceAttributeId = srcAttr.id
        modifierPreMul.operator = Operator.preMul
        modifierPreMul.targetAttributeId = tgtAttr.id
        modifierPreMul.location = Location.ship
        modifierPreMul.filterType = FilterType.all_
        modifierPreMul.filterValue = None
        effectPreMul = self.ch.effect(effectId=2, categoryId=EffectCategory.passive)
        effectPreMul.modifiers = (modifierPreMul,)
        influenceSourcePreMul = IndependentItem(self.ch.type_(typeId=2, effects=(effectPreMul,), attributes={srcAttr.id: 50}))
        self.fit.items.add(influenceSourcePreMul)
        modifierPreDiv = Modifier()
        modifierPreDiv.state = State.offline
        modifierPreDiv.context = Context.local
        modifierPreDiv.sourceAttributeId = srcAttr.id
        modifierPreDiv.operator = Operator.preDiv
        modifierPreDiv.targetAttributeId = tgtAttr.id
        modifierPreDiv.location = Location.ship
        modifierPreDiv.filterType = FilterType.all_
        modifierPreDiv.filterValue = None
        effectPreDiv = self.ch.effect(effectId=3, categoryId=EffectCategory.passive)
        effectPreDiv.modifiers = (modifierPreDiv,)
        influenceSourcePreDiv = IndependentItem(self.ch.type_(typeId=3, effects=(effectPreDiv,), attributes={srcAttr.id: 0.5}))
        self.fit.items.add(influenceSourcePreDiv)
        modifierModAdd = Modifier()
        modifierModAdd.state = State.offline
        modifierModAdd.context = Context.local
        modifierModAdd.sourceAttributeId = srcAttr.id
        modifierModAdd.operator = Operator.modAdd
        modifierModAdd.targetAttributeId = tgtAttr.id
        modifierModAdd.location = Location.ship
        modifierModAdd.filterType = FilterType.all_
        modifierModAdd.filterValue = None
        effectModAdd = self.ch.effect(effectId=4, categoryId=EffectCategory.passive)
        effectModAdd.modifiers = (modifierModAdd,)
        influenceSourceModAdd = IndependentItem(self.ch.type_(typeId=4, effects=(effectModAdd,), attributes={srcAttr.id: 10}))
        self.fit.items.add(influenceSourceModAdd)
        modifierModSub = Modifier()
        modifierModSub.state = State.offline
        modifierModSub.context = Context.local
        modifierModSub.sourceAttributeId = srcAttr.id
        modifierModSub.operator = Operator.modSub
        modifierModSub.targetAttributeId = tgtAttr.id
        modifierModSub.location = Location.ship
        modifierModSub.filterType = FilterType.all_
        modifierModSub.filterValue = None
        effectModSub = self.ch.effect(effectId=5, categoryId=EffectCategory.passive)
        effectModSub.modifiers = (modifierModSub,)
        influenceSourceModSub = IndependentItem(self.ch.type_(typeId=5, effects=(effectModSub,), attributes={srcAttr.id: 63}))
        self.fit.items.add(influenceSourceModSub)
        modifierPostMul = Modifier()
        modifierPostMul.state = State.offline
        modifierPostMul.context = Context.local
        modifierPostMul.sourceAttributeId = srcAttr.id
        modifierPostMul.operator = Operator.postMul
        modifierPostMul.targetAttributeId = tgtAttr.id
        modifierPostMul.location = Location.ship
        modifierPostMul.filterType = FilterType.all_
        modifierPostMul.filterValue = None
        effectPostMul = self.ch.effect(effectId=6, categoryId=EffectCategory.passive)
        effectPostMul.modifiers = (modifierPostMul,)
        influenceSourcePostMul = IndependentItem(self.ch.type_(typeId=6, effects=(effectPostMul,), attributes={srcAttr.id: 1.35}))
        self.fit.items.add(influenceSourcePostMul)
        modifierPostDiv = Modifier()
        modifierPostDiv.state = State.offline
        modifierPostDiv.context = Context.local
        modifierPostDiv.sourceAttributeId = srcAttr.id
        modifierPostDiv.operator = Operator.postDiv
        modifierPostDiv.targetAttributeId = tgtAttr.id
        modifierPostDiv.location = Location.ship
        modifierPostDiv.filterType = FilterType.all_
        modifierPostDiv.filterValue = None
        effectPostDiv = self.ch.effect(effectId=7, categoryId=EffectCategory.passive)
        effectPostDiv.modifiers = (modifierPostDiv,)
        influenceSourcePostDiv = IndependentItem(self.ch.type_(typeId=7, effects=(effectPostDiv,), attributes={srcAttr.id: 2.7}))
        self.fit.items.add(influenceSourcePostDiv)
        modifierPostPerc = Modifier()
        modifierPostPerc.state = State.offline
        modifierPostPerc.context = Context.local
        modifierPostPerc.sourceAttributeId = srcAttr.id
        modifierPostPerc.operator = Operator.postPercent
        modifierPostPerc.targetAttributeId = tgtAttr.id
        modifierPostPerc.location = Location.ship
        modifierPostPerc.filterType = FilterType.all_
        modifierPostPerc.filterValue = None
        effectPostPerc = self.ch.effect(effectId=8, categoryId=EffectCategory.passive)
        effectPostPerc.modifiers = (modifierPostPerc,)
        influenceSourcePostPerc = IndependentItem(self.ch.type_(typeId=8, effects=(effectPostPerc,), attributes={srcAttr.id: 15}))
        self.fit.items.add(influenceSourcePostPerc)
        modifierPostAss = Modifier()
        modifierPostAss.state = State.offline
        modifierPostAss.context = Context.local
        modifierPostAss.sourceAttributeId = srcAttr.id
        modifierPostAss.operator = Operator.postAssignment
        modifierPostAss.targetAttributeId = tgtAttr.id
        modifierPostAss.location = Location.ship
        modifierPostAss.filterType = FilterType.all_
        modifierPostAss.filterValue = None
        effectPostAss = self.ch.effect(effectId=9, categoryId=EffectCategory.passive)
        effectPostAss.modifiers = (modifierPostAss,)
        influenceSourcePostAss = IndependentItem(self.ch.type_(typeId=9, effects=(effectPostAss,), attributes={srcAttr.id: 68}))
        self.fit.items.add(influenceSourcePostAss)
        influenceTarget = ShipItem(self.ch.type_(typeId=10, attributes={tgtAttr.id: 100}))
        self.fit.items.add(influenceTarget)
        # Post-assignment value must override all other modifications
        self.assertAlmostEqual(influenceTarget.attributes[tgtAttr.id], 68)
        self.fit.items.remove(influenceSourcePreAss)
        self.fit.items.remove(influenceSourcePreMul)
        self.fit.items.remove(influenceSourcePreDiv)
        self.fit.items.remove(influenceSourceModAdd)
        self.fit.items.remove(influenceSourceModSub)
        self.fit.items.remove(influenceSourcePostMul)
        self.fit.items.remove(influenceSourcePostDiv)
        self.fit.items.remove(influenceSourcePostPerc)
        self.fit.items.remove(influenceSourcePostAss)
        self.fit.items.remove(influenceTarget)
        self.assertEqual(len(self.log), 0)
        self.assertLinkBuffersEmpty(self.fit)
