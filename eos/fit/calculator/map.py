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


from collections import namedtuple
from itertools import chain
from logging import getLogger
from math import exp

from eos.const.eos import ModifierOperator
from eos.const.eve import Attribute, Category
from eos.data.cache_handler.exception import AttributeFetchError
from eos.fit.pubsub.message import (
    InstrAttrValueChanged, InstrAttrValueChangedMasked)
from eos.util.keyed_storage import KeyedStorage
from .exception import AttributeMetaError, BaseValueError


OverrideData = namedtuple('OverrideData', ('value', 'persistent'))


logger = getLogger(__name__)


# Stacking penalty base constant, used in attribute calculations
PENALTY_BASE = 1 / exp((1 / 2.67) ** 2)

# Items belonging to these categories never have their effects stacking
# penalized
PENALTY_IMMUNE_CATS = (
    Category.ship,
    Category.charge,
    Category.skill,
    Category.implant,
    Category.subsystem)

# Tuple with penalizable operators
PENALIZABLE_OPERATORS = (
    ModifierOperator.pre_mul,
    ModifierOperator.post_mul,
    ModifierOperator.post_percent,
    ModifierOperator.pre_div,
    ModifierOperator.post_div)

# Map which helps to normalize modifications
NORMALIZATION_MAP = {
    ModifierOperator.pre_assign: lambda val: val,
    ModifierOperator.pre_mul: lambda val: val,
    ModifierOperator.pre_div: lambda val: 1 / val,
    ModifierOperator.mod_add: lambda val: val,
    ModifierOperator.mod_sub: lambda val: -val,
    ModifierOperator.post_mul: lambda val: val,
    ModifierOperator.post_mul_immune: lambda val: val,
    ModifierOperator.post_div: lambda val: 1 / val,
    ModifierOperator.post_percent: lambda val: val / 100 + 1,
    ModifierOperator.post_assign: lambda val: val}

# List operator types, according to their already normalized values
ASSIGNMENTS = (
    ModifierOperator.pre_assign,
    ModifierOperator.post_assign)
ADDITIONS = (
    ModifierOperator.mod_add,
    ModifierOperator.mod_sub)
MULTIPLICATIONS = (
    ModifierOperator.pre_mul,
    ModifierOperator.pre_div,
    ModifierOperator.post_mul,
    ModifierOperator.post_mul_immune,
    ModifierOperator.post_div,
    ModifierOperator.post_percent)

# Following attributes have limited precision - only to second number after
# decimal separator
LIMITED_PRECISION = (
    Attribute.cpu,
    Attribute.power,
    Attribute.cpu_output,
    Attribute.power_output)

# List of exceptions calculate method may throw
CALCULATE_RAISABLE_EXCEPTIONS = (AttributeMetaError, BaseValueError)


