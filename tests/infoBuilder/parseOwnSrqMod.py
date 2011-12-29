from unittest import TestCase

from eos import const
from eos.data.expression import Expression
from eos.data.effect.builder import InfoBuilder

class TestOwnSrqMod(TestCase):
    """Test parsing of trees describing modification filtered by owner and skill requirement"""

    def testBuildSuccess(self):
        eTgtOwn = Expression(1, 24, value="Char")
        eTgtSrq = Expression(2, 29, typeId=3412)
        eTgtAttr = Expression(3, 22, attributeId=1372)
        eOptr = Expression(4, 21, value="PostPercent")
        eSrcAttr = Expression(5, 22, attributeId=1156)
        eTgtItms = Expression(6, 49, arg1=eTgtOwn, arg2=eTgtSrq)
        eTgtSpec = Expression(7, 12, arg1=eTgtItms, arg2=eTgtAttr)
        eOptrTgt = Expression(8, 31, arg1=eOptr, arg2=eTgtSpec)
        eAddMod = Expression(9, 11, arg1=eOptrTgt, arg2=eSrcAttr)
        eRmMod = Expression(10, 62, arg1=eOptrTgt, arg2=eSrcAttr)
        infos, status = InfoBuilder().build(eAddMod, eRmMod)
        self.assertEqual(status, const.effectInfoOkFull, msg="expressions must be successfully parsed")
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = const.infoDuration
        self.assertEqual(info.type, expType, msg="info type must be duration (ID {})".format(expType))
        self.assertFalse(info.gang, msg="info gang flag must be False")
        expLocation = const.locSpace
        self.assertEqual(info.location, expLocation, msg="info target location must be space (ID {})".format(expLocation))
        expFilterType = const.filterSkill
        self.assertEqual(info.filterType, expFilterType, msg="info target filter type must be skill (ID {})".format(expFilterType))
        expFilterValue = 3412
        self.assertEqual(info.filterValue, expFilterValue, msg="info target filter value must be {}".format(expFilterValue))
        expOperation = const.optrPostPercent
        self.assertEqual(info.operation, expOperation, msg="info operation must be PostPercent (ID {})".format(expOperation))
        expTgtAttr = 1372
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcAttr = 1156
        self.assertEqual(info.sourceAttributeId, expSrcAttr, msg="info source attribute ID must be {}".format(expSrcAttr))
        self.assertIsNone(info.conditions, msg="conditions must be None")
