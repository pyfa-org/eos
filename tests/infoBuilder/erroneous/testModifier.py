#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
#
# This file is part of Eos.
#
# Eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Eos. If not, see <http://www.gnu.org/licenses/>.
#===============================================================================


from eos.const import EffectBuildStatus
from eos.eve.effect import Effect
from eos.eve.expression import Expression
from eos.fit.attributeCalculator.info.infoBuilder import InfoBuilder
from eos.tests.infoBuilder.environment import Eos, Logger
from eos.tests.eosTestCase import EosTestCase


class TestModifierBuilderError(EosTestCase):
    """Test reaction to errors occurred during modifier building stage"""

    def testData(self):
        effect = Effect(900, 0, preExpressionId=902, postExpressionId=28)
        eos = Eos({})
        infos, status = InfoBuilder().build(effect, eos)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.infoBuilder")
        self.assertEqual(logRecord.levelno, Logger.ERROR)
        self.assertEqual(logRecord.msg, "failed to parse expressions of effect 900: unable to fetch expression 902 from tree with root 902")

    def testGeneric(self):
        ePreStub = Expression(1, 27, value="1")
        ePost = Expression(2, 1009)
        effect = Effect(568, 0, preExpressionId=ePreStub.id, postExpressionId=ePost.id)
        eos = Eos({ePreStub.id: ePreStub, ePost.id: ePost})
        infos, status = InfoBuilder().build(effect, eos)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.infoBuilder")
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, "failed to parse expressions of effect 568: unknown generic operand 1009")

    def testIntStub(self):
        ePreStub = Expression(1, 27, value="0")
        ePost = Expression(2, 27, value="6")
        effect = Effect(662, 0, preExpressionId=ePreStub.id, postExpressionId=ePost.id)
        eos = Eos({ePreStub.id: ePreStub, ePost.id: ePost})
        infos, status = InfoBuilder().build(effect, eos)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.infoBuilder")
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, "failed to parse expressions of effect 662: integer stub with unexpected value 6")

    def testBoolStub(self):
        ePreStub = Expression(1, 27, value="0")
        ePost = Expression(2, 23, value="False")
        effect = Effect(92, 0, preExpressionId=ePreStub.id, postExpressionId=ePost.id)
        eos = Eos({ePreStub.id: ePreStub, ePost.id: ePost})
        infos, status = InfoBuilder().build(effect, eos)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.infoBuilder")
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, "failed to parse expressions of effect 92: boolean stub with unexpected value False")

    def testUnknown(self):
        ePreStub = Expression(1, 27, value="0")
        ePost = Expression(2, 23, value="Garbage")
        effect = Effect(66, 0, preExpressionId=ePreStub.id, postExpressionId=ePost.id)
        eos = Eos({ePreStub.id: ePreStub, ePost.id: ePost})
        infos, status = InfoBuilder().build(effect, eos)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.infoBuilder")
        self.assertEqual(logRecord.levelno, Logger.ERROR)
        self.assertEqual(logRecord.msg, "failed to parse expressions of effect 66 due to unknown reason")
