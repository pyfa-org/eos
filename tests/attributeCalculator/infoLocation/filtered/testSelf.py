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


from logging import WARNING

from eos.const import State, Location, Context, RunTime, FilterType, Operator, SourceType
from eos.fit.attributeCalculator.info.info import Info
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.tests.environment import Fit, IndependentItem, CharacterItem, ShipItem
from eos.tests.eosTestCase import EosTestCase


class TestLocationFilterSelf(EosTestCase):
    """Test location.self (self-reference) for massive filtered modifications"""

    def setUp(self):
        EosTestCase.setUp(self)
        self.tgtAttr = tgtAttr = Attribute(1)
        srcAttr = Attribute(2)
        info = Info()
        info.state = State.offline
        info.context = Context.local
        info.runTime = RunTime.duration
        info.gang = False
        info.location = Location.self_
        info.filterType = FilterType.all_
        info.filterValue = None
        info.operator = Operator.postPercent
        info.targetAttributeId = tgtAttr.id
        info.sourceType = SourceType.attribute
        info.sourceValue = srcAttr.id
        effect = Effect(None, EffectCategory.passive)
        effect._Effect__infos = {info}
        self.fit = Fit({tgtAttr.id: tgtAttr, srcAttr.id: srcAttr})
        self.influenceSource = IndependentItem(Type(1061, effects={effect}, attributes={srcAttr.id: 20}))

    def testShip(self):
        self.fit.ship = self.influenceSource
        self.fit._addHolder(self.influenceSource)
        influenceTarget = ShipItem(Type(None, attributes={self.tgtAttr.id: 100}))
        self.fit._addHolder(influenceTarget)
        self.assertNotAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit._removeHolder(self.influenceSource)
        self.fit.ship = None
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)

    def testCharacter(self):
        self.fit.character = self.influenceSource
        self.fit._addHolder(self.influenceSource)
        influenceTarget = CharacterItem(Type(None, attributes={self.tgtAttr.id: 100}))
        self.fit._addHolder(influenceTarget)
        self.assertNotAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)
        self.fit._removeHolder(self.influenceSource)
        self.fit.character = None
        self.assertAlmostEqual(influenceTarget.attributes[self.tgtAttr.id], 100)

    def testUnpositionedError(self):
        # Here we do not position holder in fit, this way attribute
        # calculator won't know that source is 'owner' of some location
        # and will throw corresponding exception
        self.fit._addHolder(self.influenceSource)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.levelno, WARNING)
        self.assertEqual(logRecord.msg, "malformed info on item 1061: invalid reference to self for filtered modification")
