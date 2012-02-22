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


class TestInfoBuilderError(EosTestCase):
    """Test reaction to errors occurred during info building stage"""

    def testValidation(self):
        # To make invalid modifier, we've just took location
        # and group- filtered modifier and replaced its actual
        # top-level modifying operands with direct modifier
        eTgtLoc = Expression(None, 24, value="Ship")
        eTgtGrp = Expression(None, 26, expressionGroupId=46)
        eTgtAttr = Expression(None, 22, expressionAttributeId=6)
        eOptr = Expression(None, 21, value="PostPercent")
        eSrcAttr = Expression(None, 22, expressionAttributeId=1576)
        eTgtItms = Expression(None, 48, arg1=eTgtLoc, arg2=eTgtGrp)
        eTgtSpec = Expression(None, 12, arg1=eTgtItms, arg2=eTgtAttr)
        eOptrTgt = Expression(None, 31, arg1=eOptr, arg2=eTgtSpec)
        eAddMod = Expression(1, 6, arg1=eOptrTgt, arg2=eSrcAttr)
        eRmMod = Expression(2, 58, arg1=eOptrTgt, arg2=eSrcAttr)
        effect = Effect(20807, 0, preExpressionId=eAddMod.id, postExpressionId=eRmMod.id)
        eos = Eos({eAddMod.id: eAddMod, eRmMod.id: eRmMod})
        infos, status = InfoBuilder().build(effect, eos)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.infoBuilder")
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, "failed to validate modifiers for effect 20807")

    def testUnusedModifiers(self):
        # To produce unused modifiers, we're adding half of duration
        # modifier
        eTgt = Expression(None, 24, value="Ship")
        eTgtAttr = Expression(None, 22, expressionAttributeId=9)
        eOptr = Expression(None, 21, value="PostPercent")
        eSrcAttr = Expression(None, 22, expressionAttributeId=327)
        eTgtSpec = Expression(None, 12, arg1=eTgt, arg2=eTgtAttr)
        eOptrTgt = Expression(None, 31, arg1=eOptr, arg2=eTgtSpec)
        eAddMod = Expression(1, 6, arg1=eOptrTgt, arg2=eSrcAttr)
        ePostStub = Expression(2, 27, value="1")
        effect = Effect(799, 0, preExpressionId=eAddMod.id, postExpressionId=ePostStub.id)
        eos = Eos({eAddMod.id: eAddMod, ePostStub.id: ePostStub})
        infos, status = InfoBuilder().build(effect, eos)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(infos), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.infoBuilder")
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, "unused modifiers left after generating infos for effect 799")
