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


from eos import EffectMode
from eos import ModuleHigh
from eos import State
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.effect_mode.testcase import EffectModeTestCase


class TestModeSetting(EffectModeTestCase):

    def test_single_item_not_loaded(self):
        effect_id = self.allocate_effect_id()
        item = ModuleHigh(self.allocate_type_id())
        self.fit.modules.high.append(item)
        # Verification
        item.set_effect_mode(effect_id, EffectMode.force_stop)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_multi(self):
        src_attr_fullcomp = self.mkattr()
        tgt_attr_fullcomp = self.mkattr()
        modifier_fullcomp = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr_fullcomp.id,
            operator=ModOperator.mod_add,
            src_attr_id=src_attr_fullcomp.id)
        effect_fullcomp = self.mkeffect(
            category_id=EffectCategoryId.active,
            modifiers=[modifier_fullcomp])
        src_attr_statecomp = self.mkattr()
        tgt_attr_statecomp = self.mkattr()
        modifier_statecomp = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr_statecomp.id,
            operator=ModOperator.mod_add,
            src_attr_id=src_attr_statecomp.id)
        effect_statecomp = self.mkeffect(
            category_id=EffectCategoryId.active,
            modifiers=[modifier_statecomp])
        src_attr_forcerun = self.mkattr()
        tgt_attr_forcerun = self.mkattr()
        modifier_forcerun = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr_forcerun.id,
            operator=ModOperator.mod_add,
            src_attr_id=src_attr_forcerun.id)
        effect_forcerun = self.mkeffect(
            category_id=EffectCategoryId.overload,
            modifiers=[modifier_forcerun])
        src_attr_forcestop = self.mkattr()
        tgt_attr_forcestop = self.mkattr()
        modifier_forcestop = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr_forcestop.id,
            operator=ModOperator.mod_add,
            src_attr_id=src_attr_forcestop.id)
        effect_forcestop = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_forcestop])
        item = ModuleHigh(
            self.mktype(
                attrs={
                    tgt_attr_fullcomp.id: 10, src_attr_fullcomp.id: 2,
                    tgt_attr_statecomp.id: 10, src_attr_statecomp.id: 2,
                    tgt_attr_forcerun.id: 10, src_attr_forcerun.id: 2,
                    tgt_attr_forcestop.id: 10, src_attr_forcestop.id: 2},
                effects=(
                    effect_fullcomp, effect_statecomp,
                    effect_forcerun, effect_forcestop)).id,
            state=State.active)
        self.fit.modules.high.append(item)
        self.assertAlmostEqual(item.attrs[tgt_attr_fullcomp.id], 10)
        self.assertAlmostEqual(item.attrs[tgt_attr_statecomp.id], 10)
        self.assertAlmostEqual(item.attrs[tgt_attr_forcerun.id], 10)
        self.assertAlmostEqual(item.attrs[tgt_attr_forcestop.id], 12)
        # Action
        item._set_effects_modes({
            effect_fullcomp.id: EffectMode.full_compliance,
            effect_statecomp.id: EffectMode.state_compliance,
            effect_forcerun.id: EffectMode.force_run,
            effect_forcestop.id: EffectMode.force_stop})
        # Verification
        self.assertAlmostEqual(item.attrs[tgt_attr_fullcomp.id], 10)
        self.assertAlmostEqual(item.attrs[tgt_attr_statecomp.id], 12)
        self.assertAlmostEqual(item.attrs[tgt_attr_forcerun.id], 12)
        self.assertAlmostEqual(item.attrs[tgt_attr_forcestop.id], 10)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_multi_item_not_loaded(self):
        effect1_id = self.allocate_effect_id()
        effect2_id = self.allocate_effect_id()
        effect3_id = self.allocate_effect_id()
        effect4_id = self.allocate_effect_id()
        item = ModuleHigh(self.allocate_type_id())
        self.fit.modules.high.append(item)
        # Verification
        item._set_effects_modes({
            effect1_id: EffectMode.full_compliance,
            effect2_id: EffectMode.state_compliance,
            effect3_id: EffectMode.force_run,
            effect4_id: EffectMode.force_stop})
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
