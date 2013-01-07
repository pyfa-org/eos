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


from eos.tests.cacheUpdater.updaterTestCase import UpdaterTestCase


class TestAssociatedData(UpdaterTestCase):
    """
    Check that types, which passed filter, pull in
    all related data.
    """

    def testStrong(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 5})
        self.dh.data['invgroups'].append({'groupID': 5, 'categoryID': 16, 'fittableNonSingleton': True})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 5, 'value': 10.0})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 100, 'isDefault': True})
        self.dh.data['dgmeffects'].append({'effectID': 100, 'effectCategory': 8, 'isOffensive': True, 'isAssistance': False,
                                           'fittingUsageChanceAttributeID': 1000, 'preExpression': 100, 'postExpression': 101,
                                           'durationAttributeID': 1001, 'dischargeAttributeID': 1002, 'rangeAttributeID': 1003,
                                           'falloffAttributeID': 1004, 'trackingSpeedAttributeID': 1005})
        self.dh.data['dgmattribs'].append({'attributeID': 5, 'maxAttributeID': 1006, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': True})
        self.dh.data['dgmattribs'].append({'attributeID': 1000, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmattribs'].append({'attributeID': 1001, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmattribs'].append({'attributeID': 1002, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmattribs'].append({'attributeID': 1003, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmattribs'].append({'attributeID': 1004, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmattribs'].append({'attributeID': 1005, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmattribs'].append({'attributeID': 1006, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmexpressions'].append({'expressionID': 100, 'operandID': 6, 'arg1': 102, 'arg2': 103,
                                               'expressionValue': None, 'expressionTypeID': 2,
                                               'expressionGroupID': 500, 'expressionAttributeID': 1007})
        self.dh.data['dgmexpressions'].append({'expressionID': 101, 'operandID': 6, 'arg1': 102, 'arg2': 103,
                                               'expressionValue': None, 'expressionTypeID': None,
                                               'expressionGroupID': None, 'expressionAttributeID': None})
        self.dh.data['dgmexpressions'].append({'expressionID': 102, 'operandID': 6, 'arg1': None, 'arg2': None,
                                               'expressionValue': None, 'expressionTypeID': None,
                                               'expressionGroupID': None, 'expressionAttributeID': None})
        self.dh.data['dgmexpressions'].append({'expressionID': 103, 'operandID': 6, 'arg1': None, 'arg2': None,
                                               'expressionValue': None, 'expressionTypeID': None,
                                               'expressionGroupID': None, 'expressionAttributeID': None})
        # Weak type, but linked through expression
        self.dh.data['invtypes'].append({'typeID': 2, 'groupID': 6})
        self.dh.data['invgroups'].append({'groupID': 6, 'categoryID': 50, 'fittableNonSingleton': True})
        self.dh.data['dgmattribs'].append({'attributeID': 1007, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 0)
        self.assertEqual(len(data['types']), 2)
        self.assertIn(1, data['types'])
        self.assertIn(2, data['types'])
        self.assertEqual(len(data['attributes']), 9)
        self.assertIn(5, data['attributes'])
        self.assertIn(1000, data['attributes'])
        self.assertIn(1001, data['attributes'])
        self.assertIn(1002, data['attributes'])
        self.assertIn(1003, data['attributes'])
        self.assertIn(1004, data['attributes'])
        self.assertIn(1005, data['attributes'])
        self.assertIn(1006, data['attributes'])
        self.assertIn(1007, data['attributes'])
        self.assertEqual(len(data['effects']), 1)
        self.assertIn(100, data['effects'])
        self.assertEqual(len(data['expressions']), 4)
        self.assertIn(100, data['expressions'])
        self.assertIn(101, data['expressions'])
        self.assertIn(102, data['expressions'])
        self.assertIn(103, data['expressions'])

    def testWeak(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 5})
        self.dh.data['invgroups'].append({'groupID': 5, 'categoryID': 101, 'fittableNonSingleton': True})
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 5, 'value': 10.0})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 100, 'isDefault': True})
        self.dh.data['dgmeffects'].append({'effectID': 100, 'effectCategory': 8, 'isOffensive': True, 'isAssistance': False,
                                           'fittingUsageChanceAttributeID': 1000, 'preExpression': 100, 'postExpression': 101,
                                           'durationAttributeID': 1001, 'dischargeAttributeID': 1002, 'rangeAttributeID': 1003,
                                           'falloffAttributeID': 1004, 'trackingSpeedAttributeID': 1005})
        self.dh.data['dgmattribs'].append({'attributeID': 5, 'maxAttributeID': 1006, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': True})
        self.dh.data['dgmattribs'].append({'attributeID': 1000, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmattribs'].append({'attributeID': 1001, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmattribs'].append({'attributeID': 1002, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmattribs'].append({'attributeID': 1003, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmattribs'].append({'attributeID': 1004, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmattribs'].append({'attributeID': 1005, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmattribs'].append({'attributeID': 1006, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmexpressions'].append({'expressionID': 100, 'operandID': 6, 'arg1': 102, 'arg2': 103,
                                               'expressionValue': None, 'expressionTypeID': 2,
                                               'expressionGroupID': 500, 'expressionAttributeID': 1007})
        self.dh.data['dgmexpressions'].append({'expressionID': 101, 'operandID': 6, 'arg1': 102, 'arg2': 103,
                                               'expressionValue': None, 'expressionTypeID': None,
                                               'expressionGroupID': None, 'expressionAttributeID': None})
        self.dh.data['dgmexpressions'].append({'expressionID': 102, 'operandID': 6, 'arg1': None, 'arg2': None,
                                               'expressionValue': None, 'expressionTypeID': None,
                                               'expressionGroupID': None, 'expressionAttributeID': None})
        self.dh.data['dgmexpressions'].append({'expressionID': 103, 'operandID': 6, 'arg1': None, 'arg2': None,
                                               'expressionValue': None, 'expressionTypeID': None,
                                               'expressionGroupID': None, 'expressionAttributeID': None})
        self.dh.data['invtypes'].append({'typeID': 2, 'groupID': 6})
        self.dh.data['invgroups'].append({'groupID': 6, 'categoryID': 50, 'fittableNonSingleton': True})
        self.dh.data['dgmattribs'].append({'attributeID': 1007, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 0)
        self.assertEqual(len(data['types']), 0)
        self.assertEqual(len(data['attributes']), 0)
        self.assertEqual(len(data['effects']), 0)
        self.assertEqual(len(data['expressions']), 0)

    def testUnlinked(self):
        self.dh.data['dgmtypeattribs'].append({'typeID': 1, 'attributeID': 5, 'value': 10.0})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 100, 'isDefault': True})
        self.dh.data['dgmeffects'].append({'effectID': 100, 'effectCategory': 8, 'isOffensive': True, 'isAssistance': False,
                                           'fittingUsageChanceAttributeID': 1000, 'preExpression': 100, 'postExpression': 101,
                                           'durationAttributeID': 1001, 'dischargeAttributeID': 1002, 'rangeAttributeID': 1003,
                                           'falloffAttributeID': 1004, 'trackingSpeedAttributeID': 1005})
        self.dh.data['dgmattribs'].append({'attributeID': 5, 'maxAttributeID': 1006, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': True})
        self.dh.data['dgmattribs'].append({'attributeID': 1000, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmattribs'].append({'attributeID': 1001, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmattribs'].append({'attributeID': 1002, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmattribs'].append({'attributeID': 1003, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmattribs'].append({'attributeID': 1004, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmattribs'].append({'attributeID': 1005, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmattribs'].append({'attributeID': 1006, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        self.dh.data['dgmexpressions'].append({'expressionID': 100, 'operandID': 6, 'arg1': 102, 'arg2': 103,
                                               'expressionValue': None, 'expressionTypeID': 2,
                                               'expressionGroupID': 500, 'expressionAttributeID': 1007})
        self.dh.data['dgmexpressions'].append({'expressionID': 101, 'operandID': 6, 'arg1': 102, 'arg2': 103,
                                               'expressionValue': None, 'expressionTypeID': None,
                                               'expressionGroupID': None, 'expressionAttributeID': None})
        self.dh.data['dgmexpressions'].append({'expressionID': 102, 'operandID': 6, 'arg1': None, 'arg2': None,
                                               'expressionValue': None, 'expressionTypeID': None,
                                               'expressionGroupID': None, 'expressionAttributeID': None})
        self.dh.data['dgmexpressions'].append({'expressionID': 103, 'operandID': 6, 'arg1': None, 'arg2': None,
                                               'expressionValue': None, 'expressionTypeID': None,
                                               'expressionGroupID': None, 'expressionAttributeID': None})
        self.dh.data['invtypes'].append({'typeID': 2, 'groupID': 6})
        self.dh.data['invgroups'].append({'groupID': 6, 'categoryID': 50, 'fittableNonSingleton': True})
        self.dh.data['dgmattribs'].append({'attributeID': 1007, 'maxAttributeID': None, 'defaultValue': 0.0,
                                           'highIsGood': False, 'stackable': False})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 0)
        self.assertEqual(len(data['types']), 0)
        self.assertEqual(len(data['attributes']), 0)
        self.assertEqual(len(data['effects']), 0)
        self.assertEqual(len(data['expressions']), 0)

    def testReverseTypes(self):
        # Check that single type included into table does not
        # pull other types belonging to same group
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 5})
        self.dh.data['invgroups'].append({'groupID': 5, 'categoryID': 16, 'fittableNonSingleton': True})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 100, 'isDefault': True})
        self.dh.data['dgmeffects'].append({'effectID': 100, 'effectCategory': 8, 'isOffensive': True, 'isAssistance': False,
                                           'fittingUsageChanceAttributeID': None, 'preExpression': 101, 'postExpression': None,
                                           'durationAttributeID': None, 'dischargeAttributeID': None, 'rangeAttributeID': None,
                                           'falloffAttributeID': None, 'trackingSpeedAttributeID': None})
        self.dh.data['dgmexpressions'].append({'expressionID': 101, 'operandID': 6, 'arg1': None, 'arg2': None,
                                               'expressionValue': None, 'expressionTypeID': 2,
                                               'expressionGroupID': None, 'expressionAttributeID': None})
        # Weak type, but linked through expression
        self.dh.data['invtypes'].append({'typeID': 2, 'groupID': 6})
        self.dh.data['invtypes'].append({'typeID': 3, 'groupID': 6})
        self.dh.data['invgroups'].append({'groupID': 6, 'categoryID': 50, 'fittableNonSingleton': True})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 0)
        self.assertEqual(len(data['types']), 2)
        self.assertIn(1, data['types'])
        self.assertIn(2, data['types'])
        self.assertEqual(len(data['attributes']), 0)
        self.assertEqual(len(data['effects']), 1)
        self.assertIn(100, data['effects'])
        self.assertEqual(len(data['expressions']), 1)
        self.assertIn(101, data['expressions'])
