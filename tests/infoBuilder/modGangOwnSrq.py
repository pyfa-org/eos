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

from eos.eve.expression import Expression
from eos.calc.info.builder.builder import InfoBuilder, InfoBuildStatus
from eos.calc.info.info import InfoRunTime, InfoLocation, InfoFilterType, InfoOperator, InfoSourceType


class TestModGangOwnSrq(TestCase):
    """Test parsing of trees describing gang-mates' in-space items modification filtered by skill requirement"""

    def testBuildSuccess(self):
        # Manually composed example, as CCP doesn't use this modification type in any effect
        eTgtSrq = Expression(29, expressionTypeId=3326)
        eTgtAttr = Expression(22, expressionAttributeId=654)
        eOptr = Expression(21, value="PostMul")
        eSrcAttr = Expression(22, expressionAttributeId=848)
        eTgtSpec = Expression(64, arg1=eTgtSrq, arg2=eTgtAttr)
        eOptrTgt = Expression(31, arg1=eOptr, arg2=eTgtSpec)
        eAddMod = Expression(4, arg1=eOptrTgt, arg2=eSrcAttr)
        eRmMod = Expression(56, arg1=eOptrTgt, arg2=eSrcAttr)
        infos, status = InfoBuilder().build(eAddMod, eRmMod, 0)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = InfoRunTime.duration
        self.assertEqual(info.runTime, expType, msg="info type must be duration (ID {})".format(expType))
        expGang = True
        self.assertIs(info.gang, expGang, msg="info gang flag must be {}".format(expGang))
        expLocation = InfoLocation.space
        self.assertEqual(info.location, expLocation, msg="info target location must be space (ID {})".format(expLocation))
        expFilterType = InfoFilterType.skill
        self.assertEqual(info.filterType, expFilterType, msg="info target filter type must be skill (ID {})".format(expFilterType))
        expFilterValue = 3326
        self.assertEqual(info.filterValue, expFilterValue, msg="info target filter value must be {}".format(expFilterValue))
        expOperation = InfoOperator.postMul
        self.assertEqual(info.operator, expOperation, msg="info operator must be PostMul (ID {})".format(expOperation))
        expTgtAttr = 654
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcType = InfoSourceType.attribute
        self.assertEqual(info.sourceType, expSrcType, msg="info source type must be attribute (ID {})".format(expSrcType))
        expSrcVal = 848
        self.assertEqual(info.sourceValue, expSrcVal, msg="info source value must be {}".format(expSrcVal))
        self.assertIsNone(info.conditions, msg="info conditions must be None")
