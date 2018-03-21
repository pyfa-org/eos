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
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from eos.eve_object.modifier import BasePythonModifier
from eos.eve_object.modifier import ModificationCalculationError
from eos.fit.message import AttrValueChanged
from tests.integration.calculator.testcase import CalculatorTestCase


class TestModifierPython(CalculatorTestCase):

    def setUp(self):
        CalculatorTestCase.setUp(self)
        self.attr1 = attr1 = self.mkattr()
        self.attr2 = attr2 = self.mkattr()
        self.attr3 = attr3 = self.mkattr()

        class TestPythonModifier(BasePythonModifier):

            def __init__(self):
                BasePythonModifier.__init__(
                    self,
                    tgt_filter=ModTgtFilter.item,
                    tgt_domain=ModDomain.self,
                    tgt_filter_extra_arg=None,
                    tgt_attr_id=attr1.id)

            def get_modification(self, carrier_item):
                ship = carrier_item._fit.ship
                try:
                    carrier_mul = carrier_item.attrs[attr2.id]
                    ship_mul = ship.attrs[attr3.id]
                except (AttributeError, KeyError) as e:
                    raise ModificationCalculationError from e
                return ModOperator.post_mul, carrier_mul * ship_mul

            @property
            def revise_msg_types(self):
                return {AttrValueChanged}

            def revise_modification(self, msg, carrier_item):
                ship = carrier_item._fit.ship
                if msg.item is carrier_item and msg.attr_id == attr2.id:
                    return True
                if msg.item is ship and msg.attr_id == attr3.id:
                    return True
                return False

        self.python_effect = self.mkeffect(
            category_id=EffectCategoryId.online,
            modifiers=(TestPythonModifier(),))
        self.online_effect = self.mkeffect(
            effect_id=EffectId.online,
            category_id=EffectCategoryId.online)
        self.fit.ship = Ship(self.mktype(attrs={attr3.id: 3}).id)

    def test_enabling(self):
        item = ModuleHigh(self.mktype(
            attrs={self.attr1.id: 100, self.attr2.id: 2},
            effects=(self.python_effect, self.online_effect)).id)
        self.fit.modules.high.append(item)
        self.assertAlmostEqual(item.attrs[self.attr1.id], 100)
        # Action
        item.state = State.online
        # Verification
        self.assertAlmostEqual(item.attrs[self.attr1.id], 600)
        # Cleanup
        self.fit.ship = None
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_disabling(self):
        item = ModuleHigh(self.mktype(
            attrs={self.attr1.id: 100, self.attr2.id: 2},
            effects=(self.python_effect, self.online_effect)).id)
        self.fit.modules.high.append(item)
        item.state = State.online
        self.assertAlmostEqual(item.attrs[self.attr1.id], 600)
        # Action
        item.state = State.offline
        # Verification
        self.assertAlmostEqual(item.attrs[self.attr1.id], 100)
        # Cleanup
        self.fit.ship = None
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_tgt_recalc_attr_change(self):
        # Here dogma modifier changes value of one of attributes which are used
        # as source by python modifier, and sees if python modifier target value
        # is updated
        attr4 = self.mkattr()
        dogma_modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=self.attr2.id,
            operator=ModOperator.post_mul,
            src_attr_id=attr4.id)
        dogma_effect = self.mkeffect(
            category_id=EffectCategoryId.active, modifiers=[dogma_modifier])
        item = ModuleHigh(self.mktype(
            attrs={self.attr1.id: 100, self.attr2.id: 2, attr4.id: 5},
            effects=(self.python_effect, self.online_effect, dogma_effect),
            default_effect=dogma_effect).id)
        self.fit.modules.high.append(item)
        item.state = State.online
        self.assertAlmostEqual(item.attrs[self.attr1.id], 600)
        # Action
        item.state = State.active
        # Verification
        self.assertAlmostEqual(item.attrs[self.attr1.id], 3000)
        # Cleanup
        self.fit.ship = None
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_unsubscription(self):
        # Make sure that when python modifier unsubscribes from message type
        # needed by calculator, calculator still receives that message type
        dogma_modifier1 = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=self.attr1.id,
            operator=ModOperator.post_mul,
            src_attr_id=self.attr2.id)
        dogma_effect1 = self.mkeffect(
            category_id=EffectCategoryId.passive, modifiers=[dogma_modifier1])
        dogma_modifier2 = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=self.attr2.id,
            operator=ModOperator.post_mul,
            src_attr_id=self.attr3.id)
        dogma_effect2 = self.mkeffect(
            category_id=EffectCategoryId.online, modifiers=[dogma_modifier2])
        python_item = ModuleHigh(self.mktype(
            attrs={self.attr1.id: 100, self.attr2.id: 2},
            effects=(self.python_effect, self.online_effect)).id)
        dogma_item = ModuleHigh(self.mktype(
            attrs={self.attr1.id: 100, self.attr2.id: 2, self.attr3.id: 3},
            effects=(dogma_effect1, dogma_effect2, self.online_effect)).id)
        self.fit.modules.high.append(python_item)
        self.assertAlmostEqual(python_item.attrs[self.attr1.id], 100)
        python_item.state = State.online
        self.assertAlmostEqual(python_item.attrs[self.attr1.id], 600)
        # Here modifier is unsubscribed from attribute change events
        self.fit.modules.high.remove(python_item)
        self.fit.modules.high.append(dogma_item)
        self.assertAlmostEqual(dogma_item.attrs[self.attr1.id], 200)
        # Action
        dogma_item.state = State.online
        # Verification
        # If value is updated, then calculator service received attribute
        # updated message
        self.assertAlmostEqual(dogma_item.attrs[self.attr1.id], 600)
        # Cleanup
        self.fit.ship = None
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
