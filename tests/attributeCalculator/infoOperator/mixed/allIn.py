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
from eos.fit.attributeCalculator.info.info import Info
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.tests.attributeCalculator.environment import Fit, IndependentItem, ShipItem
from eos.tests.eosTestCase import EosTestCase


class TestOperatorAllIn(EosTestCase):
    """Test interaction of all operators, besides post-assignment"""

    def testAllIn(self):
        tgtAttr = Attribute(1, stackable=False)
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
        effectPreAss._Effect__infos = {infoPreAss}
        valuePreAss = 5
        influenceSourcePreAss = IndependentItem(Type(None, effects={effectPreAss}, attributes={srcAttr.id: valuePreAss}))
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
        effectPreMul._Effect__infos = {infoPreMul}
        valuePreMul = 50
        influenceSourcePreMul = IndependentItem(Type(None, effects={effectPreMul}, attributes={srcAttr.id: valuePreMul}))
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
        effectPreDiv._Effect__infos = {infoPreDiv}
        valuePreDiv = 0.5
        influenceSourcePreDiv = IndependentItem(Type(None, effects={effectPreDiv}, attributes={srcAttr.id: valuePreDiv}))
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
        effectModAdd._Effect__infos = {infoModAdd}
        valueModAdd = 10
        influenceSourceModAdd = IndependentItem(Type(None, effects={effectModAdd}, attributes={srcAttr.id: valueModAdd}))
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
        effectModSub._Effect__infos = {infoModSub}
        valueModSub = 63
        influenceSourceModSub = IndependentItem(Type(None, effects={effectModSub}, attributes={srcAttr.id: valueModSub}))
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
        effectPostMul._Effect__infos = {infoPostMul}
        valuePostMul = 1.35
        influenceSourcePostMul = IndependentItem(Type(None, effects={effectPostMul}, attributes={srcAttr.id: valuePostMul}))
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
        effectPostDiv._Effect__infos = {infoPostDiv}
        valuePostDiv = 2.7
        influenceSourcePostDiv = IndependentItem(Type(None, effects={effectPostDiv}, attributes={srcAttr.id: valuePostDiv}))
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
        effectPostPerc._Effect__infos = {infoPostPerc}
        valuePostPerc = 15
        influenceSourcePostPerc = IndependentItem(Type(None, effects={effectPostPerc}, attributes={srcAttr.id: valuePostPerc}))
        fit._addHolder(influenceSourcePostPerc)
        influenceTarget = ShipItem(Type(None, attributes={tgtAttr.id: 100}))
        fit._addHolder(influenceTarget)
        # Operators shouldn't be penalized and should go in this order
        expValue = ((valuePreAss * valuePreMul / valuePreDiv) + valueModAdd - valueModSub) * valuePostMul / valuePostDiv * (1 + valuePostPerc / 100)
        self.assertAlmostEqual(influenceTarget.attributes[tgtAttr.id], expValue, msg="value must be equal {}".format(expValue))
