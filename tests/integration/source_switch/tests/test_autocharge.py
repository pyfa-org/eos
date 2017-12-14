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


from eos import ModuleHigh
from eos import Ship
from eos import State
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import AttrId
from eos.const.eve import EffectId
from eos.const.eve import EffectCategoryId
from tests.integration.source_switch.testcase import SourceSwitchTestCase


class TestSourceSwitchAutocharge(SourceSwitchTestCase):
    """Check that autocharge items are updated properly on source switch."""

    def setUp(self):
        SourceSwitchTestCase.setUp(self)
        self.autocharge_attr_id = AttrId.ammo_loaded

    def mkeffect_container_autocharge(self, src):
        """Make effect, which loads autocharge when assigned to container."""
        return self.mkeffect(
            src=src,
            effect_id=EffectId.tgt_attack,
            category_id=EffectCategoryId.target,
            customize=True)

    def mkmod_filter_item(self, src_attr_id, tgt_attr_id):
        return self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=tgt_attr_id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr_id)

    def test_autocharge_to_none_no_effect(self):
        # Attribute setup
        src_attr_id = self.allocate_attr_id('src1', 'src2')
        tgt_attr_id = self.allocate_attr_id('src1', 'src2')
        self.mkattr(src='src1', attr_id=src_attr_id)
        self.mkattr(src='src2', attr_id=src_attr_id)
        self.mkattr(src='src1', attr_id=tgt_attr_id)
        self.mkattr(src='src2', attr_id=tgt_attr_id)
        # Autocharge setup
        autocharge_modifier = self.mkmod_filter_item(src_attr_id, tgt_attr_id)
        autocharge_effect_id = self.allocate_effect_id('src1', 'src2')
        autocharge_effect_src1 = self.mkeffect(
            src='src1',
            effect_id=autocharge_effect_id,
            category_id=EffectCategoryId.passive,
            modifiers=[autocharge_modifier])
        autocharge_effect_src2 = self.mkeffect(
            src='src2',
            effect_id=autocharge_effect_id,
            category_id=EffectCategoryId.passive,
            modifiers=[autocharge_modifier])
        autocharge_type_id = self.allocate_type_id('src1', 'src2')
        self.mktype(
            src='src1',
            type_id=autocharge_type_id,
            attrs={src_attr_id: 50},
            effects=[autocharge_effect_src1])
        self.mktype(
            src='src2',
            type_id=autocharge_type_id,
            attrs={src_attr_id: 50},
            effects=[autocharge_effect_src2])
        # Container setup
        container_effect_src1 = self.mkeffect_container_autocharge('src1')
        # Just create it to 2nd source, we're not going to use it
        self.mkeffect_container_autocharge('src2')
        container_type_id = self.allocate_type_id('src1', 'src2')
        self.mktype(
            src='src1',
            type_id=container_type_id,
            attrs={self.autocharge_attr_id: autocharge_type_id},
            effects=[container_effect_src1])
        self.mktype(
            src='src2',
            type_id=container_type_id,
            attrs={self.autocharge_attr_id: autocharge_type_id})
        container = ModuleHigh(container_type_id, state=State.active)
        # Influence target setup
        influence_tgt_type_id = self.allocate_type_id('src1', 'src2')
        self.mktype(
            src='src1',
            type_id=influence_tgt_type_id,
            attrs={tgt_attr_id: 10})
        self.mktype(
            src='src2',
            type_id=influence_tgt_type_id,
            attrs={tgt_attr_id: 10})
        influence_tgt = Ship(influence_tgt_type_id)
        # Fit setup
        self.fit.ship = influence_tgt
        self.fit.modules.high.append(container)
        self.assertAlmostEqual(influence_tgt.attrs[tgt_attr_id], 15)
        # Action
        self.fit.source = 'src2'
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[tgt_attr_id], 10)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_no_effect_to_autocharge(self):
        # Attribute setup
        src_attr_id = self.allocate_attr_id('src1', 'src2')
        tgt_attr_id = self.allocate_attr_id('src1', 'src2')
        self.mkattr(src='src1', attr_id=src_attr_id)
        self.mkattr(src='src2', attr_id=src_attr_id)
        self.mkattr(src='src1', attr_id=tgt_attr_id)
        self.mkattr(src='src2', attr_id=tgt_attr_id)
        # Autocharge setup
        autocharge_modifier = self.mkmod_filter_item(src_attr_id, tgt_attr_id)
        autocharge_effect_id = self.allocate_effect_id('src1', 'src2')
        autocharge_effect_src1 = self.mkeffect(
            src='src1',
            effect_id=autocharge_effect_id,
            category_id=EffectCategoryId.passive,
            modifiers=[autocharge_modifier])
        autocharge_effect_src2 = self.mkeffect(
            src='src2',
            effect_id=autocharge_effect_id,
            category_id=EffectCategoryId.passive,
            modifiers=[autocharge_modifier])
        autocharge_type_id = self.allocate_type_id('src1', 'src2')
        self.mktype(
            src='src1',
            type_id=autocharge_type_id,
            attrs={src_attr_id: 50},
            effects=[autocharge_effect_src1])
        self.mktype(
            src='src2',
            type_id=autocharge_type_id,
            attrs={src_attr_id: 50},
            effects=[autocharge_effect_src2])
        # Container setup
        # Just create it to 2nd source, we're not going to use it
        self.mkeffect_container_autocharge('src1')
        container_effect_src2 = self.mkeffect_container_autocharge('src2')
        container_type_id = self.allocate_type_id('src1', 'src2')
        self.mktype(
            src='src1',
            type_id=container_type_id,
            attrs={self.autocharge_attr_id: autocharge_type_id})
        self.mktype(
            src='src2',
            type_id=container_type_id,
            attrs={self.autocharge_attr_id: autocharge_type_id},
            effects=[container_effect_src2])
        container = ModuleHigh(container_type_id, state=State.active)
        # Influence target setup
        influence_tgt_type_id = self.allocate_type_id('src1', 'src2')
        self.mktype(
            src='src1',
            type_id=influence_tgt_type_id,
            attrs={tgt_attr_id: 10})
        self.mktype(
            src='src2',
            type_id=influence_tgt_type_id,
            attrs={tgt_attr_id: 10})
        influence_tgt = Ship(influence_tgt_type_id)
        # Fit setup
        self.fit.ship = influence_tgt
        self.fit.modules.high.append(container)
        self.assertAlmostEqual(influence_tgt.attrs[tgt_attr_id], 10)
        # Action
        self.fit.source = 'src2'
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[tgt_attr_id], 15)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_autocharge_to_autocharge_changed_attrs(self):
        # Attribute setup
        src_attr_id = self.allocate_attr_id('src1', 'src2')
        tgt_attr_id = self.allocate_attr_id('src1', 'src2')
        self.mkattr(src='src1', attr_id=src_attr_id)
        self.mkattr(src='src2', attr_id=src_attr_id)
        self.mkattr(src='src1', attr_id=tgt_attr_id)
        self.mkattr(src='src2', attr_id=tgt_attr_id)
        # Autocharge setup
        autocharge_modifier = self.mkmod_filter_item(src_attr_id, tgt_attr_id)
        autocharge_effect_id = self.allocate_effect_id('src1', 'src2')
        autocharge_effect_src1 = self.mkeffect(
            src='src1',
            effect_id=autocharge_effect_id,
            category_id=EffectCategoryId.passive,
            modifiers=[autocharge_modifier])
        autocharge_effect_src2 = self.mkeffect(
            src='src2',
            effect_id=autocharge_effect_id,
            category_id=EffectCategoryId.passive,
            modifiers=[autocharge_modifier])
        autocharge_type_id = self.allocate_type_id('src1', 'src2')
        self.mktype(
            src='src1',
            type_id=autocharge_type_id,
            attrs={src_attr_id: 50},
            effects=[autocharge_effect_src1])
        self.mktype(
            src='src2',
            type_id=autocharge_type_id,
            attrs={src_attr_id: 5},
            effects=[autocharge_effect_src2])
        # Container setup
        container_effect_src1 = self.mkeffect_container_autocharge('src1')
        container_effect_src2 = self.mkeffect_container_autocharge('src2')
        container_type_id = self.allocate_type_id('src1', 'src2')
        self.mktype(
            src='src1',
            type_id=container_type_id,
            attrs={self.autocharge_attr_id: autocharge_type_id},
            effects=[container_effect_src1])
        self.mktype(
            src='src2',
            type_id=container_type_id,
            attrs={self.autocharge_attr_id: autocharge_type_id},
            effects=[container_effect_src2])
        container = ModuleHigh(container_type_id, state=State.active)
        # Influence target setup
        influence_tgt_type_id = self.allocate_type_id('src1', 'src2')
        self.mktype(
            src='src1',
            type_id=influence_tgt_type_id,
            attrs={tgt_attr_id: 10})
        self.mktype(
            src='src2',
            type_id=influence_tgt_type_id,
            attrs={tgt_attr_id: 200})
        influence_tgt = Ship(influence_tgt_type_id)
        # Fit setup
        self.fit.ship = influence_tgt
        self.fit.modules.high.append(container)
        self.assertAlmostEqual(influence_tgt.attrs[tgt_attr_id], 15)
        # Action
        self.fit.source = 'src2'
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[tgt_attr_id], 210)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_autocharge_to_autocharge_changed_type(self):
        # Attribute setup
        src_attr_id = self.allocate_attr_id('src1', 'src2')
        tgt_attr_id = self.allocate_attr_id('src1', 'src2')
        self.mkattr(src='src1', attr_id=src_attr_id)
        self.mkattr(src='src2', attr_id=src_attr_id)
        self.mkattr(src='src1', attr_id=tgt_attr_id)
        self.mkattr(src='src2', attr_id=tgt_attr_id)
        # Autocharge setup
        autocharge_modifier = self.mkmod_filter_item(src_attr_id, tgt_attr_id)
        autocharge_effect_id = self.allocate_effect_id('src1', 'src2')
        autocharge_effect_src1 = self.mkeffect(
            src='src1',
            effect_id=autocharge_effect_id,
            category_id=EffectCategoryId.passive,
            modifiers=[autocharge_modifier])
        autocharge_effect_src2 = self.mkeffect(
            src='src2',
            effect_id=autocharge_effect_id,
            category_id=EffectCategoryId.passive,
            modifiers=[autocharge_modifier])
        autocharge_type1_id = self.allocate_type_id('src1', 'src2')
        self.mktype(
            src='src1',
            type_id=autocharge_type1_id,
            attrs={src_attr_id: 50},
            effects=[autocharge_effect_src1])
        self.mktype(
            src='src2',
            type_id=autocharge_type1_id,
            attrs={src_attr_id: 100},
            effects=[autocharge_effect_src2])
        autocharge_type2_id = self.allocate_type_id('src1', 'src2')
        self.mktype(
            src='src1',
            type_id=autocharge_type2_id,
            attrs={src_attr_id: 50},
            effects=[autocharge_effect_src1])
        self.mktype(
            src='src2',
            type_id=autocharge_type2_id,
            attrs={src_attr_id: 100},
            effects=[autocharge_effect_src2])
        # Container setup
        container_effect_src1 = self.mkeffect_container_autocharge('src1')
        container_effect_src2 = self.mkeffect_container_autocharge('src2')
        container_type_id = self.allocate_type_id('src1', 'src2')
        self.mktype(
            src='src1',
            type_id=container_type_id,
            attrs={self.autocharge_attr_id: autocharge_type1_id},
            effects=[container_effect_src1])
        self.mktype(
            src='src2',
            type_id=container_type_id,
            attrs={self.autocharge_attr_id: autocharge_type2_id},
            effects=[container_effect_src2])
        container = ModuleHigh(container_type_id, state=State.active)
        # Influence target setup
        influence_tgt_type_id = self.allocate_type_id('src1', 'src2')
        self.mktype(
            src='src1',
            type_id=influence_tgt_type_id,
            attrs={tgt_attr_id: 10})
        self.mktype(
            src='src2',
            type_id=influence_tgt_type_id,
            attrs={tgt_attr_id: 10})
        influence_tgt = Ship(influence_tgt_type_id)
        # Fit setup
        self.fit.ship = influence_tgt
        self.fit.modules.high.append(container)
        self.assertAlmostEqual(influence_tgt.attrs[tgt_attr_id], 15)
        # Action
        self.fit.source = 'src2'
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[tgt_attr_id], 20)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
