# ===============================================================================
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
# ===============================================================================


from eos.const.eos import State, ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import DogmaModifier, ModificationCalculationError
from eos.data.cache_object.modifier.python import BasePythonModifier
from eos.fit.messages import AttrValueChanged, AttrValueChangedOverride
from tests.calculator.calculator_testcase import CalculatorTestCase
from tests.calculator.environment import IndependentItem


class TestModifierPython(CalculatorTestCase):

    def setUp(self):
        super().setUp()
        self.attr1 = attr1 = self.ch.attribute(attribute_id=1)
        self.attr2 = attr2 = self.ch.attribute(attribute_id=2)
        self.attr3 = attr3 = self.ch.attribute(attribute_id=3)

        class TestPythonModifier(BasePythonModifier):

            def __init__(self):
                BasePythonModifier.__init__(
                    self, state=State.online, tgt_filter=ModifierTargetFilter.item,
                    tgt_domain=ModifierDomain.self, tgt_filter_extra_arg=None,
                    tgt_attr=attr1.id
                )

            def get_modification(self, carrier_item, fit):
                try:
                    carrier_attrs = carrier_item.attributes
                    ship_attrs = fit.ship.attributes
                except AttributeError as e:
                    raise ModificationCalculationError from e
                try:
                    carrier_mul = carrier_attrs[attr2.id]
                    ship_mul = ship_attrs[attr3.id]
                except KeyError as e:
                    raise ModificationCalculationError from e
                return ModifierOperator.post_mul, carrier_mul * ship_mul

            @property
            def revise_message_types(self):
                return {AttrValueChanged, AttrValueChangedOverride}

            def revise_modification(self, message, carrier_item, fit):
                item, attr = message
                if (
                    (item is carrier_item and attr == attr2.id) or
                    (item is fit.ship and attr == attr3.id)
                ):
                    return True
                return False

        python_effect = self.ch.effect(
            effect_id=1, category=EffectCategory.online, modifiers=(TestPythonModifier(),)
        )
        self.fit.ship = IndependentItem(self.ch.type(type_id=1, attributes={attr3.id: 3}))
        self.eve_type = self.ch.type(type_id=2, effects=(python_effect,), attributes={attr1.id: 100, attr2.id: 2})
        self.item = IndependentItem(self.eve_type)

    def test_enabling(self):
        item = self.item
        self.fit.items.add(item)
        self.assertAlmostEqual(item.attributes[self.attr1.id], 100)
        # Action
        item.state = State.online
        # Verification
        self.assertAlmostEqual(item.attributes[self.attr1.id], 600)
        # Misc
        self.fit.items.remove(item)
        self.fit.ship = None
        self.assert_calculator_buffers_empty(self.fit)

    def test_disabling(self):
        item = self.item
        self.fit.items.add(item)
        item.state = State.online
        self.assertAlmostEqual(item.attributes[self.attr1.id], 600)
        # Action
        item.state = State.offline
        # Verification
        self.assertAlmostEqual(item.attributes[self.attr1.id], 100)
        # Misc
        self.fit.items.remove(item)
        self.fit.ship = None
        self.assert_calculator_buffers_empty(self.fit)

    def test_target_recalc_attr_change(self):
        # Here dogma modifier changes value of one of attributes
        # which are used as source by python modifier, and sees if
        # python modifier target value is updated
        attr4 = self.ch.attribute(attribute_id=4)
        dogma_modifier = DogmaModifier(
            state=State.active,
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.attr2.id,
            operator=ModifierOperator.post_mul,
            src_attr=attr4.id
        )
        dogma_effect = self.ch.effect(effect_id=2, category=EffectCategory.active, modifiers=(dogma_modifier,))
        item = self.item
        self.eve_type.effects = (*self.eve_type.effects, dogma_effect)
        self.eve_type.attributes[attr4.id] = 5
        self.fit.items.add(item)
        item.state = State.online
        self.assertAlmostEqual(item.attributes[self.attr1.id], 600)
        # Action
        item.state = State.active
        # Verification
        self.assertAlmostEqual(item.attributes[self.attr1.id], 3000)
        # Misc
        self.fit.items.remove(item)
        self.fit.ship = None
        self.assert_calculator_buffers_empty(self.fit)

    def test_unsubscription(self):
        # Make sure that when python modifier unsubscribes
        # from message type needed by calculator, calculator
        # still receives that message type
        modifier1 = DogmaModifier(
            state=State.offline,
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.attr1.id,
            operator=ModifierOperator.post_mul,
            src_attr=self.attr2.id
        )
        effect1 = self.ch.effect(effect_id=2, category=EffectCategory.passive, modifiers=(modifier1,))
        modifier2 = DogmaModifier(
            state=State.online,
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.attr2.id,
            operator=ModifierOperator.post_mul,
            src_attr=self.attr3.id
        )
        effect2 = self.ch.effect(effect_id=3, category=EffectCategory.online, modifiers=(modifier2,))
        item1 = self.item
        item2 = IndependentItem(self.ch.type(
            type_id=3, effects=(effect1, effect2),
            attributes={self.attr1.id: 100, self.attr2.id: 2, self.attr3.id: 3}
        ))
        self.fit.items.add(item1)
        self.assertAlmostEqual(item1.attributes[self.attr1.id], 100)
        item1.state = State.online
        self.assertAlmostEqual(item1.attributes[self.attr1.id], 600)
        self.fit.items.remove(item1)  # Here modifier is unsubscribed from attr change events
        self.fit.items.add(item2)
        self.assertAlmostEqual(item2.attributes[self.attr1.id], 200)
        # Action
        item2.state = State.online
        # Verification
        # If value is updated, then calculator service received attribute
        # updated message
        self.assertAlmostEqual(item2.attributes[self.attr1.id], 600)
        # Misc
        self.fit.items.remove(item2)
        self.fit.ship = None
        self.assert_calculator_buffers_empty(self.fit)
