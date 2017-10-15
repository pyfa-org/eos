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
from unittest.mock import patch

from tests.eve_obj_builder.eve_obj_builder_testcase import EveObjBuilderTestCase


class TestConversionEffect(EveObjBuilderTestCase):
    """Data should be saved into appropriate fields of an effect."""

    @patch('eos.data.eve_obj_builder.converter.ModifierBuilder')
    def test_fields(self, mod_builder):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 112})
        self.dh.data['dgmeffects'].append({
            'postExpression': 11, 'effectID': 112, 'isOffensive': True,
            'falloffAttributeID': 3, 'rangeAttributeID': 2,
            'fittingUsageChanceAttributeID': 96, 'preExpression': 1,
            'durationAttributeID': 781, 'randomField': 666,
            'dischargeAttributeID': 72, 'isAssistance': False,
            'effectCategory': 111, 'trackingSpeedAttributeID': 6,
            'modifierInfo': None})
        mod = self.mod(
            tgt_filter=3, tgt_domain=4, tgt_filter_extra_arg=5, tgt_attr=6,
            operator=7, src_attr=8)
        mod_builder.return_value.build.return_value = ([mod], 29)
        self.run_builder()
        self.assertEqual(len(self.log), 2)
        idzing_stats = self.log[0]
        self.assertEqual(
            idzing_stats.name, 'eos.data.eve_obj_builder.normalizer')
        self.assertEqual(idzing_stats.levelno, logging.WARNING)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.eve_obj_builder.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(len(self.effects), 1)
        self.assertIn(112, self.effects)
        effect = self.effects[112]
        self.assertEqual(effect.id, 112)
        self.assertEqual(effect.category, 111)
        self.assertIs(effect.is_offensive, True)
        self.assertIs(effect.is_assistance, False)
        self.assertEqual(effect.duration_attribute, 781)
        self.assertEqual(effect.discharge_attribute, 72)
        self.assertEqual(effect.range_attribute, 2)
        self.assertEqual(effect.falloff_attribute, 3)
        self.assertEqual(effect.tracking_speed_attribute, 6)
        self.assertEqual(effect.fitting_usage_chance_attribute, 96)
        self.assertEqual(effect.build_status, 29)
        self.assertIn(mod, effect.modifiers)
