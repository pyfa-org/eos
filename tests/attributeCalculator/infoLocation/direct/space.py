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

from eos.const import State, Location, Context, RunTime, Operator, SourceType
from eos.fit.attributeCalculator.info.info import Info
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.tests.attributeCalculator.environment import Fit, IndependentItem
from eos.tests.eosTestCase import EosTestCase


class TestLocationDirectSpace(EosTestCase):
    """Test location.space for direct modifications"""

    def testError(self):
        tgtAttr = Attribute(1)
        srcAttr = Attribute(2)
        info = Info()
        info.state = State.offline
        info.context = Context.local
        info.runTime = RunTime.duration
        info.gang = False
        info.location = Location.space
        info.filterType = None
        info.filterValue = None
        info.operator = Operator.postPercent
        info.targetAttributeId = tgtAttr.id
        info.sourceType = SourceType.attribute
        info.sourceValue = srcAttr.id
        effect = Effect(None, EffectCategory.passive)
        effect._Effect__infos = {info}
        fit = Fit({tgtAttr.id: tgtAttr, srcAttr.id: srcAttr})
        influenceSource = IndependentItem(Type(34, effects={effect}, attributes={srcAttr.id: 20}))
        # Space location was introduced in Eos as holder to contain in-space
        # items like missiles or drones, but it can't be targeted directly
        fit._addHolder(influenceSource)
        self.assertEqual(len(self.log), 2)
        logRecord = self.log[0]
        self.assertEqual(logRecord.levelno, WARNING)
        expMessage = "malformed info on item 34: unsupported target location {}".format(Location.space)
        self.assertEqual(logRecord.msg, expMessage)
        logRecord = self.log[1]
        self.assertEqual(logRecord.levelno, WARNING)
        self.assertEqual(logRecord.msg, expMessage)
        fit._removeHolder(influenceSource)
        self.assertEqual(len(self.log), 4)
        logRecord = self.log[2]
        self.assertEqual(logRecord.levelno, WARNING)
        self.assertEqual(logRecord.msg, expMessage)
        logRecord = self.log[3]
        self.assertEqual(logRecord.levelno, WARNING)
        self.assertEqual(logRecord.msg, expMessage)
