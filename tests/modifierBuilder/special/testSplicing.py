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
from eos.fit.attributeCalculator.modifier.modifierBuilder import ModifierBuilder
from eos.tests.environment import Logger
from eos.tests.eosTestCase import EosTestCase
from eos.tests.modifierBuilder.environment import DataHandler


class TestSplicing(EosTestCase):
    """Test parsing of trees describing joins of multiple operations applied onto items"""

    def testBuildSuccess(self):
        dh = DataHandler()
        eTgtLoc = Expression(dataHandler=dh, expressionId=1, operandId=24, value="Target")
        eTgtSrq = Expression(dataHandler=dh, expressionId=2, operandId=29, expressionTypeId=3300)
        eTgtAttr1 = Expression(dataHandler=dh, expressionId=3, operandId=22, expressionAttributeId=54)
        eTgtAttr2 = Expression(dataHandler=dh, expressionId=4, operandId=22, expressionAttributeId=158)
        eTgtAttr3 = Expression(dataHandler=dh, expressionId=5, operandId=22, expressionAttributeId=160)
        eOptr = Expression(dataHandler=dh, expressionId=6, operandId=21, value="PostPercent")
        eSrcAttr1 = Expression(dataHandler=dh, expressionId=7, operandId=22, expressionAttributeId=351)
        eSrcAttr2 = Expression(dataHandler=dh, expressionId=8, operandId=22, expressionAttributeId=349)
        eSrcAttr3 = Expression(dataHandler=dh, expressionId=9, operandId=22, expressionAttributeId=767)
        eTgtItms = Expression(dataHandler=dh, expressionId=10, operandId=49, arg1Id=eTgtLoc.id, arg2Id=eTgtSrq.id)
        eTgtSpec1 = Expression(dataHandler=dh, expressionId=11, operandId=12, arg1Id=eTgtItms.id, arg2Id=eTgtAttr1.id)
        eTgtSpec2 = Expression(dataHandler=dh, expressionId=12, operandId=12, arg1Id=eTgtItms.id, arg2Id=eTgtAttr2.id)
        eTgtSpec3 = Expression(dataHandler=dh, expressionId=13, operandId=12, arg1Id=eTgtItms.id, arg2Id=eTgtAttr3.id)
        eOptrTgt1 = Expression(dataHandler=dh, expressionId=14, operandId=31, arg1Id=eOptr.id, arg2Id=eTgtSpec1.id)
        eOptrTgt2 = Expression(dataHandler=dh, expressionId=15, operandId=31, arg1Id=eOptr.id, arg2Id=eTgtSpec2.id)
        eOptrTgt3 = Expression(dataHandler=dh, expressionId=16, operandId=31, arg1Id=eOptr.id, arg2Id=eTgtSpec3.id)
        eAddMod1 = Expression(dataHandler=dh, expressionId=17, operandId=9, arg1Id=eOptrTgt1.id, arg2Id=eSrcAttr1.id)
        eAddMod2 = Expression(dataHandler=dh, expressionId=18, operandId=9, arg1Id=eOptrTgt2.id, arg2Id=eSrcAttr2.id)
        eAddMod3 = Expression(dataHandler=dh, expressionId=19, operandId=9, arg1Id=eOptrTgt3.id, arg2Id=eSrcAttr3.id)
        eRmMod1 = Expression(dataHandler=dh, expressionId=20, operandId=61, arg1Id=eOptrTgt1.id, arg2Id=eSrcAttr1.id)
        eRmMod2 = Expression(dataHandler=dh, expressionId=21, operandId=61, arg1Id=eOptrTgt2.id, arg2Id=eSrcAttr2.id)
        eRmMod3 = Expression(dataHandler=dh, expressionId=22, operandId=61, arg1Id=eOptrTgt3.id, arg2Id=eSrcAttr3.id)
        eAddSplice1 = Expression(dataHandler=dh, expressionId=23, operandId=17, arg1Id=eAddMod1.id, arg2Id=eAddMod3.id)
        eAddSplice2 = Expression(dataHandler=dh, expressionId=24, operandId=17, arg1Id=eAddMod2.id, arg2Id=eAddSplice1.id)
        eRmSplice1 = Expression(dataHandler=dh, expressionId=25, operandId=17, arg1Id=eRmMod1.id, arg2Id=eRmMod3.id)
        eRmSplice2 = Expression(dataHandler=dh, expressionId=26, operandId=17, arg1Id=eRmMod2.id, arg2Id=eRmSplice1.id)
        dh.addExpressions((eTgtLoc, eTgtSrq, eTgtAttr1, eTgtAttr2, eTgtAttr3, eOptr, eSrcAttr1, eSrcAttr2, eSrcAttr3, eTgtItms,
                           eTgtSpec1, eTgtSpec2, eTgtSpec3, eOptrTgt1, eOptrTgt2, eOptrTgt3, eAddMod1, eAddMod2, eAddMod3,
                           eRmMod1, eRmMod2, eRmMod3, eAddSplice1, eAddSplice2, eRmSplice1, eRmSplice2))
        effect = Effect(dataHandler=dh, categoryId=0, preExpressionId=eAddSplice2.id, postExpressionId=eRmSplice2.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 3)
