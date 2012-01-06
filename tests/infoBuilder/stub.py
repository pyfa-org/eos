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
