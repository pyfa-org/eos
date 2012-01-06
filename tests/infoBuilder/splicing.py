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

from unittest import TestCase

from eos import const
from eos.data.expression import Expression
from eos.data.effect.builder import InfoBuilder

class TestSplicing(TestCase):
    """Test parsing of trees describing joins of multiple actual modifiers"""

    def testBuildSuccess(self):
        eTgtLoc = Expression(1, 24, value="Target")
        eTgtSrq = Expression(2, 29, typeId=3300)
        eTgtAttr1 = Expression(3, 22, attributeId=54)
        eTgtAttr2 = Expression(4, 22, attributeId=158)
        eTgtAttr3 = Expression(5, 22, attributeId=160)
        eOptr = Expression(6, 21, value="PostPercent")
        eSrcAttr1 = Expression(7, 22, attributeId=351)
        eSrcAttr2 = Expression(8, 22, attributeId=349)
        eSrcAttr3 = Expression(9, 22, attributeId=767)
        eTgtItms = Expression(10, 49, arg1=eTgtLoc, arg2=eTgtSrq)
        eTgtSpec1 = Expression(11, 12, arg1=eTgtItms, arg2=eTgtAttr1)
        eTgtSpec2 = Expression(12, 12, arg1=eTgtItms, arg2=eTgtAttr2)
        eTgtSpec3 = Expression(13, 12, arg1=eTgtItms, arg2=eTgtAttr3)
        eOptrTgt1 = Expression(14, 31, arg1=eOptr, arg2=eTgtSpec1)
        eOptrTgt2 = Expression(15, 31, arg1=eOptr, arg2=eTgtSpec2)
        eOptrTgt3 = Expression(16, 31, arg1=eOptr, arg2=eTgtSpec3)
        eAddMod1 = Expression(17, 9, arg1=eOptrTgt1, arg2=eSrcAttr1)
        eAddMod2 = Expression(18, 9, arg1=eOptrTgt2, arg2=eSrcAttr2)
        eAddMod3 = Expression(19, 9, arg1=eOptrTgt3, arg2=eSrcAttr3)
        eRmMod1 = Expression(20, 61, arg1=eOptrTgt1, arg2=eSrcAttr1)
        eRmMod2 = Expression(21, 61, arg1=eOptrTgt2, arg2=eSrcAttr2)
        eRmMod3 = Expression(22, 61, arg1=eOptrTgt3, arg2=eSrcAttr3)
        eAddSplice1 = Expression(23, 17, arg1=eAddMod1, arg2=eAddMod3)
        eAddSplice2 = Expression(24, 17, arg1=eAddMod2, arg2=eAddSplice1)
        eRmSplice1 = Expression(25, 17, arg1=eRmMod1, arg2=eRmMod3)
        eRmSplice2 = Expression(26, 17, arg1=eRmMod2, arg2=eRmSplice1)
        infos, status = InfoBuilder().build(eAddSplice2, eRmSplice2)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 3, msg="three infos must be generated")
