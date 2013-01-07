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


class TestConversionExpression(UpdaterTestCase):
    """
    Appropriate data should be saved into appropriate
    indexes of object representing expression.
    """

    def testFields(self):
        self.dh.data['invtypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 111})
        self.dh.data['dgmeffects'].append({'effectID': 111, 'preExpression': 24})
        self.dh.data['dgmexpressions'].append({'expressionTypeID': 502, 'expressionValue': None, 'randomField': 'vals',
                                               'operandID': 6, 'arg1': 1009, 'expressionID': 24, 'arg2': 15,
                                               'expressionAttributeID': 90, 'expressionGroupID': 451})
        data = self.updater.run(self.dh)
        self.assertEqual(len(self.log), 0)
        self.assertEqual(len(data['expressions']), 1)
        self.assertIn(24, data['expressions'])
        self.assertEqual(data['expressions'][24], (6, 1009, 15, None, 502, 451, 90))
