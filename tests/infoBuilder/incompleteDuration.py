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

from eos.const import EffectBuildStatus
from eos.eve.expression import Expression
from eos.fit.calc.info.builder.infoBuilder import InfoBuilder


class TestIncompleteDuration(TestCase):
    """Test parsing of trees, which include modifiers, which are not converted into infos"""

    def setUp(self):
        # Duration modifier, except for top-most expression
        eTgt = Expression(None, 24, value="Ship")
        eTgtAttr = Expression(None, 22, expressionAttributeId=9)
        eOptr = Expression(None, 21, value="PostPercent")
        self.eSrcAttr = Expression(None, 22, expressionAttributeId=327)
        eTgtSpec = Expression(None, 12, arg1=eTgt, arg2=eTgtAttr)
        self.eOptrTgt = Expression(None, 31, arg1=eOptr, arg2=eTgtSpec)
        self.stub = Expression(None, 27, value="1")

    def testPre(self):
        eAddMod = Expression(None, 6, arg1=self.eOptrTgt, arg2=self.eSrcAttr)
        infos, status = InfoBuilder().build(eAddMod, self.stub, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testPost(self):
        eRmMod = Expression(None, 58, arg1=self.eOptrTgt, arg2=self.eSrcAttr)
        infos, status = InfoBuilder().build(self.stub, eRmMod, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")
