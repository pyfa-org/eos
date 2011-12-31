from unittest import TestCase

from eos import const
from eos.data.expression import Expression
from eos.data.effect.builder import InfoBuilder

class TestModSub(TestCase):
    """Test parsing of trees describing direct attribute decrement"""

    def testPreBuildSuccess(self):
        eTgt = Expression(1, 24, value="Target")
        eTgtAttr = Expression(2, 22, attributeId=18)
        eSrcAttr = Expression(3, 22, attributeId=97)
        eTgtSpec = Expression(4, 12, arg1=eTgt, arg2=eTgtAttr)
        ePreSub = Expression(5, 18, arg1=eTgtSpec, arg2=eSrcAttr)
        ePostStub = Expression(6, 27, value="1")
        infos, status = InfoBuilder().build(ePreSub, ePostStub)
        self.assertEqual(status, const.effectInfoOkFull, msg="expressions must be successfully parsed")
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = const.infoPre
        self.assertEqual(info.type, expType, msg="info type must be instant pre-modifier (ID {})".format(expType))
        expGang = False
        self.assertIs(info.gang, expGang, msg="info gang flag must be {}".format(expGang))
        expLocation = const.locTgt
        self.assertEqual(info.location, expLocation, msg="info target location must be target (ID {})".format(expLocation))
        self.assertIsNone(info.filterType, msg="info target filter type must be None")
        self.assertIsNone(info.filterValue, msg="info target filter value must be None")
        expOperation = const.optrDecr
        self.assertEqual(info.operation, expOperation, msg="info operation must be Decreement (ID {})".format(expOperation))
        expTgtAttr = 18
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcAttr = 97
        self.assertEqual(info.sourceAttributeId, expSrcAttr, msg="info source attribute ID must be {}".format(expSrcAttr))
        self.assertIsNone(info.conditions, msg="conditions must be None")

    def testPostBuildSuccess(self):
        ePreStub = Expression(1, 27, value="1")
        eTgt = Expression(2, 24, value="Target")
        eTgtAttr = Expression(3, 22, attributeId=266)
        eSrcAttr = Expression(4, 22, attributeId=84)
        eTgtSpec = Expression(5, 12, arg1=eTgt, arg2=eTgtAttr)
        ePostSub = Expression(6, 18, arg1=eTgtSpec, arg2=eSrcAttr)
        infos, status = InfoBuilder().build(ePreStub, ePostSub)
        self.assertEqual(status, const.effectInfoOkFull, msg="expressions must be successfully parsed")
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = const.infoPost
        self.assertEqual(info.type, expType, msg="info type must be instant post-modifier (ID {})".format(expType))
        expGang = False
        self.assertIs(info.gang, expGang, msg="info gang flag must be {}".format(expGang))
        expLocation = const.locTgt
        self.assertEqual(info.location, expLocation, msg="info target location must be target (ID {})".format(expLocation))
        self.assertIsNone(info.filterType, msg="info target filter type must be None")
        self.assertIsNone(info.filterValue, msg="info target filter value must be None")
        expOperation = const.optrDecr
        self.assertEqual(info.operation, expOperation, msg="info operation must be Decreement (ID {})".format(expOperation))
        expTgtAttr = 266
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcAttr = 84
        self.assertEqual(info.sourceAttributeId, expSrcAttr, msg="info source attribute ID must be {}".format(expSrcAttr))
        self.assertIsNone(info.conditions, msg="conditions must be None")