class MutableAttributeMap:
    """Map which contains modified attribute values.

    It provides some of facilities which help to calculate, store and provide
    access to modified attribute values.
    """

    def __init__(self, item):
        self.__item = item
        # Actual container of calculated attributes.
        # Format: {attribute ID: value}
        self.__modified_attributes = {}
        # Override and cap maps are initialized as None to save memory, as they
        # are not needed most of the time
        self.__override_callbacks = None
        self.__cap_map = None

    def __getitem__(self, attr_id):
        # Overridden values are priority. Access 'private' override callbacks
        # map directly due to performance reasons
        if (
            self.__override_callbacks is not None and
            attr_id in self.__override_callbacks
        ):
            callback, args, kwargs = self.__override_callbacks[attr_id]
            return callback(*args, **kwargs)
        # If no override is set, use modified value. If value is stored in
        # modified map, it's considered valid
        try:
            val = self.__modified_attributes[attr_id]
        # Else, we have to run full calculation process
        except KeyError:
            try:
                val = self.__calculate(attr_id)
            except CALCULATE_RAISABLE_EXCEPTIONS as e:
                raise KeyError(attr_id) from e
            else:
                self.__modified_attributes[attr_id] = val
        return val

    def __len__(self):
        return len(self.keys())

    def __contains__(self, attr_id):
        return attr_id in self.keys()

    def __iter__(self):
        for k in self.keys():
            yield k

    def __delitem__(self, attr_id):
        # Clear the value in our calculated attributes dictionary
        try:
            del self.__modified_attributes[attr_id]
        # Do nothing if it wasn't calculated
        except KeyError:
            return
        # Launch message which notifies that attribute value may change
        # (normally calculated values are removed if their dependencies change)
        else:
            # Special message type if modified attribute is masked by override.
            # While exposed value cannot change in this case, underlying
            # modified value can
            if (
                self.__override_callbacks is not None and
                attr_id in self.__override_callbacks
            ):
                msg = InstrAttrValueChangedMasked(
                    item=self.__item, attr=attr_id)
                self.__publish(msg)
            else:
                msg = InstrAttrValueChanged(item=self.__item, attr=attr_id)
                self.__publish(msg)

    def get(self, attr_id, default=None):
        # Almost copy-paste of __getitem__ due to performance reasons -
        # attribute getters should make as few calls as possible, especially
        # when attribute is already calculated
        if (
            self.__override_callbacks is not None and
            attr_id in self.__override_callbacks
        ):
            callback, args, kwargs = self.__override_callbacks[attr_id]
            return callback(*args, **kwargs)
        try:
            val = self.__modified_attributes[attr_id]
        except KeyError:
            try:
                val = self.__calculate(attr_id)
            except CALCULATE_RAISABLE_EXCEPTIONS:
                return default
            else:
                self.__modified_attributes[attr_id] = val
        return val

    def keys(self):
        # Return union of attributes from base, modified and override dictionary
        return set(chain(
            self.__item._eve_type_attributes, self.__modified_attributes,
            self.__override_callbacks or {}))

    def items(self):
        return set((attr_id, self.get(attr_id)) for attr_id in self.keys())

    def clear(self):
        """Reset map to its initial state"""
        for attr in set(self.__modified_attributes):
            del self[attr]
        self.__cap_map = None

    def __calculate(self, attr_id):
        """Run calculations to find the actual value of attribute.

        Args:
            attr_id: ID of attribute to be calculated.

        Returns:
            Calculated attribute value.

        Raises:
            AttributeMetaError: If metadata of attribute being calculated cannot
                be fetched.
            BaseValueError: If base value for attribute being calculated cannot
                be found.
        """
        item = self.__item
        # Attribute object for attribute being calculated
        try:
            attr_meta = item._fit.source.cache_handler.get_attribute(attr_id)
        # Raise error if we can't get metadata for requested attribute
        except (AttributeError, AttributeFetchError) as e:
            msg = (
                'unable to fetch metadata for attribute {}, '
                'requested for eve type {}'
            ).format(attr_id, item._eve_type_id)
            logger.warning(msg)
            raise AttributeMetaError(attr_id) from e
        # Base attribute value which we'll use for modification
        try:
            result = item._eve_type_attributes[attr_id]
        # If attribute isn't available on eve type, base off its default value
        except KeyError:
            result = attr_meta.default_value
            # If eve type attribute is not specified and default value isn't
            # available, raise error - without valid base we can't keep going
            if result is None:
                msg = (
                    'unable to find base value for attribute {} on eve type {}'
                ).format(attr_id, item._eve_type_id)
                logger.info(msg)
                raise BaseValueError(attr_id)
        # Container for non-penalized modifications
        # Format: {operator: [values]}
        normal_mods = {}
        # Container for penalized modifications
        # Format: {operator: [values]}
        penalized_mods = {}
        # Now, go through all affectors affecting our item
        for mod_data in item._fit._calculator.get_modifications(item, attr_id):
            operator, mod_value, carrier_item = mod_data
            # Decide if it should be stacking penalized or not, based on
            # stackable property, carrier item eve type category and operator
            penalize = (
                not attr_meta.stackable and
                carrier_item._eve_type.category not in PENALTY_IMMUNE_CATS and
                operator in PENALIZABLE_OPERATORS)
            # Normalize operations to just three types: assignments, additions,
            # multiplications
            try:
                normalization_func = NORMALIZATION_MAP[operator]
            # Log error on any unknown operator types
            except KeyError:
                msg = (
                    'malformed modifier on eve type {}: unknown operator {}'
                ).format(carrier_item._eve_type_id, operator)
                logger.warning(msg)
                continue
            mod_value = normalization_func(mod_value)
            # Add value to appropriate dictionary
            if penalize:
                mod_list = penalized_mods.setdefault(operator, [])
            else:
                mod_list = normal_mods.setdefault(operator, [])
            mod_list.append(mod_value)
        # When data gathering is complete, process penalized modifications. They
        # are penalized on per-operator basis
        for operator, mod_list in penalized_mods.items():
            penalized_value = self.__penalize_values(mod_list)
            normal_mods.setdefault(operator, []).append(penalized_value)
        # Calculate result of normal dictionary, according to operator order
        for operator in sorted(normal_mods):
            mod_list = normal_mods[operator]
            # Pick best modification for assignments, based on high_is_good
            # value
            if operator in ASSIGNMENTS:
                if attr_meta.high_is_good:
                    result = max(mod_list)
                else:
                    result = min(mod_list)
            elif operator in ADDITIONS:
                for mod_val in mod_list:
                    result += mod_val
            elif operator in MULTIPLICATIONS:
                for mod_val in mod_list:
                    result *= mod_val
        # If attribute has upper cap, do not let its value to grow above it
        if attr_meta.max_attribute is not None:
            try:
                max_value = self[attr_meta.max_attribute]
            # If max value isn't available, don't cap anything
            except KeyError:
                pass
            else:
                result = min(result, max_value)
                # Let map know that capping attribute restricts current
                # attribute
                self._cap_set(attr_meta.max_attribute, attr_id)
        # Some of attributes are rounded for whatever reason, deal with it
        # after all the calculations
        if attr_id in LIMITED_PRECISION:
            result = round(result, 2)
        return result

    def __penalize_values(self, mod_list):
        """Calculate aggregated multiplier from list of multipliers.

        Assuming all multipliers received should be stacking penalized, and that
        they are normalized to multiplier form, calculate final multiplier.

        Args:
            mod_list: Iterable with multipliers.

        Returns:
            Final aggregated multiplier.
        """
        # Gather positive multipliers into one chain, negative into another
        chain_pos = []
        chain_neg = []
        for mod_val in mod_list:
            # Transform value into form of multiplier - 1 for ease of stacking
            # chain calculation
            mod_val -= 1
            if mod_val >= 0:
                chain_pos.append(mod_val)
            else:
                chain_neg.append(mod_val)
        # Strongest modifications always go first
        chain_pos.sort(reverse=True)
        chain_neg.sort()
        # Base final multiplier on 1
        res = 1
        for pen_chain in (chain_pos, chain_neg):
            # Same for intermediate per-chain result
            chain_res = 1
            for pos, mod in enumerate(pen_chain):
                # Ignore 12th modification and further as non-significant
                if pos > 10:
                    break
                # Apply stacking penalty based on modification position
                chain_res *= 1 + mod * PENALTY_BASE ** (pos ** 2)
            res *= chain_res
        return res

    # Override-related methods
    def _set_override_callback(self, attr_id, callback):
        """Set override for the attribute in the form of callback."""
        if self.__override_callbacks is None:
            self.__override_callbacks = {}
        # If the same callback is set, do nothing
        if self.__override_callbacks.get(attr_id) == callback:
            return
        self.__override_callbacks[attr_id] = callback
        # Exposed attribute value may change after setting/resetting override
        self.__publish(InstrAttrValueChanged(item=self.__item, attr=attr_id))

    def _del_override_callback(self, attr_id):
        """Remove override callback from attribute."""
        overrides = self.__override_callbacks or {}
        if attr_id not in overrides:
            return
        del overrides[attr_id]
        # Set overrides map to None if there're none left to save some memory
        if not overrides:
            self.__override_callbacks = None
        # Exposed attribute value may change after removing override
        self.__publish(InstrAttrValueChanged(item=self.__item, attr=attr_id))

    def _override_value_may_change(self, attr_id):
        """Notify everyone that callback value may change.

        When originator of callback knows that callback return value may (or
        will) change for an attribute, it should invoke this method.
        """

        self.__publish(InstrAttrValueChanged(item=self.__item, attr=attr_id))

    def _get_without_overrides(self, attr_id, default=None):
        """Get attribute value without using overrides."""
        # Partially borrowed from get() method
        try:
            val = self.__modified_attributes[attr_id]
        except KeyError:
            try:
                val = self.__calculate(attr_id)
            except CALCULATE_RAISABLE_EXCEPTIONS:
                return default
            else:
                self.__modified_attributes[attr_id] = val
        return val

    # Cap-related methods
    @property
    def _cap_map(self):
        # Returns map of attributes which cap something, and attributes capped
        # by them
        # Format {capping attribute ID: {capped attribute IDs}}
        return self.__cap_map or {}

    def _cap_set(self, capping_attr, capped_attr):
        if self.__cap_map is None:
            self.__cap_map = KeyedStorage()
        self.__cap_map.add_data_entry(capping_attr, capped_attr)

    def _cap_del(self, capping_attr, capped_attr):
        self.__cap_map.rm_data_entry(capping_attr, capped_attr)
        if not self.__cap_map:
            self.__cap_map = None

    # Auxiliary methods
    def __publish(self, message):
        fit = self.__item._fit
        if fit is not None:
            fit._publish(message)
