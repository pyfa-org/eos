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


import logging

from tests.eve_obj_builder.eve_obj_builder_testcase import EveObjBuilderTestCase


class TestDefaultEffects(EveObjBuilderTestCase):
    """Check that each item can have has max 1 default effect."""

    def setUp(self):
        super().setUp()
        self.eve_type = {'typeID': 1, 'groupID': 1}
        self.dh.data['evetypes'].append(self.eve_type)
        self.eff_link1 = {'typeID': 1, 'effectID': 1}
        self.eff_link2 = {'typeID': 1, 'effectID': 2}
        self.dh.data['dgmtypeeffects'].append(self.eff_link1)
        self.dh.data['dgmtypeeffects'].append(self.eff_link2)
        self.dh.data['dgmeffects'].append(
            {'effectID': 1, 'falloffAttributeID': 10})
        self.dh.data['dgmeffects'].append(
            {'effectID': 2, 'falloffAttributeID': 20})

    def test_normal(self):
        self.eff_link1['isDefault'] = False
        self.eff_link2['isDefault'] = True
        self.run_builder()
        self.assertEqual(len(self.log), 2)
        idzing_stats = self.log[0]
        self.assertEqual(
            idzing_stats.name, 'eos.data.eve_obj_builder.normalizer')
        self.assertEqual(idzing_stats.levelno, logging.WARNING)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.eve_obj_builder.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertIn(1, self.types)
        self.assertEqual(len(self.effects), 2)
        self.assertIn(2, self.effects)
        self.assertEqual(self.effects[2].falloff_attribute, 20)

    def test_duplicate(self):
        self.eff_link1['isDefault'] = True
        self.eff_link2['isDefault'] = True
        self.run_builder()
        self.assertEqual(len(self.log), 3)
        idzing_stats = self.log[0]
        self.assertEqual(
            idzing_stats.name, 'eos.data.eve_obj_builder.normalizer')
        self.assertEqual(idzing_stats.levelno, logging.WARNING)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.eve_obj_builder.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        log_record = self.log[2]
        self.assertEqual(
            log_record.name, 'eos.data.eve_obj_builder.validator_preconv')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(
            log_record.msg,
            'data contains 1 excessive default effects, '
            'marking them as non-default'
        )
        self.assertEqual(len(self.types), 1)
        self.assertIn(1, self.types)
        # Make sure effects are not removed
        self.assertEqual(len(self.effects), 2)
        self.assertIn(1, self.effects)
        self.assertIn(2, self.effects)
        self.assertEqual(self.effects[1].falloff_attribute, 10)

    def test_cleanup(self):
        del self.eve_type['groupID']
        self.eff_link1['isDefault'] = True
        self.eff_link2['isDefault'] = True
        self.run_builder()
        self.assertEqual(len(self.log), 2)
        idzing_stats = self.log[0]
        self.assertEqual(
            idzing_stats.name, 'eos.data.eve_obj_builder.normalizer')
        self.assertEqual(idzing_stats.levelno, logging.WARNING)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.eve_obj_builder.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(len(self.types), 0)
        self.assertEqual(len(self.effects), 0)
