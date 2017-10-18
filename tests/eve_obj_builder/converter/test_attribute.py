# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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


from tests.eve_obj_builder.eve_obj_builder_testcase import EveObjBuilderTestCase


class TestConversionAttribute(EveObjBuilderTestCase):
    """Data should be saved into appropriate fields of an attribute."""

    logger_name = 'eos.data.eve_obj_builder.converter'

    def test_fields(self):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeattribs'].append(
            {'typeID': 1, 'attributeID': 111, 'value': 8.2})
        self.dh.data['dgmattribs'].append({
            'maxAttributeID': 84, 'randomField': None, 'stackable': True,
            'defaultValue': 0.0, 'attributeID': 111, 'highIsGood': False})
        self.run_builder()
        log = self.get_log(name=self.logger_name)
        self.assertEqual(len(log), 0)
        self.assertEqual(len(self.attributes), 1)
        self.assertIn(111, self.attributes)
        attribute = self.attributes[111]
        self.assertEqual(attribute.id, 111)
        self.assertEqual(attribute.max_attribute, 84)
        self.assertEqual(attribute.default_value, 0.0)
        self.assertIs(attribute.high_is_good, False)
        self.assertIs(attribute.stackable, True)
