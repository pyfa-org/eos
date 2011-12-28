from unittest import TestCase

from eos import const
from eos.data.expression import Expression
from eos.data.effect.builder import InfoBuilder

class TestItmMod(TestCase):
    def testSuccess(self):
        target = Expression(1, 24, value="Ship")
        tgtAttr = Expression(2, 22, attributeId=9)
        operator = Expression(3, 21, value="PostPercent")
        srcAttr = Expression(4, 22, attributeId=327)
        tgtSpec = Expression(5, 12, arg1=target, arg2=tgtAttr)
        optrTgt = Expression(6, 31, arg1=operator, arg2=tgtSpec)
        addMod = Expression(7, 6, arg1=optrTgt, arg2=srcAttr)
        rmMod = Expression(8, 58, arg1=optrTgt, arg2=srcAttr)
        builder = InfoBuilder()
        infos, status = builder.build(addMod, rmMod)
        # Parsing status
        self.assertEqual(status, const.effectInfoOkFull)
        # Amount of infos we got from tree
        self.assertEqual(len(infos), 1)
        # Get our info object
        info = infos.pop()
        # Info fields
        self.assertEqual(info.type, const.infoDuration)
        self.assertFalse(info.gang)
        self.assertEqual(info.location, const.locShip)
        self.assertIsNone(info.filterType)
        self.assertIsNone(info.filterValue)
        self.assertEqual(info.operation, const.optrPostPercent)
        self.assertEqual(info.targetAttributeId, 9)
        self.assertEqual(info.sourceAttributeId, 327)
        self.assertIsNone(info.conditions)
