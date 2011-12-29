from unittest import TestCase

from eos import const
from eos.data.expression import Expression
from eos.data.effect.builder import InfoBuilder

class TestGangItmMod(TestCase):
    """Test parsing of trees describing gang-mates' direct ship modification"""

    def testBuildSuccess(self):
        eTgtAttr = Expression(1, 22, attributeId=70)
        eOptr = Expression(2, 21, value="PostPercent")
        eSrcAttr = Expression(3, 22, attributeId=151)
        eTgtSpec = Expression(4, 40, arg1=eTgtAttr)
        eOptrTgt = Expression(5, 31, arg1=eOptr, arg2=eTgtSpec)
        eAddMod = Expression(6, 3, arg1=eOptrTgt, arg2=eSrcAttr)
        eRmMod = Expression(7, 55, arg1=eOptrTgt, arg2=eSrcAttr)
        infos, status = InfoBuilder().build(eAddMod, eRmMod)
        self.assertEqual(status, const.effectInfoOkFull, msg="expressions must be successfully parsed")
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = const.infoDuration
        self.assertEqual(info.type, expType, msg="info type must be duration (ID {})".format(expType))
        exGang = True
        self.assertIs(info.gang, exGang, msg="info gang flag must be {}".format(exGang))
        expLocation = const.locShip
        self.assertEqual(info.location, expLocation, msg="info target location must be ship (ID {})".format(expLocation))
        self.assertIsNone(info.filterType, msg="info target filter type must be None")
        self.assertIsNone(info.filterValue, msg="info target filter value must be None")
        expOperation = const.optrPostPercent
        self.assertEqual(info.operation, expOperation, msg="info operation must be PostPercent (ID {})".format(expOperation))
        expTgtAttr = 70
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcAttr = 151
        self.assertEqual(info.sourceAttributeId, expSrcAttr, msg="info source attribute ID must be {}".format(expSrcAttr))
        self.assertIsNone(info.conditions, msg="conditions must be None")
