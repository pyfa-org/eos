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

from eos.const import Location, EffectBuildStatus, AtomType, AtomLogicOperator, AtomComparisonOperator, AtomMathOperator
from eos.eve.expression import Expression
from eos.fit.calc.info.builder.infoBuilder import InfoBuilder


class TestCondition(TestCase):
    """Test parsing of trees describing conditions"""

    def setUp(self):
        # Create some modifier which makes sense for builder, we'll use it instead
        # of stub to test conditions which are assigned to it
        eTgt = Expression(None, 24, value="Ship")
        eTgtAttr = Expression(None, 22, expressionAttributeId=15)
        eOptr = Expression(None, 21, value="ModAdd")
        eSrcAttr = Expression(None, 22, expressionAttributeId=30)
        eTgtSpec = Expression(None, 12, arg1=eTgt, arg2=eTgtAttr)
        eOptrTgt = Expression(None, 31, arg1=eOptr, arg2=eTgtSpec)
        self.eAddMod = Expression(None, 6, arg1=eOptrTgt, arg2=eSrcAttr)
        self.eRmMod = Expression(None, 58, arg1=eOptrTgt, arg2=eSrcAttr)

    def testLogic(self):
        # Make a tree so we can focus on logic testing
        eTgtShip = Expression(None, 24, value="Ship")
        eAttr = Expression(None, 22, expressionAttributeId=11)
        eVal1 = Expression(None, 27, value="0")
        eVal2 = Expression(None, 27, value="100")
        eVal3 = Expression(None, 27, value="-1")
        eTgtSpec = Expression(None, 35, arg1=eTgtShip, arg2=eAttr)
        eComp1 = Expression(None, 39, arg1=eTgtSpec, arg2=eVal1)
        eComp2 = Expression(None, 39, arg1=eVal2, arg2=eTgtSpec)
        eComp3 = Expression(None, 33, arg1=eTgtSpec, arg2=eVal3)
        eLogic1 = Expression(None, 10, arg1=eComp1, arg2=eComp2)
        eLogic2 = Expression(None, 52, arg1=eLogic1, arg2=eComp3)
        eIfThen = Expression(None, 41, arg1=eLogic2, arg2=self.eAddMod)
        eElseStub = Expression(None, 27, value="1")
        eIfElse = Expression(None, 52, arg1=eIfThen, arg2=eElseStub)

        infos, status = InfoBuilder().build(eIfElse, self.eRmMod, 0)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        self.assertIsNotNone(info.conditions, msg="info conditions must be not None")

        currentAtom = info.conditions
        expAtomType = AtomType.logic
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be logic (ID {})".format(expAtomType))
        expAtomOptr = AtomLogicOperator.or_
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be logical or (ID {})".format(expAtomOptr))

        currentAtom = info.conditions.child1
        expAtomType = AtomType.logic
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be logic (ID {})".format(expAtomType))
        expAtomOptr = AtomLogicOperator.and_
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be logical and (ID {})".format(expAtomOptr))

        # Check logic atom children types
        currentAtom = info.conditions.child2
        expAtomType = AtomType.comparison
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))

        currentAtom = info.conditions.child1.child1
        expAtomType = AtomType.comparison
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))

        currentAtom = info.conditions.child1.child2
        expAtomType = AtomType.comparison
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))

    def testComparison(self):
        # Make tree so we can test basic comparison
        eTgtShip = Expression(None, 24, value="Ship")
        eAttr = Expression(None, 22, expressionAttributeId=11)
        eVal = Expression(None, 27, value="100")
        eTgtSpec = Expression(None, 35, arg1=eTgtShip, arg2=eAttr)
        eComparison = Expression(None, 39, arg1=eTgtSpec, arg2=eVal)
        eIfThen = Expression(None, 41, arg1=eComparison, arg2=self.eAddMod)
        eElseStub = Expression(None, 27, value="1")
        eIfElse = Expression(None, 52, arg1=eIfThen, arg2=eElseStub)

        infos, status = InfoBuilder().build(eIfElse, self.eRmMod, 0)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        self.assertIsNotNone(info.conditions, msg="info conditions must be not None")

        currentAtom = info.conditions
        expAtomType = AtomType.comparison
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))
        expAtomOptr = AtomComparisonOperator.greaterOrEqual
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be greater than or equal (ID {})".format(expAtomOptr))

        # Check children types
        currentAtom = info.conditions.child1
        expAtomType = AtomType.valueReference
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be value reference (ID {})".format(expAtomType))

        currentAtom = info.conditions.child2
        expAtomType = AtomType.value
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be value (ID {})".format(expAtomType))

    def testMath(self):
        # Create a tree so we can check math atoms and their child types
        eTgtShip = Expression(None, 24, value="Ship")
        eAttr1 = Expression(None, 22, expressionAttributeId=11)
        eAttr2 = Expression(None, 2, expressionAttributeId=49)
        eAttr3 = Expression(None, 22, expressionAttributeId=5)
        eVal = Expression(None, 27, value="53")
        eTgtSpec1 = Expression(None, 35, arg1=eTgtShip, arg2=eAttr1)
        eTgtSpec2 = Expression(None, 35, arg1=eTgtShip, arg2=eAttr2)
        eTgtSpec3 = Expression(None, 35, arg1=eTgtShip, arg2=eAttr3)
        eMath1 = Expression(None, 1, arg1=eTgtSpec1, arg2=eVal)
        eMath2 = Expression(None, 68, arg1=eMath1, arg2=eTgtSpec2)
        eComparison = Expression(None, 39, arg1=eMath2, arg2=eTgtSpec3)
        eIfThen = Expression(None, 41, arg1=eComparison, arg2=self.eAddMod)
        eElseStub = Expression(None, 27, value="1")
        eIfElse = Expression(None, 52, arg1=eIfThen, arg2=eElseStub)

        infos, status = InfoBuilder().build(eIfElse, self.eRmMod, 0)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        self.assertIsNotNone(info.conditions, msg="info conditions must be not None")

        currentAtom = info.conditions
        expAtomType = AtomType.comparison
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))

        currentAtom = info.conditions.child1
        expAtomType = AtomType.math
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be math (ID {})".format(expAtomType))
        expAtomOptr = AtomMathOperator.subtract
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be subtraction (ID {})".format(expAtomOptr))

        currentAtom = info.conditions.child1.child1
        expAtomType = AtomType.math
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be math (ID {})".format(expAtomType))
        expAtomOptr = AtomMathOperator.add
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be addition (ID {})".format(expAtomOptr))

        # Check math children types
        currentAtom = info.conditions.child1.child1.child1
        expAtomType = AtomType.valueReference
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be value reference (ID {})".format(expAtomType))

        currentAtom = info.conditions.child1.child1.child2
        expAtomType = AtomType.value
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be value (ID {})".format(expAtomType))

        currentAtom = info.conditions.child1.child2
        expAtomType = AtomType.valueReference
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be value reference (ID {})".format(expAtomType))

        currentAtom = info.conditions.child2
        expAtomType = AtomType.valueReference
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be value reference (ID {})".format(expAtomType))

    def testTerminals(self):
        # Here we'll check value and attribute reference terminals
        eTgtSelf = Expression(None, 24, value="Self")
        eAttr = Expression(None, 22, expressionAttributeId=87)
        eVal = Expression(None, 27, value="-50")
        eTgtSpec = Expression(None, 35, arg1=eTgtSelf, arg2=eAttr)
        eComparison = Expression(None, 39, arg1=eTgtSpec, arg2=eVal)
        eIfThen = Expression(None, 41, arg1=eComparison, arg2=self.eAddMod)
        eElseStub = Expression(None, 27, value="1")
        eIfElse = Expression(None, 52, arg1=eIfThen, arg2=eElseStub)

        infos, status = InfoBuilder().build(eIfElse, self.eRmMod, 0)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        self.assertIsNotNone(info.conditions, msg="info conditions must be not None")

        currentAtom = info.conditions
        expAtomType = AtomType.comparison
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))

        currentAtom = info.conditions.child1
        expAtomType = AtomType.valueReference
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be value reference (ID {})".format(expAtomType))
        expAtomCarrier = Location.self_
        self.assertEqual(currentAtom.carrier, expAtomCarrier, msg="atom carrier must be self (ID {})".format(expAtomCarrier))
        expAtomAttr = 87
        self.assertEqual(currentAtom.attribute, expAtomAttr, msg="atom attribute ID must be {}".format(expAtomAttr))

        currentAtom = info.conditions.child2
        expAtomType = AtomType.value
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be value (ID {})".format(expAtomType))
        expAtomValue = -50
        self.assertEqual(currentAtom.value, expAtomValue, msg="atom value must be {}".format(expAtomValue))

    def testNested(self):
        # Tree which has two if-then-else blocks
        eTgtShip = Expression(None, 24, value="Ship")
        eAttr1 = Expression(None, 22, expressionAttributeId=11)
        eAttr2 = Expression(None, 22, expressionAttributeId=76)
        eVal1 = Expression(None, 27, value="5")
        eVal2 = Expression(None, 27, value="25")
        eStub = Expression(None, 27, value="1")
        eTgtSpec1 = Expression(None, 35, arg1=eTgtShip, arg2=eAttr1)
        eTgtSpec2 = Expression(None, 35, arg1=eTgtShip, arg2=eAttr2)
        eComp1 = Expression(None, 33, arg1=eTgtSpec1, arg2=eVal1)
        eComp2 = Expression(None, 38, arg1=eTgtSpec2, arg2=eVal2)
        eIfThen1 = Expression(None, 41, arg1=eComp1, arg2=self.eAddMod)
        eIfElse1 = Expression(None, 52, arg1=eIfThen1, arg2=eStub)
        eSplicedCondStub = Expression(None, 17, arg1=eIfElse1, arg2=eStub)
        eIfThen2 = Expression(None, 41, arg1=eComp2, arg2=eSplicedCondStub)
        eIfElse2 = Expression(None, 52, arg1=eIfThen2, arg2=eStub)

        infos, status = InfoBuilder().build(eIfElse2, self.eRmMod, 0)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        self.assertIsNotNone(info.conditions, msg="info conditions must be not None")

        # Nested ifs are joined using logical and
        currentAtom = info.conditions
        expAtomType = AtomType.logic
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be logic (ID {})".format(expAtomType))
        expAtomOptr = AtomLogicOperator.and_
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be logical and (ID {})".format(expAtomOptr))

        # Check children types
        currentAtom = info.conditions.child1
        expAtomType = AtomType.comparison
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))

        currentAtom = info.conditions.child2
        expAtomType = AtomType.comparison
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))

    def testInversion(self):
        # As each info object has its own copy of conditions, for infos located
        # in else clauses some conditions are inverted, here we test it
        eTgtShip = Expression(None, 24, value="Ship")
        eAttr1 = Expression(None, 22, expressionAttributeId=11)
        eAttr2 = Expression(None, 22, expressionAttributeId=76)
        eAttr3 = Expression(None, 22, expressionAttributeId=53)
        eVal1 = Expression(None, 27, value="5")
        eVal2 = Expression(None, 27, value="25")
        eVal3 = Expression(None, 27, value="125")
        eStub = Expression(None, 27, value="1")
        eTgtSpec1 = Expression(None, 35, arg1=eTgtShip, arg2=eAttr1)
        eTgtSpec2 = Expression(None, 35, arg1=eTgtShip, arg2=eAttr2)
        eTgtSpec3 = Expression(None, 35, arg1=eTgtShip, arg2=eAttr3)
        eComp1 = Expression(None, 33, arg1=eTgtSpec1, arg2=eVal1)
        eComp2 = Expression(None, 39, arg1=eTgtSpec2, arg2=eVal2)
        eComp3 = Expression(None, 38, arg1=eTgtSpec3, arg2=eVal3)
        eLogic = Expression(None, 10, arg1=eComp1, arg2=eComp2)
        eIfThen1 = Expression(None, 41, arg1=eLogic, arg2=eStub)
        eIfElse1 = Expression(None, 52, arg1=eIfThen1, arg2=self.eAddMod)
        eSplicedCondStub = Expression(None, 17, arg1=eIfElse1, arg2=eStub)
        eIfThen2 = Expression(None, 41, arg1=eComp3, arg2=eSplicedCondStub)
        eIfElse2 = Expression(None, 52, arg1=eIfThen2, arg2=eStub)

        infos, status = InfoBuilder().build(eIfElse2, self.eRmMod, 0)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        self.assertIsNotNone(info.conditions, msg="info conditions must be not None")

        # We have nested conditions, logical and generated by them
        # is not affected by inversion in this case, as it's above inversion
        currentAtom = info.conditions
        expAtomType = AtomType.logic
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be logic (ID {})".format(expAtomType))
        expAtomOptr = AtomLogicOperator.and_
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be logical and (ID {})".format(expAtomOptr))

        # Affected: and -> or
        currentAtom = info.conditions.child2
        expAtomType = AtomType.logic
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be logic (ID {})".format(expAtomType))
        expAtomOptr = AtomLogicOperator.or_
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be logical or (ID {})".format(expAtomOptr))

        # Affected: == -> !=
        currentAtom = info.conditions.child2.child1
        expAtomType = AtomType.comparison
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))
        expAtomOptr = AtomComparisonOperator.notEqual
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be not equal (ID {})".format(expAtomOptr))

        # Affected: >= -> <
        currentAtom = info.conditions.child2.child2
        expAtomType = AtomType.comparison
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))
        expAtomOptr = AtomComparisonOperator.less
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be less (ID {})".format(expAtomOptr))

        # This atom is also on more upper level that inverted if-then-else clause to which
        # belongs our modifier, so it shouldn't be affected too
        currentAtom = info.conditions.child1
        expAtomType = AtomType.comparison
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))
        expAtomOptr = AtomComparisonOperator.greater
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be greater than (ID {})".format(expAtomOptr))

    def testUnification(self):
        # If we have 2 similar duration modifiers with different conditions,
        # they should be combined into one by builder
        eTgtShip = Expression(None, 24, value="Ship")
        eAttr = Expression(None, 22, expressionAttributeId=175)
        eVal1 = Expression(None, 27, value="8")
        eVal2 = Expression(None, 27, value="56")
        eStub = Expression(None, 27, value="1")
        eTgtSpec = Expression(None, 35, arg1=eTgtShip, arg2=eAttr)
        eComp1 = Expression(None, 33, arg1=eTgtSpec, arg2=eVal1)
        eComp2 = Expression(None, 38, arg1=eTgtSpec, arg2=eVal2)
        eIfThen1 = Expression(None, 41, arg1=eComp1, arg2=self.eAddMod)
        eIfElse1 = Expression(None, 52, arg1=eIfThen1, arg2=eStub)
        eIfThen2 = Expression(None, 41, arg1=eComp2, arg2=self.eAddMod)
        eIfElse2 = Expression(None, 52, arg1=eIfThen2, arg2=eStub)
        eSplicedIfs = Expression(None, 17, arg1=eIfElse1, arg2=eIfElse2)

        infos, status = InfoBuilder().build(eSplicedIfs, self.eRmMod, 0)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        self.assertIsNotNone(info.conditions, msg="info conditions must be not None")

        # Conditions of similar modifiers are combined using logical or
        currentAtom = info.conditions
        expAtomType = AtomType.logic
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be logic (ID {})".format(expAtomType))
        expAtomOptr = AtomLogicOperator.or_
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be logical or (ID {})".format(expAtomOptr))

        currentAtom = info.conditions.child1
        expAtomType = AtomType.comparison
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))

        currentAtom = info.conditions.child2
        expAtomType = AtomType.comparison
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))
