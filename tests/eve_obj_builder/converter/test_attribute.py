# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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
# ==============================================================================


from tests.eve_obj_builder.testcase import EveObjBuilderTestCase


class TestConversionAttribute(EveObjBuilderTestCase):
    """Data should be saved into appropriate fields of an attribute."""

    logger_name = 'eos.eve_obj_builder.converter'

    def test_fields(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeattribs'].append(
            {'typeID': 1, 'attributeID': 111, 'value': 8.2})
        self.dh.data['dgmattribs'].append({
            'maxAttributeID': 84, 'randomField': None, 'stackable': True,
            'defaultValue': 0.0, 'attributeID': 111, 'highIsGood': False})
        self.run_builder()
        self.assertEqual(len(self.attrs), 1)
        self.assertIn(111, self.attrs)
        attr = self.attrs[111]
        self.assertEqual(attr.id, 111)
        self.assertEqual(attr.max_attr_id, 84)
        self.assertEqual(attr.default_value, 0.0)
        self.assertIs(attr.high_is_good, False)
        self.assertIs(attr.stackable, True)
        self.assertEqual(len(self.get_log(name=self.logger_name)), 0)
