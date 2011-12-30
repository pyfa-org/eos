from unittest import TestCase

from eos import const
from eos.data.expression import Expression
from eos.data.effect.builder import InfoBuilder

class TestItmMod(TestCase):
    """Test parsing of stub expressions"""

    def testInt0StubBuildSuccess(self):
        preStub = Expression(1, 27, value="0")
        postStub = Expression(2, 27, value="0")
        infos, status = InfoBuilder().build(preStub, postStub)
        self.assertEqual(status, const.effectInfoOkFull, msg="expressions must be successfully parsed")
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testInt1StubBuildSuccess(self):
        preStub = Expression(1, 27, value="1")
        postStub = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(preStub, postStub)
        self.assertEqual(status, const.effectInfoOkFull, msg="expressions must be successfully parsed")
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testBoolStubTrueBuildSuccess(self):
        preStub = Expression(1, 23, value="True")
        postStub = Expression(2, 23, value="True")
        infos, status = InfoBuilder().build(preStub, postStub)
        self.assertEqual(status, const.effectInfoOkFull, msg="expressions must be successfully parsed")
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testDiffStubBuildSuccess(self):
        preStub = Expression(1, 23, value="True")
        postStub = Expression(2, 27, value="0")
        infos, status = InfoBuilder().build(preStub, postStub)
        self.assertEqual(status, const.effectInfoOkFull, msg="expressions must be successfully parsed")
        self.assertEqual(len(infos), 0, msg="no infos must be generated")
