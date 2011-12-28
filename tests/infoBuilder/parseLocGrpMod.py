from unittest import TestCase

from eos import const
from eos.data.expression import Expression
from eos.data.effect.builder import InfoBuilder

class TestLocGrpMod(TestCase):
    def testBuildSuccess(self):
        eTgtLoc = Expression(1, 24, value="Ship")
        eTgtGrp = Expression(2, 26, groupId=46)
        eTgtAttr = Expression(3, 22, attributeId=6)
        eOptr = Expression(4, 21, value="PostPercent")
        eSrcAttr = Expression(5, 22, attributeId=1576)
        eTgtItms = Expression(6, 48, arg1=eTgtLoc, arg2=eTgtGrp)
        eTgtSpec = Expression(7, 12, arg1=eTgtItms, arg2=eTgtAttr)
        eOptrTgt = Expression(8, 31, arg1=eOptr, arg2=eTgtSpec)
        eAddMod = Expression(9, 7, arg1=eOptrTgt, arg2=eSrcAttr)
        eRmMod = Expression(10, 59, arg1=eOptrTgt, arg2=eSrcAttr)
        infos, status = InfoBuilder().build(eAddMod, eRmMod)
        self.assertEqual(status, const.effectInfoOkFull, msg="expressions must be successfully parsed")
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        # Get our info object
        info = infos.pop()
        # Info fields
        expType = const.infoDuration
        self.assertEqual(info.type, expType, msg="info type must be duration (ID {})".format(expType))
        self.assertFalse(info.gang, msg="info gang flag must be False")
        expLocation = const.locShip
        self.assertEqual(info.location, expLocation, msg="info target location must be ship (ID {})".format(expLocation))
        expFilterType = const.filterGroup
        self.assertEqual(info.filterType, expFilterType, msg="info target filter type must be group (ID {})".format(expFilterType))
        expFilterValue = 46
        self.assertEqual(info.filterValue, expFilterValue, msg="info target filter value must be {}".format(expFilterValue))
        expOperation = const.optrPostPercent
        self.assertEqual(info.operation, expOperation, msg="info operation must be PostPercent (ID {})".format(expOperation))
        expTgtAttr = 6
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expTgtAttr = 1576
        self.assertEqual(info.sourceAttributeId, expTgtAttr, msg="info source attribute ID must be {}".format(expTgtAttr))
        self.assertIsNone(info.conditions, msg="conditions must be None")
