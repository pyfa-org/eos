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


from eos.const.eos import EffectBuildStatus, FilterType
from eos.const.eve import EffectCategory, Operand
from eos.tests.modifierBuilder.modBuilderTestCase import ModBuilderTestCase


class TestSelfType(ModBuilderTestCase):
    """Test parsing of trees describing modification which contains reference to typeID of its carrier"""

    def testBuildSuccess(self):
        eTgtOwn = self.ef.make(1, operandID=Operand.defLoc, expressionValue='Char')
        eSelf = self.ef.make(2, operandID=Operand.defLoc, expressionValue='Self')
        eSelfType = self.ef.make(3, operandID=Operand.getType, arg1=eSelf['expressionID'])
        eTgtAttr = self.ef.make(4, operandID=Operand.defAttr, expressionAttributeID=64)
        eOptr = self.ef.make(5, operandID=Operand.defOptr, expressionValue='PostPercent')
        eSrcAttr = self.ef.make(6, operandID=Operand.defAttr, expressionAttributeID=292)
        eTgtItms = self.ef.make(7, operandID=Operand.locSrq, arg1=eTgtOwn['expressionID'], arg2=eSelfType['expressionID'])
        eTgtSpec = self.ef.make(8, operandID=Operand.itmAttr, arg1=eTgtItms['expressionID'], arg2=eTgtAttr['expressionID'])
        eOptrTgt = self.ef.make(9, operandID=Operand.optrTgt, arg1=eOptr['expressionID'], arg2=eTgtSpec['expressionID'])
        eAddMod = self.ef.make(10, operandID=Operand.addOwnSrqMod, arg1=eOptrTgt['expressionID'], arg2=eSrcAttr['expressionID'])
        eRmMod = self.ef.make(11, operandID=Operand.rmOwnSrqMod, arg1=eOptrTgt['expressionID'], arg2=eSrcAttr['expressionID'])
        modifiers, status = self.runBuilder(eAddMod['expressionID'], eRmMod['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.filterType, FilterType.skillSelf)
        self.assertEqual(modifier.filterValue, None)
        self.assertEqual(len(self.log), 0)
