#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
from eos.fit.attributeCalculator.modifier.modifierBuilder import ModifierBuilder
from eos.tests.environment import Logger
from eos.tests.eosTestCase import EosTestCase


class TestStubInt0(EosTestCase):
    """Test parsing of trees describing integer-0 stub"""

    def testBuildSuccess(self):
        ePreStub = self.ch.expression(expressionId=1, operandId=27, value="0")
        ePostStub = self.ch.expression(expressionId=2, operandId=27, value="0")
        effect = self.ch.effect(categoryId=0, preExpressionId=ePreStub.id, postExpressionId=ePostStub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)


class TestStubInt1(EosTestCase):
    """Test parsing of trees describing integer-1 stub"""

    def testBuildSuccess(self):
        ePreStub = self.ch.expression(expressionId=1, operandId=27, value="1")
        ePostStub = self.ch.expression(expressionId=2, operandId=27, value="1")
        effect = self.ch.effect(categoryId=0, preExpressionId=ePreStub.id, postExpressionId=ePostStub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)


class TestStubBoolTrue(EosTestCase):
    """Test parsing of trees describing boolean-True stub"""

    def tesBuildSuccess(self):
        ePreStub = self.ch.expression(expressionId=1, operandId=23, value="True")
        ePostStub = self.ch.expression(expressionId=2, operandId=23, value="True")
        effect = self.ch.effect(categoryId=0, preExpressionId=ePreStub.id, postExpressionId=ePostStub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)


class TestStubMixed(EosTestCase):
    """Test parsing of trees describing mixed form stubs"""

    def testBuildSuccess(self):
        ePreStub = self.ch.expression(expressionId=1, operandId=23, value="True")
        ePostStub = self.ch.expression(expressionId=2, operandId=27, value="0")
        effect = self.ch.effect(categoryId=0, preExpressionId=ePreStub.id, postExpressionId=ePostStub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)
