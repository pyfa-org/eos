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


from eos.const import State, Location, Context, RunTime, FilterType, Operator, SourceType
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.fit.attributeCalculator.info.info import Info
from eos.tests.attributeCalculator.attrCalcTestCase import AttrCalcTestCase
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, ShipItem


class TestOperatorForcedValue(AttrCalcTestCase):
    """Test that post-assignment forces value of attribute"""

    def testForcedValue(self):
        tgtAttr = Attribute(1)
        srcAttr = Attribute(2)
        fit = Fit({tgtAttr.id: tgtAttr, srcAttr.id: srcAttr})
        infoPreAss = Info()
        infoPreAss.state = State.offline
        infoPreAss.context = Context.local
        infoPreAss.runTime = RunTime.duration
        infoPreAss.gang = False
        infoPreAss.location = Location.ship
        infoPreAss.filterType = FilterType.all_
        infoPreAss.filterValue = None
        infoPreAss.operator = Operator.preAssignment
        infoPreAss.targetAttributeId = tgtAttr.id
        infoPreAss.sourceType = SourceType.attribute
        infoPreAss.sourceValue = srcAttr.id
        effectPreAss = Effect(None, EffectCategory.passive)
        effectPreAss._infos = (infoPreAss,)
        influenceSourcePreAss = IndependentItem(Type(None, effects=(effectPreAss,), attributes={srcAttr.id: 5}))
        fit._addHolder(influenceSourcePreAss)
        infoPreMul = Info()
        infoPreMul.state = State.offline
        infoPreMul.context = Context.local
        infoPreMul.runTime = RunTime.duration
        infoPreMul.gang = False
        infoPreMul.location = Location.ship
        infoPreMul.filterType = FilterType.all_
        infoPreMul.filterValue = None
        infoPreMul.operator = Operator.preMul
        infoPreMul.targetAttributeId = tgtAttr.id
        infoPreMul.sourceType = SourceType.attribute
        infoPreMul.sourceValue = srcAttr.id
        effectPreMul = Effect(None, EffectCategory.passive)
        effectPreMul._infos = (infoPreMul,)
        influenceSourcePreMul = IndependentItem(Type(None, effects=(effectPreMul,), attributes={srcAttr.id: 50}))
        fit._addHolder(influenceSourcePreMul)
        infoPreDiv = Info()
        infoPreDiv.state = State.offline
        infoPreDiv.context = Context.local
        infoPreDiv.runTime = RunTime.duration
        infoPreDiv.gang = False
        infoPreDiv.location = Location.ship
        infoPreDiv.filterType = FilterType.all_
        infoPreDiv.filterValue = None
        infoPreDiv.operator = Operator.preDiv
        infoPreDiv.targetAttributeId = tgtAttr.id
        infoPreDiv.sourceType = SourceType.attribute
        infoPreDiv.sourceValue = srcAttr.id
        effectPreDiv = Effect(None, EffectCategory.passive)
        effectPreDiv._infos = (infoPreDiv,)
        influenceSourcePreDiv = IndependentItem(Type(None, effects=(effectPreDiv,), attributes={srcAttr.id: 0.5}))
        fit._addHolder(influenceSourcePreDiv)
        infoModAdd = Info()
        infoModAdd.state = State.offline
        infoModAdd.context = Context.local
        infoModAdd.runTime = RunTime.duration
        infoModAdd.gang = False
        infoModAdd.location = Location.ship
        infoModAdd.filterType = FilterType.all_
        infoModAdd.filterValue = None
        infoModAdd.operator = Operator.modAdd
        infoModAdd.targetAttributeId = tgtAttr.id
        infoModAdd.sourceType = SourceType.attribute
        infoModAdd.sourceValue = srcAttr.id
        effectModAdd = Effect(None, EffectCategory.passive)
        effectModAdd._infos = (infoModAdd,)
        influenceSourceModAdd = IndependentItem(Type(None, effects=(effectModAdd,), attributes={srcAttr.id: 10}))
        fit._addHolder(influenceSourceModAdd)
        infoModSub = Info()
        infoModSub.state = State.offline
        infoModSub.context = Context.local
        infoModSub.runTime = RunTime.duration
        infoModSub.gang = False
        infoModSub.location = Location.ship
        infoModSub.filterType = FilterType.all_
        infoModSub.filterValue = None
        infoModSub.operator = Operator.modSub
        infoModSub.targetAttributeId = tgtAttr.id
        infoModSub.sourceType = SourceType.attribute
        infoModSub.sourceValue = srcAttr.id
        effectModSub = Effect(None, EffectCategory.passive)
        effectModSub._infos = (infoModSub,)
        influenceSourceModSub = IndependentItem(Type(None, effects=(effectModSub,), attributes={srcAttr.id: 63}))
        fit._addHolder(influenceSourceModSub)
        infoPostMul = Info()
        infoPostMul.state = State.offline
        infoPostMul.context = Context.local
        infoPostMul.runTime = RunTime.duration
        infoPostMul.gang = False
        infoPostMul.location = Location.ship
        infoPostMul.filterType = FilterType.all_
        infoPostMul.filterValue = None
        infoPostMul.operator = Operator.postMul
        infoPostMul.targetAttributeId = tgtAttr.id
        infoPostMul.sourceType = SourceType.attribute
        infoPostMul.sourceValue = srcAttr.id
        effectPostMul = Effect(None, EffectCategory.passive)
        effectPostMul._infos = (infoPostMul,)
        influenceSourcePostMul = IndependentItem(Type(None, effects=(effectPostMul,), attributes={srcAttr.id: 1.35}))
        fit._addHolder(influenceSourcePostMul)
        infoPostDiv = Info()
        infoPostDiv.state = State.offline
        infoPostDiv.context = Context.local
        infoPostDiv.runTime = RunTime.duration
        infoPostDiv.gang = False
        infoPostDiv.location = Location.ship
        infoPostDiv.filterType = FilterType.all_
        infoPostDiv.filterValue = None
        infoPostDiv.operator = Operator.postDiv
        infoPostDiv.targetAttributeId = tgtAttr.id
        infoPostDiv.sourceType = SourceType.attribute
        infoPostDiv.sourceValue = srcAttr.id
        effectPostDiv = Effect(None, EffectCategory.passive)
        effectPostDiv._infos = (infoPostDiv,)
        influenceSourcePostDiv = IndependentItem(Type(None, effects=(effectPostDiv,), attributes={srcAttr.id: 2.7}))
        fit._addHolder(influenceSourcePostDiv)
        infoPostPerc = Info()
        infoPostPerc.state = State.offline
        infoPostPerc.context = Context.local
        infoPostPerc.runTime = RunTime.duration
        infoPostPerc.gang = False
        infoPostPerc.location = Location.ship
        infoPostPerc.filterType = FilterType.all_
        infoPostPerc.filterValue = None
        infoPostPerc.operator = Operator.postPercent
        infoPostPerc.targetAttributeId = tgtAttr.id
        infoPostPerc.sourceType = SourceType.attribute
        infoPostPerc.sourceValue = srcAttr.id
        effectPostPerc = Effect(None, EffectCategory.passive)
        effectPostPerc._infos = (infoPostPerc,)
        influenceSourcePostPerc = IndependentItem(Type(None, effects=(effectPostPerc,), attributes={srcAttr.id: 15}))
        fit._addHolder(influenceSourcePostPerc)
        infoPostAss = Info()
        infoPostAss.state = State.offline
        infoPostAss.context = Context.local
        infoPostAss.runTime = RunTime.duration
        infoPostAss.gang = False
        infoPostAss.location = Location.ship
        infoPostAss.filterType = FilterType.all_
        infoPostAss.filterValue = None
        infoPostAss.operator = Operator.postAssignment
        infoPostAss.targetAttributeId = tgtAttr.id
        infoPostAss.sourceType = SourceType.attribute
        infoPostAss.sourceValue = srcAttr.id
        effectPostAss = Effect(None, EffectCategory.passive)
        effectPostAss._infos = (infoPostAss,)
        influenceSourcePostAss = IndependentItem(Type(None, effects=(effectPostAss,), attributes={srcAttr.id: 68}))
        fit._addHolder(influenceSourcePostAss)
        influenceTarget = ShipItem(Type(None, attributes={tgtAttr.id: 100}))
        fit._addHolder(influenceTarget)
        # Post-assignment value must override all other modifications
        self.assertAlmostEqual(influenceTarget.attributes[tgtAttr.id], 68)
        fit._removeHolder(influenceSourcePreAss)
        fit._removeHolder(influenceSourcePreMul)
        fit._removeHolder(influenceSourcePreDiv)
        fit._removeHolder(influenceSourceModAdd)
        fit._removeHolder(influenceSourceModSub)
        fit._removeHolder(influenceSourcePostMul)
        fit._removeHolder(influenceSourcePostDiv)
        fit._removeHolder(influenceSourcePostPerc)
        fit._removeHolder(influenceSourcePostAss)
        fit._removeHolder(influenceTarget)
        self.assertBuffersEmpty(fit)
