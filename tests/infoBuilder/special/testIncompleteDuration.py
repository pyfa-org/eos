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


from eos.const import EffectBuildStatus
from eos.eve.effect import Effect
from eos.eve.expression import Expression
from eos.fit.attributeCalculator.info.infoBuilder import InfoBuilder
from eos.tests.environment import Logger
from eos.tests.eosTestCase import EosTestCase
from eos.tests.infoBuilder.environment import callize


class TestIncompleteDuration(EosTestCase):
    """Test parsing of trees, which include modifiers, which are not converted into infos"""

    def setUp(self):
        EosTestCase.setUp(self)
        # Duration modifier, except for top-most expression, which
        # is added in test cases
        eTgt = Expression(None, 24, value="Ship")
        eTgtAttr = Expression(None, 22, expressionAttributeId=9)
        eOptr = Expression(None, 21, value="PostPercent")
        self.eSrcAttr = Expression(None, 22, expressionAttributeId=327)
        eTgtSpec = Expression(None, 12, arg1=eTgt, arg2=eTgtAttr)
        self.eOptrTgt = Expression(None, 31, arg1=eOptr, arg2=eTgtSpec)
        self.stub = Expression(1, 27, value="1")

    def testPre(self):
        eAddMod = Expression(2, 6, arg1=self.eOptrTgt, arg2=self.eSrcAttr)
        effect = Effect(None, 0, preExpressionData=callize(eAddMod), postExpressionData=callize(self.stub))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(infos), 0)

    def testPost(self):
        eRmMod = Expression(2, 58, arg1=self.eOptrTgt, arg2=self.eSrcAttr)
        effect = Effect(None, 0, preExpressionData=callize(self.stub), postExpressionData=callize(eRmMod))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(infos), 0)
