from unittest import TestCase

from eos import const
from eos.data.expression import Expression
from eos.data.effect.builder import InfoBuilder

class TestModItm(TestCase):
    """Test parsing of trees describing direct item modification"""

    def testBuildSuccess(self):
        eTgt = Expression(1, 24, value="Ship")
        eTgtAttr = Expression(2, 22, attributeId=9)
        eOptr = Expression(3, 21, value="PostPercent")
        eSrcAttr = Expression(4, 22, attributeId=327)
        eTgtSpec = Expression(5, 12, arg1=eTgt, arg2=eTgtAttr)
        eOptrTgt = Expression(6, 31, arg1=eOptr, arg2=eTgtSpec)
        eAddMod = Expression(7, 6, arg1=eOptrTgt, arg2=eSrcAttr)
        eRmMod = Expression(8, 58, arg1=eOptrTgt, arg2=eSrcAttr)
        infos, status = InfoBuilder().build(eAddMod, eRmMod)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = const.infoDuration
        self.assertEqual(info.type, expType, msg="info type must be duration (ID {})".format(expType))
        expGang = False
        self.assertIs(info.gang, expGang, msg="info gang flag must be {}".format(expGang))
        expLocation = const.locShip
        self.assertEqual(info.location, expLocation, msg="info target location must be ship (ID {})".format(expLocation))
        self.assertIsNone(info.filterType, msg="info target filter type must be None")
        self.assertIsNone(info.filterValue, msg="info target filter value must be None")
        expOperation = const.optrPostPercent
        self.assertEqual(info.operation, expOperation, msg="info operation must be PostPercent (ID {})".format(expOperation))
        expTgtAttr = 9
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcAttr = 327
        self.assertEqual(info.sourceAttributeId, expSrcAttr, msg="info source attribute ID must be {}".format(expSrcAttr))
        self.assertIsNone(info.sourceValue, msg="info source value must be None")
        self.assertIsNone(info.conditions, msg="info conditions must be None")
