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

from eos import const
from eos.eve.expression import Expression
from eos.calc.info.builder.builder import InfoBuilder

class TestPreModAssignAttr(TestCase):
    """Test parsing of trees describing assignments by attribute applied in the beginning of the cycle"""

    def testBuildSuccess(self):
        # Manually composed example, CCP doesn't use such combination
        eTgt = Expression(24, value="Char")
        eTgtAttr = Expression(22, attributeId=166)
        eSrcAttr = Expression(22, attributeId=177)
        eTgtSpec = Expression(12, arg1=eTgt, arg2=eTgtAttr)
        ePreAssign = Expression(65, arg1=eTgtSpec, arg2=eSrcAttr)
        ePostStub = Expression(27, value="1")
        infos, status = InfoBuilder().build(ePreAssign, ePostStub)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = const.infoPre
        self.assertEqual(info.type, expType, msg="info type must be instant pre-modifier (ID {})".format(expType))
        expGang = False
        self.assertIs(info.gang, expGang, msg="info gang flag must be {}".format(expGang))
        expLocation = const.locChar
        self.assertEqual(info.location, expLocation, msg="info target location must be char (ID {})".format(expLocation))
        self.assertIsNone(info.filterType, msg="info target filter type must be None")
        self.assertIsNone(info.filterValue, msg="info target filter value must be None")
        expOperation = const.optrAssign
        self.assertEqual(info.operator, expOperation, msg="info operator must be Assign (ID {})".format(expOperation))
        expTgtAttr = 166
        self.assertEqual(info.targetAttribute, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcType = const.srcAttr
        self.assertEqual(info.sourceType, expSrcType, msg="info source type must be attribute (ID {})".format(expSrcType))
        expSrcVal = 177
        self.assertEqual(info.sourceValue, expSrcVal, msg="info source value must be {}".format(expSrcVal))
        self.assertIsNone(info.conditions, msg="info conditions must be None")


class TestPreModAssignVal(TestCase):
    """Test parsing of trees describing assignments by value applied in the beginning of the cycle"""

    def testBuildSuccess(self):
        eTgt = Expression(24, value="Self")
        eTgtAttr = Expression(22, attributeId=2)
        eSrcVal = Expression(27, value="1")
        eTgtSpec = Expression(12, arg1=eTgt, arg2=eTgtAttr)
        ePreAssign = Expression(65, arg1=eTgtSpec, arg2=eSrcVal)
        ePostStub = Expression(27, value="1")
        infos, status = InfoBuilder().build(ePreAssign, ePostStub)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = const.infoPre
        self.assertEqual(info.type, expType, msg="info type must be instant pre-modifier (ID {})".format(expType))
        expGang = False
        self.assertIs(info.gang, expGang, msg="info gang flag must be {}".format(expGang))
        expLocation = const.locSelf
        self.assertEqual(info.location, expLocation, msg="info target location must be self (ID {})".format(expLocation))
        self.assertIsNone(info.filterType, msg="info target filter type must be None")
        self.assertIsNone(info.filterValue, msg="info target filter value must be None")
        expOperation = const.optrAssign
        self.assertEqual(info.operator, expOperation, msg="info operator must be Assign (ID {})".format(expOperation))
        expTgtAttr = 2
        self.assertEqual(info.targetAttribute, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcType = const.srcVal
        self.assertEqual(info.sourceType, expSrcType, msg="info source type must be value (ID {})".format(expSrcType))
        expSrcVal = 1
        self.assertEqual(info.sourceValue, expSrcVal, msg="info source value must be {}".format(expSrcVal))
        self.assertIsNone(info.conditions, msg="info conditions must be None")


class TestPostModAssignAttr(TestCase):
    """Test parsing of trees describing assignments by attribute applied in the end of the cycle"""

    def testBuildSuccess(self):
        # Manually composed example, CCP doesn't use such combination
        ePreStub = Expression(27, value="1")
        eTgt = Expression(24, value="Char")
        eTgtAttr = Expression(22, attributeId=166)
        eSrcAttr = Expression(22, attributeId=177)
        eTgtSpec = Expression(12, arg1=eTgt, arg2=eTgtAttr)
        ePostAssign = Expression(65, arg1=eTgtSpec, arg2=eSrcAttr)
        infos, status = InfoBuilder().build(ePreStub, ePostAssign)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = const.infoPost
        self.assertEqual(info.type, expType, msg="info type must be instant post-modifier (ID {})".format(expType))
        expGang = False
        self.assertIs(info.gang, expGang, msg="info gang flag must be {}".format(expGang))
        expLocation = const.locChar
        self.assertEqual(info.location, expLocation, msg="info target location must be char (ID {})".format(expLocation))
        self.assertIsNone(info.filterType, msg="info target filter type must be None")
        self.assertIsNone(info.filterValue, msg="info target filter value must be None")
        expOperation = const.optrAssign
        self.assertEqual(info.operator, expOperation, msg="info operator must be Assign (ID {})".format(expOperation))
        expTgtAttr = 166
        self.assertEqual(info.targetAttribute, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcType = const.srcAttr
        self.assertEqual(info.sourceType, expSrcType, msg="info source type must be attribute (ID {})".format(expSrcType))
        expSrcVal = 177
        self.assertEqual(info.sourceValue, expSrcVal, msg="info source value must be {}".format(expSrcVal))
        self.assertIsNone(info.conditions, msg="info conditions must be None")


class TestPostModAssignVal(TestCase):
    """Test parsing of trees describing assignments by value applied in the end of the cycle"""

    def testBuildSuccess(self):
        ePreStub = Expression(27, value="1")
        eTgt = Expression(24, value="Self")
        eTgtAttr = Expression(22, attributeId=2)
        eSrcVal = Expression(27, value="0")
        eTgtSpec = Expression(12, arg1=eTgt, arg2=eTgtAttr)
        ePostAssign = Expression(65, arg1=eTgtSpec, arg2=eSrcVal)
        infos, status = InfoBuilder().build(ePreStub, ePostAssign)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = const.infoPost
        self.assertEqual(info.type, expType, msg="info type must be instant post-modifier (ID {})".format(expType))
        expGang = False
        self.assertIs(info.gang, expGang, msg="info gang flag must be {}".format(expGang))
        expLocation = const.locSelf
        self.assertEqual(info.location, expLocation, msg="info target location must be self (ID {})".format(expLocation))
        self.assertIsNone(info.filterType, msg="info target filter type must be None")
        self.assertIsNone(info.filterValue, msg="info target filter value must be None")
        expOperation = const.optrAssign
        self.assertEqual(info.operator, expOperation, msg="info operator must be Assign (ID {})".format(expOperation))
        expTgtAttr = 2
        self.assertEqual(info.targetAttribute, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcType = const.srcVal
        self.assertEqual(info.sourceType, expSrcType, msg="info source type must be value (ID {})".format(expSrcType))
        expSrcVal = 0
        self.assertEqual(info.sourceValue, expSrcVal, msg="info source value must be {}".format(expSrcVal))
        self.assertIsNone(info.conditions, msg="info conditions must be None")
