from unittest import TestCase

from eos import const
from eos.data.expression import Expression
from eos.data.effect.builder import InfoBuilder

class TestStubInt0(TestCase):
    """Test parsing of trees describing integer-0 stub"""

    def testBuildSuccess(self):
        ePreStub = Expression(1, 27, value="0")
        ePostStub = Expression(2, 27, value="0")
        infos, status = InfoBuilder().build(ePreStub, ePostStub)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")


class TestStubInt1(TestCase):
    """Test parsing of trees describing integer-1 stub"""

    def testBuildSuccess(self):
        ePreStub = Expression(1, 27, value="1")
        ePostStub = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(ePreStub, ePostStub)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")


class TestStubBoolTrue(TestCase):
    """Test parsing of trees describing boolean-True stub"""

    def tesBuildSuccess(self):
        ePreStub = Expression(1, 23, value="True")
        ePostStub = Expression(2, 23, value="True")
        infos, status = InfoBuilder().build(ePreStub, ePostStub)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")


class TestStubMixed(TestCase):
    """Test parsing of trees describing mixed form stubs"""

    def testBuildSuccess(self):
        preStub = Expression(1, 23, value="True")
        postStub = Expression(2, 27, value="0")
        infos, status = InfoBuilder().build(preStub, postStub)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")
