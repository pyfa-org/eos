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


from eos.const import State, Location, Context, FilterType, Operator
from eos.eve.const import EffectCategory
from eos.fit.attributeCalculator.modifier.modifier import Modifier
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, ShipItem


class TestOperatorAllIn(AttrCalcTestCase):
    """Test interaction of all operators, besides post-assignment"""

    def testAllIn(self):
        tgtAttr = self.dh.attribute(attributeId=1, stackable=0)
        srcAttr = self.dh.attribute(attributeId=2)
        fit = Fit()
        modifierPreAss = Modifier()
        modifierPreAss.state = State.offline
        modifierPreAss.context = Context.local
        modifierPreAss.sourceAttributeId = srcAttr.id
        modifierPreAss.operator = Operator.preAssignment
        modifierPreAss.targetAttributeId = tgtAttr.id
        modifierPreAss.location = Location.ship
        modifierPreAss.filterType = FilterType.all_
        modifierPreAss.filterValue = None
        effectPreAss = self.dh.effect(effectId=1, categoryId=EffectCategory.passive)
        effectPreAss._modifiers = (modifierPreAss,)
        valuePreAss = 5
        influenceSourcePreAss = IndependentItem(self.dh.type_(typeId=1, effects=(effectPreAss,), attributes={srcAttr.id: valuePreAss}))
        fit.items.append(influenceSourcePreAss)
        modifierPreMul = Modifier()
        modifierPreMul.state = State.offline
        modifierPreMul.context = Context.local
        modifierPreMul.sourceAttributeId = srcAttr.id
        modifierPreMul.operator = Operator.preMul
        modifierPreMul.targetAttributeId = tgtAttr.id
        modifierPreMul.location = Location.ship
        modifierPreMul.filterType = FilterType.all_
        modifierPreMul.filterValue = None
        effectPreMul = self.dh.effect(effectId=2, categoryId=EffectCategory.passive)
        effectPreMul._modifiers = (modifierPreMul,)
        valuePreMul = 50
        influenceSourcePreMul = IndependentItem(self.dh.type_(typeId=2, effects=(effectPreMul,), attributes={srcAttr.id: valuePreMul}))
        fit.items.append(influenceSourcePreMul)
        modifierPreDiv = Modifier()
        modifierPreDiv.state = State.offline
        modifierPreDiv.context = Context.local
        modifierPreDiv.sourceAttributeId = srcAttr.id
        modifierPreDiv.operator = Operator.preDiv
        modifierPreDiv.targetAttributeId = tgtAttr.id
        modifierPreDiv.location = Location.ship
        modifierPreDiv.filterType = FilterType.all_
        modifierPreDiv.filterValue = None
        effectPreDiv = self.dh.effect(effectId=3, categoryId=EffectCategory.passive)
        effectPreDiv._modifiers = (modifierPreDiv,)
        valuePreDiv = 0.5
        influenceSourcePreDiv = IndependentItem(self.dh.type_(typeId=3, effects=(effectPreDiv,), attributes={srcAttr.id: valuePreDiv}))
        fit.items.append(influenceSourcePreDiv)
        modifierModAdd = Modifier()
        modifierModAdd.state = State.offline
        modifierModAdd.context = Context.local
        modifierModAdd.sourceAttributeId = srcAttr.id
        modifierModAdd.operator = Operator.modAdd
        modifierModAdd.targetAttributeId = tgtAttr.id
        modifierModAdd.location = Location.ship
        modifierModAdd.filterType = FilterType.all_
        modifierModAdd.filterValue = None
        effectModAdd = self.dh.effect(effectId=4, categoryId=EffectCategory.passive)
        effectModAdd._modifiers = (modifierModAdd,)
        valueModAdd = 10
        influenceSourceModAdd = IndependentItem(self.dh.type_(typeId=4, effects=(effectModAdd,), attributes={srcAttr.id: valueModAdd}))
        fit.items.append(influenceSourceModAdd)
        modifierModSub = Modifier()
        modifierModSub.state = State.offline
        modifierModSub.context = Context.local
        modifierModSub.sourceAttributeId = srcAttr.id
        modifierModSub.operator = Operator.modSub
        modifierModSub.targetAttributeId = tgtAttr.id
        modifierModSub.location = Location.ship
        modifierModSub.filterType = FilterType.all_
        modifierModSub.filterValue = None
        effectModSub = self.dh.effect(effectId=5, categoryId=EffectCategory.passive)
        effectModSub._modifiers = (modifierModSub,)
        valueModSub = 63
        influenceSourceModSub = IndependentItem(self.dh.type_(typeId=5, effects=(effectModSub,), attributes={srcAttr.id: valueModSub}))
        fit.items.append(influenceSourceModSub)
        modifierPostMul = Modifier()
        modifierPostMul.state = State.offline
        modifierPostMul.context = Context.local
        modifierPostMul.sourceAttributeId = srcAttr.id
        modifierPostMul.operator = Operator.postMul
        modifierPostMul.targetAttributeId = tgtAttr.id
        modifierPostMul.location = Location.ship
        modifierPostMul.filterType = FilterType.all_
        modifierPostMul.filterValue = None
        effectPostMul = self.dh.effect(effectId=6, categoryId=EffectCategory.passive)
        effectPostMul._modifiers = (modifierPostMul,)
        valuePostMul = 1.35
        influenceSourcePostMul = IndependentItem(self.dh.type_(typeId=6, effects=(effectPostMul,), attributes={srcAttr.id: valuePostMul}))
        fit.items.append(influenceSourcePostMul)
        modifierPostDiv = Modifier()
        modifierPostDiv.state = State.offline
        modifierPostDiv.context = Context.local
        modifierPostDiv.sourceAttributeId = srcAttr.id
        modifierPostDiv.operator = Operator.postDiv
        modifierPostDiv.targetAttributeId = tgtAttr.id
        modifierPostDiv.location = Location.ship
        modifierPostDiv.filterType = FilterType.all_
        modifierPostDiv.filterValue = None
        effectPostDiv = self.dh.effect(effectId=7, categoryId=EffectCategory.passive)
        effectPostDiv._modifiers = (modifierPostDiv,)
        valuePostDiv = 2.7
        influenceSourcePostDiv = IndependentItem(self.dh.type_(typeId=7, effects=(effectPostDiv,), attributes={srcAttr.id: valuePostDiv}))
        fit.items.append(influenceSourcePostDiv)
        modifierPostPerc = Modifier()
        modifierPostPerc.state = State.offline
        modifierPostPerc.context = Context.local
        modifierPostPerc.sourceAttributeId = srcAttr.id
        modifierPostPerc.operator = Operator.postPercent
        modifierPostPerc.targetAttributeId = tgtAttr.id
        modifierPostPerc.location = Location.ship
        modifierPostPerc.filterType = FilterType.all_
        modifierPostPerc.filterValue = None
        effectPostPerc = self.dh.effect(effectId=8, categoryId=EffectCategory.passive)
        effectPostPerc._modifiers = (modifierPostPerc,)
        valuePostPerc = 15
        influenceSourcePostPerc = IndependentItem(self.dh.type_(typeId=8, effects=(effectPostPerc,), attributes={srcAttr.id: valuePostPerc}))
        fit.items.append(influenceSourcePostPerc)
        influenceTarget = ShipItem(self.dh.type_(typeId=9, attributes={tgtAttr.id: 100}))
        fit.items.append(influenceTarget)
        # Operators shouldn't be penalized and should go in this order
        expValue = ((valuePreAss * valuePreMul / valuePreDiv) + valueModAdd - valueModSub) * valuePostMul / valuePostDiv * (1 + valuePostPerc / 100)
        self.assertAlmostEqual(influenceTarget.attributes[tgtAttr.id], expValue)
        fit.items.remove(influenceSourcePreAss)
        fit.items.remove(influenceSourcePreMul)
        fit.items.remove(influenceSourcePreDiv)
        fit.items.remove(influenceSourceModAdd)
        fit.items.remove(influenceSourceModSub)
        fit.items.remove(influenceSourcePostMul)
        fit.items.remove(influenceSourcePostDiv)
        fit.items.remove(influenceSourcePostPerc)
        fit.items.remove(influenceTarget)
        self.assertBuffersEmpty(fit)
