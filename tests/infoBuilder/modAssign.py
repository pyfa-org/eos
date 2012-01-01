from unittest import TestCase, expectedFailure

from eos import const
from eos.data.expression import Expression
from eos.data.effect.builder import InfoBuilder

class TestPreModAssignVal(TestCase):
    """Test parsing of trees describing increments by value applied in the beginning of the cycle"""

    @expectedFailure
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


class TestPostModAssignVal(TestCase):
    """Test parsing of trees describing increments by value applied in the end of the cycle"""

    @expectedFailure
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
