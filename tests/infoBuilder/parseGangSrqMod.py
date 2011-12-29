from unittest import TestCase

from eos import const
from eos.data.expression import Expression
from eos.data.effect.builder import InfoBuilder

class TestGangSrqMod(TestCase):
    """Test parsing of trees describing gang-mates' ship modules modification filtered by skill requirement"""

    def testBuildSuccess(self):
        eTgtSrq = Expression(1, 29, typeId=3435)
        eTgtAttr = Expression(2, 22, attributeId=54)
        eOptr = Expression(3, 21, value="PostPercent")
        eSrcAttr = Expression(4, 22, attributeId=833)
        eTgtSpec = Expression(5, 64, arg1=eTgtSrq, arg2=eTgtAttr)
        eOptrTgt = Expression(6, 31, arg1=eOptr, arg2=eTgtSpec)
        eAddMod = Expression(7, 5, arg1=eOptrTgt, arg2=eSrcAttr)
        eRmMod = Expression(8, 57, arg1=eOptrTgt, arg2=eSrcAttr)
        infos, status = InfoBuilder().build(eAddMod, eRmMod)
        self.assertEqual(status, const.effectInfoOkFull, msg="expressions must be successfully parsed")
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = const.infoDuration
        self.assertEqual(info.type, expType, msg="info type must be duration (ID {})".format(expType))
        self.assertTrue(info.gang, msg="info gang flag must be True")
        expLocation = const.locShip
        self.assertEqual(info.location, expLocation, msg="info target location must be ship (ID {})".format(expLocation))
        expFilterType = const.filterSkill
        self.assertEqual(info.filterType, expFilterType, msg="info target filter type must be skill (ID {})".format(expFilterType))
        expFilterValue = 3435
        self.assertEqual(info.filterValue, expFilterValue, msg="info target filter value must be {}".format(expFilterValue))
        expOperation = const.optrPostPercent
        self.assertEqual(info.operation, expOperation, msg="info operation must be PostPercent (ID {})".format(expOperation))
        expTgtAttr = 54
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcAttr = 833
        self.assertEqual(info.sourceAttributeId, expSrcAttr, msg="info source attribute ID must be {}".format(expSrcAttr))
        self.assertIsNone(info.conditions, msg="conditions must be None")
