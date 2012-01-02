from unittest import TestCase

from eos import const
from eos.data.expression import Expression
from eos.data.effect.builder import InfoBuilder

class TestModLocSrq(TestCase):
    """Test parsing of trees describing modification filtered by location and skill requirement"""

    def testBuildSuccess(self):
        eTgtLoc = Expression(1, 24, value="Ship")
        eTgtSrq = Expression(2, 29, typeId=3307)
        eTgtAttr = Expression(3, 22, attributeId=54)
        eOptr = Expression(4, 21, value="PostPercent")
        eSrcAttr = Expression(5, 22, attributeId=491)
        eTgtItms = Expression(6, 49, arg1=eTgtLoc, arg2=eTgtSrq)
        eTgtSpec = Expression(7, 12, arg1=eTgtItms, arg2=eTgtAttr)
        eOptrTgt = Expression(8, 31, arg1=eOptr, arg2=eTgtSpec)
        eAddMod = Expression(9, 9, arg1=eOptrTgt, arg2=eSrcAttr)
        eRmMod = Expression(10, 61, arg1=eOptrTgt, arg2=eSrcAttr)
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
        expFilterType = const.filterSkill
        self.assertEqual(info.filterType, expFilterType, msg="info target filter type must be skill (ID {})".format(expFilterType))
        expFilterValue = 3307
        self.assertEqual(info.filterValue, expFilterValue, msg="info target filter value must be {}".format(expFilterValue))
        expOperation = const.optrPostPercent
        self.assertEqual(info.operation, expOperation, msg="info operation must be PostPercent (ID {})".format(expOperation))
        expTgtAttr = 54
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcType = const.srcAttr
        self.assertEqual(info.sourceType, expSrcType, msg="info source type must be attribute (ID {})".format(expSrcType))
        expSrcVal = 491
        self.assertEqual(info.sourceValue, expSrcVal, msg="info source value must be {}".format(expSrcVal))
        self.assertIsNone(info.conditions, msg="info conditions must be None")
