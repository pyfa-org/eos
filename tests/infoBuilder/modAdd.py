from unittest import TestCase, expectedFailure

from eos import const
from eos.data.expression import Expression
from eos.data.effect.builder import InfoBuilder

class TestPreModAddAttr(TestCase):
    """Test parsing of trees describing increment by attribute in the beginning of the cycle"""

    def testBuildSuccess(self):
        eTgt = Expression(1, 24, value="Ship")
        eTgtAttr = Expression(2, 22, attributeId=264)
        eSrcAttr = Expression(3, 22, attributeId=68)
        eTgtSpec = Expression(4, 12, arg1=eTgt, arg2=eTgtAttr)
        ePreAdd = Expression(5, 42, arg1=eTgtSpec, arg2=eSrcAttr)
        ePostStub = Expression(6, 27, value="1")
        infos, status = InfoBuilder().build(ePreAdd, ePostStub)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = const.infoPre
        self.assertEqual(info.type, expType, msg="info type must be instant pre-modifier (ID {})".format(expType))
        expGang = False
        self.assertIs(info.gang, expGang, msg="info gang flag must be {}".format(expGang))
        expLocation = const.locShip
        self.assertEqual(info.location, expLocation, msg="info target location must be ship (ID {})".format(expLocation))
        self.assertIsNone(info.filterType, msg="info target filter type must be None")
        self.assertIsNone(info.filterValue, msg="info target filter value must be None")
        expOperation = const.optrIncr
        self.assertEqual(info.operation, expOperation, msg="info operation must be Increment (ID {})".format(expOperation))
        expTgtAttr = 264
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcAttr = 68
        self.assertEqual(info.sourceAttributeId, expSrcAttr, msg="info source attribute ID must be {}".format(expSrcAttr))
        self.assertIsNone(info.conditions, msg="conditions must be None")

class TestPreModAddVal(TestCase):
    """Test parsing of trees describing increment by value in the beginning of the cycle"""

    @expectedFailure
    def testBuildSuccess(self):
        eTgt = Expression(1, 24, value="Ship")
        eTgtAttr = Expression(2, 22, attributeId=264)
        eSrcVal = Expression(3, 27, value="200")
        eTgtSpec = Expression(4, 12, arg1=eTgt, arg2=eTgtAttr)
        ePreAdd = Expression(5, 42, arg1=eTgtSpec, arg2=eSrcVal)
        ePostStub = Expression(6, 27, value="1")
        infos, status = InfoBuilder().build(ePreAdd, ePostStub)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))


class TestPostModAddAttr(TestCase):
    """Test parsing of trees describing increment by attribute in the end of the cycle"""

    def testBuildSuccess(self):
        ePreStub = Expression(1, 27, value="1")
        eTgt = Expression(2, 24, value="Ship")
        eTgtAttr = Expression(3, 22, attributeId=264)
        eSrcAttr = Expression(4, 22, attributeId=68)
        eTgtSpec = Expression(5, 12, arg1=eTgt, arg2=eTgtAttr)
        ePostAdd = Expression(6, 42, arg1=eTgtSpec, arg2=eSrcAttr)
        infos, status = InfoBuilder().build(ePreStub, ePostAdd)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = const.infoPost
        self.assertEqual(info.type, expType, msg="info type must be instant post-modifier (ID {})".format(expType))
        expGang = False
        self.assertIs(info.gang, expGang, msg="info gang flag must be {}".format(expGang))
        expLocation = const.locShip
        self.assertEqual(info.location, expLocation, msg="info target location must be ship (ID {})".format(expLocation))
        self.assertIsNone(info.filterType, msg="info target filter type must be None")
        self.assertIsNone(info.filterValue, msg="info target filter value must be None")
        expOperation = const.optrIncr
        self.assertEqual(info.operation, expOperation, msg="info operation must be Increment (ID {})".format(expOperation))
        expTgtAttr = 264
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcAttr = 68
        self.assertEqual(info.sourceAttributeId, expSrcAttr, msg="info source attribute ID must be {}".format(expSrcAttr))
        self.assertIsNone(info.conditions, msg="conditions must be None")

class TestPostModAddVal(TestCase):
    """Test parsing of trees describing increment by value in the end of the cycle"""

    @expectedFailure
    def testBuildSuccess(self):
        ePreStub = Expression(1, 27, value="1")
        eTgt = Expression(2, 24, value="Ship")
        eTgtAttr = Expression(3, 22, attributeId=264)
        eSrcVal = Expression(4, 27, value="3")
        eTgtSpec = Expression(5, 12, arg1=eTgt, arg2=eTgtAttr)
        ePostAdd = Expression(6, 42, arg1=eTgtSpec, arg2=eSrcVal)
        infos, status = InfoBuilder().build(ePreStub, ePostAdd)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
