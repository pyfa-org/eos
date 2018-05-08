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


from eos import Ship
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import EffectCategoryId
from eos.eve_obj.modifier import BasePythonModifier
from eos.pubsub.message import AttrValueChanged
from tests.integration.calculator.testcase import CalculatorTestCase


class TestSimilarModifiersDogma(CalculatorTestCase):

    def make_modifier(self, src_attr_id, tgt_attr_id):

        class TestPythonModifier(BasePythonModifier):

            def __init__(self):
                BasePythonModifier.__init__(
                    self,
                    tgt_filter=ModTgtFilter.item,
                    tgt_domain=ModDomain.self,
                    tgt_filter_extra_arg=None,
                    tgt_attr_id=tgt_attr_id)

            def get_modification(self, mod_item):
                value = mod_item.attrs[src_attr_id]
                return ModOperator.post_percent, value

            @property
            def revise_msg_types(self):
                return {AttrValueChanged}

            def revise_modification(self, msg, mod_item):
                if msg.item is mod_item and msg.attr_id == src_attr_id:
                    return True
                return False

        return TestPythonModifier()

    def test_same_item(self):
        tgt_attr = self.mkattr()
        src_attr1 = self.mkattr()
        src_attr2 = self.mkattr()
        modifier1 = self.make_modifier(src_attr1.id, tgt_attr.id)
        modifier2 = self.make_modifier(src_attr2.id, tgt_attr.id)
        effect1 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier1])
        effect2 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier2])
        item = Ship(self.mktype(
            attrs={src_attr1.id: 20, src_attr2.id: 20, tgt_attr.id: 100},
            effects=(effect1, effect2)).id)
        # Action
        self.fit.ship = item
        # Verification
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 144)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_same_item_attr(self):
        # Setup
        tgt_attr = self.mkattr()
        src_attr = self.mkattr()
        modifier1 = self.make_modifier(src_attr.id, tgt_attr.id)
        modifier2 = self.make_modifier(src_attr.id, tgt_attr.id)
        effect1 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier1])
        effect2 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier2])
        item = Ship(self.mktype(
            attrs={src_attr.id: 20, tgt_attr.id: 100},
            effects=(effect1, effect2)).id)
        # Action
        self.fit.ship = item
        # Verification
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 144)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_same_item_effect(self):
        # Setup
        tgt_attr = self.mkattr()
        src_attr1 = self.mkattr()
        src_attr2 = self.mkattr()
        modifier1 = self.make_modifier(src_attr1.id, tgt_attr.id)
        modifier2 = self.make_modifier(src_attr2.id, tgt_attr.id)
        effect1 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier1, modifier2])
        item = Ship(self.mktype(
            attrs={src_attr1.id: 20, src_attr2.id: 20, tgt_attr.id: 100},
            effects=[effect1]).id)
        # Action
        self.fit.ship = item
        # Verification
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 144)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_same_item_effect_attr(self):
        # Setup
        tgt_attr = self.mkattr()
        src_attr = self.mkattr()
        modifier1 = self.make_modifier(src_attr.id, tgt_attr.id)
        modifier2 = self.make_modifier(src_attr.id, tgt_attr.id)
        effect1 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier1, modifier2])
        item = Ship(self.mktype(
            attrs={src_attr.id: 20, tgt_attr.id: 100},
            effects=[effect1]).id)
        # Action
        self.fit.ship = item
        # Verification
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 144)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)
