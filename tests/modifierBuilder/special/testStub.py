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
from eos.tests.modifierBuilder.modBuilderTestCase import ModBuilderTestCase


class TestStubInt0(ModBuilderTestCase):
    """Test parsing of trees describing integer-0 stub"""

    def testBuildSuccess(self):
        ePreStub = self.ef.make(1, operandId=27, expressionValue='0')
        ePostStub = self.ef.make(2, operandId=27, expressionValue='0')
        modifiers, status = self.runBuilder(ePreStub['expressionId'], ePostStub['expressionId'], 0)
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)


class TestStubInt1(ModBuilderTestCase):
    """Test parsing of trees describing integer-1 stub"""

    def testBuildSuccess(self):
        ePreStub = self.ef.make(1, operandId=27, expressionValue='1')
        ePostStub = self.ef.make(2, operandId=27, expressionValue='1')
        modifiers, status = self.runBuilder(ePreStub['expressionId'], ePostStub['expressionId'], 0)
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)


class TestStubBoolTrue(ModBuilderTestCase):
    """Test parsing of trees describing boolean-True stub"""

    def tesBuildSuccess(self):
        ePreStub = self.ef.make(1, operandId=23, expressionValue='True')
        ePostStub = self.ef.make(2, operandId=23, expressionValue='True')
        modifiers, status = self.runBuilder(ePreStub['expressionId'], ePostStub['expressionId'], 0)
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)


class TestStubMixed(ModBuilderTestCase):
    """Test parsing of trees describing mixed form stubs"""

    def testBuildSuccess(self):
        ePreStub = self.ef.make(1, operandId=23, expressionValue='True')
        ePostStub = self.ef.make(2, operandId=27, expressionValue='0')
        modifiers, status = self.runBuilder(ePreStub['expressionId'], ePostStub['expressionId'], 0)
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)
