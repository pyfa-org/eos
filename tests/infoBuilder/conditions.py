from unittest import TestCase

from eos import const
from eos.data.expression import Expression
from eos.data.effect.builder import InfoBuilder

class TestCondition(TestCase):
    """Test parsing of trees describing conditions"""

    def setUp(self):
        # Create some modifier which makes sense for builder, we'll use it instead
        # of stub to test conditions which are assigned to it
        eTgt = Expression(1, 24, value="Ship")
        eTgtAttr = Expression(2, 22, attributeId=15)
        eOptr = Expression(3, 21, value="ModAdd")
        eSrcAttr = Expression(4, 22, attributeId=30)
        eTgtSpec = Expression(5, 12, arg1=eTgt, arg2=eTgtAttr)
        eOptrTgt = Expression(6, 31, arg1=eOptr, arg2=eTgtSpec)
        self.eAddMod = Expression(7, 6, arg1=eOptrTgt, arg2=eSrcAttr)
        self.eRmMod = Expression(8, 58, arg1=eOptrTgt, arg2=eSrcAttr)

    def testLogic(self):
        # Make a tree so we can focus on logic testing
        eTgtShip = Expression(9, 24, value="Ship")
        eAttr = Expression(10, 22, attributeId=11)
        eVal1 = Expression(11, 27, value="0")
        eVal2 = Expression(12, 27, value="100")
        eVal3 = Expression(13, 27, value="-1")
        eTgtSpec = Expression(14, 35, arg1=eTgtShip, arg2=eAttr)
        eComp1 = Expression(15, 39, arg1=eTgtSpec, arg2=eVal1)
        eComp2 = Expression(16, 39, arg1=eVal2, arg2=eTgtSpec)
        eComp3 = Expression(17, 33, arg1=eTgtSpec, arg2=eVal3)
        eLogic1 = Expression(18, 10, arg1=eComp1, arg2=eComp2)
        eLogic2 = Expression(19, 52, arg1=eLogic1, arg2=eComp3)
        eIfThen = Expression(20, 41, arg1=eLogic2, arg2=self.eAddMod)
        eElseStub = Expression(21, 27, value="1")
        eIfElse = Expression(22, 52, arg1=eIfThen, arg2=eElseStub)

        infos, status = InfoBuilder().build(eIfElse, self.eRmMod)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        self.assertIsNotNone(info.conditions, msg="info conditions must be not None")

        currentAtom = info.conditions
        expAtomType = const.atomTypeLogic
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be logic (ID {})".format(expAtomType))
        expAtomOptr = const.atomLogicOr
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be logical or (ID {})".format(expAtomOptr))

        currentAtom = info.conditions.arg1
        expAtomType = const.atomTypeLogic
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be logic (ID {})".format(expAtomType))
        expAtomOptr = const.atomLogicAnd
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be logical and (ID {})".format(expAtomOptr))

        # Check logic atom children types
        currentAtom = info.conditions.arg2
        expAtomType = const.atomTypeComp
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))

        currentAtom = info.conditions.arg1.arg1
        expAtomType = const.atomTypeComp
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))

        currentAtom = info.conditions.arg1.arg2
        expAtomType = const.atomTypeComp
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))

    def testComparison(self):
        # Make tree so we can test basic comparison
        eTgtShip = Expression(9, 24, value="Ship")
        eAttr = Expression(10, 22, attributeId=11)
        eVal = Expression(11, 27, value="100")
        eTgtSpec = Expression(12, 35, arg1=eTgtShip, arg2=eAttr)
        eComparison = Expression(13, 39, arg1=eTgtSpec, arg2=eVal)
        eIfThen = Expression(16, 41, arg1=eComparison, arg2=self.eAddMod)
        eElseStub = Expression(17, 27, value="1")
        eIfElse = Expression(18, 52, arg1=eIfThen, arg2=eElseStub)

        infos, status = InfoBuilder().build(eIfElse, self.eRmMod)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        self.assertIsNotNone(info.conditions, msg="info conditions must be not None")

        currentAtom = info.conditions
        expAtomType = const.atomTypeComp
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))
        expAtomOptr = const.atomCompGreatEq
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be greater than or equal (ID {})".format(expAtomOptr))

        # Check children types
        currentAtom = info.conditions.arg1
        expAtomType = const.atomTypeValRef
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be value reference (ID {})".format(expAtomType))

        currentAtom = info.conditions.arg2
        expAtomType = const.atomTypeVal
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be value (ID {})".format(expAtomType))

    def testMath(self):
        # Create a tree so we can check math atoms and their child types
        eTgtShip = Expression(9, 24, value="Ship")
        eAttr1 = Expression(10, 22, attributeId=11)
        eAttr2 = Expression(11, 22, attributeId=49)
        eAttr3 = Expression(12, 22, attributeId=5)
        eVal = Expression(13, 27, value="53")
        eTgtSpec1 = Expression(14, 35, arg1=eTgtShip, arg2=eAttr1)
        eTgtSpec2 = Expression(15, 35, arg1=eTgtShip, arg2=eAttr2)
        eTgtSpec3 = Expression(16, 35, arg1=eTgtShip, arg2=eAttr3)
        eMath1 = Expression(17, 1, arg1=eTgtSpec1, arg2=eVal)
        eMath2 = Expression(18, 68, arg1=eMath1, arg2=eTgtSpec2)
        eComparison = Expression(19, 39, arg1=eMath2, arg2=eTgtSpec3)
        eIfThen = Expression(20, 41, arg1=eComparison, arg2=self.eAddMod)
        eElseStub = Expression(21, 27, value="1")
        eIfElse = Expression(22, 52, arg1=eIfThen, arg2=eElseStub)

        infos, status = InfoBuilder().build(eIfElse, self.eRmMod)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        self.assertIsNotNone(info.conditions, msg="info conditions must be not None")

        currentAtom = info.conditions
        expAtomType = const.atomTypeComp
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))

        currentAtom = info.conditions.arg1
        expAtomType = const.atomTypeMath
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be math (ID {})".format(expAtomType))
        expAtomOptr = const.atomMathSub
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be subtraction (ID {})".format(expAtomOptr))

        currentAtom = info.conditions.arg1.arg1
        expAtomType = const.atomTypeMath
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be math (ID {})".format(expAtomType))
        expAtomOptr = const.atomMathAdd
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be addition (ID {})".format(expAtomOptr))

        # Check math children types
        currentAtom = info.conditions.arg1.arg1.arg1
        expAtomType = const.atomTypeValRef
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be value reference (ID {})".format(expAtomType))

        currentAtom = info.conditions.arg1.arg1.arg2
        expAtomType = const.atomTypeVal
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be value (ID {})".format(expAtomType))

        currentAtom = info.conditions.arg1.arg2
        expAtomType = const.atomTypeValRef
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be value reference (ID {})".format(expAtomType))

        currentAtom = info.conditions.arg2
        expAtomType = const.atomTypeValRef
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be value reference (ID {})".format(expAtomType))

    def testTerminals(self):
        # Here we'll check value and attribute reference terminals
        eTgtSelf = Expression(9, 24, value="Self")
        eAttr = Expression(10, 22, attributeId=87)
        eVal = Expression(11, 27, value="-50")
        eTgtSpec = Expression(12, 35, arg1=eTgtSelf, arg2=eAttr)
        eComparison = Expression(13, 39, arg1=eTgtSpec, arg2=eVal)
        eIfThen = Expression(16, 41, arg1=eComparison, arg2=self.eAddMod)
        eElseStub = Expression(17, 27, value="1")
        eIfElse = Expression(18, 52, arg1=eIfThen, arg2=eElseStub)

        infos, status = InfoBuilder().build(eIfElse, self.eRmMod)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        self.assertIsNotNone(info.conditions, msg="info conditions must be not None")

        currentAtom = info.conditions
        expAtomType = const.atomTypeComp
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))

        currentAtom = info.conditions.arg1
        expAtomType = const.atomTypeValRef
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be value reference (ID {})".format(expAtomType))
        expAtomCarrier = const.locSelf
        self.assertEqual(currentAtom.carrier, expAtomCarrier, msg="atom carrier must be self (ID {})".format(expAtomCarrier))
        expAtomAttr = 87
        self.assertEqual(currentAtom.attribute, expAtomAttr, msg="atom attribute ID must be {}".format(expAtomAttr))

        currentAtom = info.conditions.arg2
        expAtomType = const.atomTypeVal
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be value (ID {})".format(expAtomType))
        expAtomValue = -50
        self.assertEqual(currentAtom.value, expAtomValue, msg="atom value must be {}".format(expAtomValue))

    def testNested(self):
        # Tree which has two if-then-else blocks
        eTgtShip = Expression(9, 24, value="Ship")
        eAttr1 = Expression(10, 22, attributeId=11)
        eAttr2 = Expression(11, 22, attributeId=76)
        eVal1 = Expression(12, 27, value="5")
        eVal2 = Expression(13, 27, value="25")
        eStub = Expression(14, 27, value="1")
        eTgtSpec1 = Expression(15, 35, arg1=eTgtShip, arg2=eAttr1)
        eTgtSpec2 = Expression(16, 35, arg1=eTgtShip, arg2=eAttr2)
        eComp1 = Expression(17, 33, arg1=eTgtSpec1, arg2=eVal1)
        eComp2 = Expression(18, 38, arg1=eTgtSpec2, arg2=eVal2)
        eIfThen1 = Expression(19, 41, arg1=eComp1, arg2=self.eAddMod)
        eIfElse1 = Expression(20, 52, arg1=eIfThen1, arg2=eStub)
        eSplicedCondStub = Expression(21, 17, arg1=eIfElse1, arg2=eStub)
        eIfThen2 = Expression(22, 41, arg1=eComp2, arg2=eSplicedCondStub)
        eIfElse2 = Expression(23, 52, arg1=eIfThen2, arg2=eStub)

        infos, status = InfoBuilder().build(eIfElse2, self.eRmMod)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        self.assertIsNotNone(info.conditions, msg="info conditions must be not None")

        # Nested ifs are joined using logical and
        currentAtom = info.conditions
        expAtomType = const.atomTypeLogic
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be logic (ID {})".format(expAtomType))
        expAtomOptr = const.atomLogicAnd
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be logical and (ID {})".format(expAtomOptr))

        # Check children types
        currentAtom = info.conditions.arg1
        expAtomType = const.atomTypeComp
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))

        currentAtom = info.conditions.arg2
        expAtomType = const.atomTypeComp
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))

    def testInversion(self):
        # Conditions are inverted by builder at build time, test it too
        eTgtShip = Expression(9, 24, value="Ship")
        eAttr1 = Expression(10, 22, attributeId=11)
        eAttr2 = Expression(11, 22, attributeId=76)
        eAttr3 = Expression(12, 22, attributeId=53)
        eVal1 = Expression(13, 27, value="5")
        eVal2 = Expression(14, 27, value="25")
        eVal3 = Expression(15, 27, value="125")
        eStub = Expression(16, 27, value="1")
        eTgtSpec1 = Expression(17, 35, arg1=eTgtShip, arg2=eAttr1)
        eTgtSpec2 = Expression(18, 35, arg1=eTgtShip, arg2=eAttr2)
        eTgtSpec3 = Expression(19, 35, arg1=eTgtShip, arg2=eAttr3)
        eComp1 = Expression(20, 33, arg1=eTgtSpec1, arg2=eVal1)
        eComp2 = Expression(21, 39, arg1=eTgtSpec2, arg2=eVal2)
        eComp3 = Expression(22, 38, arg1=eTgtSpec3, arg2=eVal3)
        eLogic = Expression(23, 10, arg1=eComp1, arg2=eComp2)
        eIfThen1 = Expression(24, 41, arg1=eLogic, arg2=eStub)
        eIfElse1 = Expression(25, 52, arg1=eIfThen1, arg2=self.eAddMod)
        eSplicedCondStub = Expression(26, 17, arg1=eIfElse1, arg2=eStub)
        eIfThen2 = Expression(27, 41, arg1=eComp3, arg2=eSplicedCondStub)
        eIfElse2 = Expression(28, 52, arg1=eIfThen2, arg2=eStub)

        infos, status = InfoBuilder().build(eIfElse2, self.eRmMod)
        expStatus = const.effectInfoOkFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        self.assertIsNotNone(info.conditions, msg="info conditions must be not None")

        # We have nested conditions, logical and generated by them
        # is not affected by inversion in this case
        currentAtom = info.conditions
        expAtomType = const.atomTypeLogic
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be logic (ID {})".format(expAtomType))
        expAtomOptr = const.atomLogicAnd
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be logical and (ID {})".format(expAtomOptr))

        # Affected: and -> or
        currentAtom = info.conditions.arg2
        expAtomType = const.atomTypeLogic
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be logic (ID {})".format(expAtomType))
        expAtomOptr = const.atomLogicOr
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be logical or (ID {})".format(expAtomOptr))

        # Affected: == -> !=
        currentAtom = info.conditions.arg2.arg1
        expAtomType = const.atomTypeComp
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))
        expAtomOptr = const.atomCompNotEq
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be not equal (ID {})".format(expAtomOptr))

        # Affected: >= -> <
        currentAtom = info.conditions.arg2.arg2
        expAtomType = const.atomTypeComp
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))
        expAtomOptr = const.atomCompLess
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be less (ID {})".format(expAtomOptr))

        # This atom is also upper than inversion, so shouldn't be affected
        currentAtom = info.conditions.arg1
        expAtomType = const.atomTypeComp
        self.assertEqual(currentAtom.type, expAtomType, msg="atom type must be comparison (ID {})".format(expAtomType))
        expAtomOptr = const.atomCompGreat
        self.assertEqual(currentAtom.operator, expAtomOptr, msg="atom operator must be greater than (ID {})".format(expAtomOptr))
