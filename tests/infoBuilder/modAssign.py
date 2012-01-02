from unittest import TestCase

from eos import const
from eos.data.expression import Expression
from eos.data.effect.builder import InfoBuilder

class TestPreModAssignAttr(TestCase):
    """Test parsing of trees describing assignments by attribute applied in the beginning of the cycle"""

    def testBuildSuccess(self):
        # Manually composed example, CCP doesn't use such combination
        eTgt = Expression(1, 24, value="Char")
        eTgtAttr = Expression(2, 22, attributeId=166)
        eSrcAttr = Expression(3, 22, attributeId=177)
        eTgtSpec = Expression(4, 12, arg1=eTgt, arg2=eTgtAttr)
        ePreAssign = Expression(5, 65, arg1=eTgtSpec, arg2=eSrcAttr)
        ePostStub = Expression(6, 27, value="1")
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
        self.assertEqual(info.operation, expOperation, msg="info operation must be Assign (ID {})".format(expOperation))
        expTgtAttr = 166
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcType = const.srcAttr
        self.assertEqual(info.sourceType, expSrcType, msg="info source type must be attribute (ID {})".format(expSrcType))
        expSrcVal = 177
        self.assertEqual(info.sourceValue, expSrcVal, msg="info source value must be {}".format(expSrcVal))
        self.assertIsNone(info.conditions, msg="info conditions must be None")


class TestPreModAssignVal(TestCase):
    """Test parsing of trees describing assignments by value applied in the beginning of the cycle"""

    def testBuildSuccess(self):
        eTgt = Expression(1, 24, value="Self")
        eTgtAttr = Expression(2, 22, attributeId=2)
        eSrcVal = Expression(3, 27, value="1")
        eTgtSpec = Expression(4, 12, arg1=eTgt, arg2=eTgtAttr)
        ePreAssign = Expression(5, 65, arg1=eTgtSpec, arg2=eSrcVal)
        ePostStub = Expression(6, 27, value="1")
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
        self.assertEqual(info.operation, expOperation, msg="info operation must be Assign (ID {})".format(expOperation))
        expTgtAttr = 2
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcType = const.srcVal
        self.assertEqual(info.sourceType, expSrcType, msg="info source type must be value (ID {})".format(expSrcType))
        expSrcVal = 1
        self.assertEqual(info.sourceValue, expSrcVal, msg="info source value must be {}".format(expSrcVal))
        self.assertIsNone(info.conditions, msg="info conditions must be None")


class TestPostModAssignAttr(TestCase):
    """Test parsing of trees describing assignments by attribute applied in the end of the cycle"""

    def testBuildSuccess(self):
        # Manually composed example, CCP doesn't use such combination
        ePreStub = Expression(1, 27, value="1")
        eTgt = Expression(2, 24, value="Char")
        eTgtAttr = Expression(3, 22, attributeId=166)
        eSrcAttr = Expression(4, 22, attributeId=177)
        eTgtSpec = Expression(5, 12, arg1=eTgt, arg2=eTgtAttr)
        ePostAssign = Expression(6, 65, arg1=eTgtSpec, arg2=eSrcAttr)
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
        self.assertEqual(info.operation, expOperation, msg="info operation must be Assign (ID {})".format(expOperation))
        expTgtAttr = 166
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcType = const.srcAttr
        self.assertEqual(info.sourceType, expSrcType, msg="info source type must be attribute (ID {})".format(expSrcType))
        expSrcVal = 177
        self.assertEqual(info.sourceValue, expSrcVal, msg="info source value must be {}".format(expSrcVal))
        self.assertIsNone(info.conditions, msg="info conditions must be None")


class TestPostModAssignVal(TestCase):
    """Test parsing of trees describing assignments by value applied in the end of the cycle"""

    def testBuildSuccess(self):
        ePreStub = Expression(1, 27, value="1")
        eTgt = Expression(2, 24, value="Self")
        eTgtAttr = Expression(3, 22, attributeId=2)
        eSrcVal = Expression(4, 27, value="0")
        eTgtSpec = Expression(5, 12, arg1=eTgt, arg2=eTgtAttr)
        ePostAssign = Expression(6, 65, arg1=eTgtSpec, arg2=eSrcVal)
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
        self.assertEqual(info.operation, expOperation, msg="info operation must be Assign (ID {})".format(expOperation))
        expTgtAttr = 2
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcType = const.srcVal
        self.assertEqual(info.sourceType, expSrcType, msg="info source type must be value (ID {})".format(expSrcType))
        expSrcVal = 0
        self.assertEqual(info.sourceValue, expSrcVal, msg="info source value must be {}".format(expSrcVal))
        self.assertIsNone(info.conditions, msg="info conditions must be None")
