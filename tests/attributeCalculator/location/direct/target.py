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


from unittest import TestCase

from eos.const import State, Location, Context, RunTime, Operator, SourceType
from eos.fit.attributeCalculator.exception import UnsupportedLocationException
from eos.fit.attributeCalculator.info.info import Info
from eos.fit.fit import Fit
from eos.eve.attribute import Attribute
from eos.eve.const import EffectCategory
from eos.eve.effect import Effect
from eos.eve.type import Type
from eos.tests.attributeCalculator.helper import IndependentItem


class TestLocationDirectTarget(TestCase):
    """Test location.target for direct modifications"""

    def setUp(self):
        self.tgtAttr = tgtAttr = Attribute(1)
        srcAttr = Attribute(2)
        info = Info()
        info.state = State.offline
        info.context = Context.local
        info.runTime = RunTime.duration
        info.gang = False
        info.location = Location.target
        info.filterType = None
        info.operator = Operator.postPercent
        info.targetAttributeId = tgtAttr.id
        info.sourceType = SourceType.attribute
        info.sourceValue = srcAttr.id
        effect = Effect(1, EffectCategory.passive)
        effect._Effect__infos = {info}
        self.fit = Fit(lambda attrId: {tgtAttr.id: tgtAttr, srcAttr.id: srcAttr}[attrId])
        self.influenceSource = IndependentItem(Type(1, effects={effect}, attributes={srcAttr.id: 20}))

    def testException(self):
        # This functionality isn't implemented for now
        self.assertRaises(UnsupportedLocationException, self.fit._addHolder, self.influenceSource)
