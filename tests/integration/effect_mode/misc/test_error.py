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


import logging

from eos import ModuleHigh
from eos import State
from eos.const.eve import EffectCategoryId
from tests.integration.effect_mode.testcase import EffectModeTestCase


class TestEffectModeErrors(EffectModeTestCase):

    def test_unknown_mode(self):
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[self.modifier])
        item = ModuleHigh(
            self.mktype(
                attrs={self.tgt_attr.id: 10, self.src_attr.id: 2},
                effects=[effect]).id,
            state=State.offline)
        self.fit.modules.high.append(item)
        # Action
        item.set_effect_mode(effect.id, 9999)
        # Verification
        self.assertAlmostEqual(item.attrs[self.tgt_attr.id], 10)
        log = self.get_log()
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(log_record.name, 'eos.effect_status')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(log_record.msg, 'unknown effect mode 9999')
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
