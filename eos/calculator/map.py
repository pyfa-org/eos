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


import math
from collections import namedtuple
from itertools import chain
from logging import getLogger

from eos.cache_handler import AttrFetchError
from eos.const.eos import ModAggregateMode
from eos.const.eos import ModOperator
from eos.const.eve import AttrId
from eos.const.eve import TypeCategoryId
from eos.pubsub.message import AttrsValueChanged
from eos.util.keyed_storage import KeyedStorage
from .exception import AttrMetadataError
from .exception import BaseValueError


OverrideData = namedtuple('OverrideData', ('value', 'persistent'))


logger = getLogger(__name__)


# Stacking penalty base constant, used in attribute calculations
PENALTY_BASE = 1 / math.exp((1 / 2.67) ** 2)

# Items belonging to these categories never have their effects stacking
# penalized
PENALTY_IMMUNE_CATEGORY_IDS = (
    TypeCategoryId.ship,
    TypeCategoryId.charge,
    TypeCategoryId.skill,
    TypeCategoryId.implant,
    TypeCategoryId.subsystem)

# Tuple with penalizable operators
PENALIZABLE_OPERATORS = (
    ModOperator.pre_mul,
    ModOperator.post_mul,
    ModOperator.post_percent,
    ModOperator.pre_div,
    ModOperator.post_div)

# Map which helps to normalize modifications
NORMALIZATION_MAP = {
    ModOperator.pre_assign: lambda value: value,
    ModOperator.pre_mul: lambda value: value - 1,
    ModOperator.pre_div: lambda value: 1 / value - 1,
    ModOperator.mod_add: lambda value: value,
    ModOperator.mod_sub: lambda value: -value,
    ModOperator.post_mul: lambda value: value - 1,
    ModOperator.post_mul_immune: lambda value: value - 1,
    ModOperator.post_div: lambda value: 1 / value - 1,
    ModOperator.post_percent: lambda value: value / 100,
    ModOperator.post_assign: lambda value: value}

# List operator types, according to their already normalized values
ASSIGNMENT_OPERATORS = (
    ModOperator.pre_assign,
    ModOperator.post_assign)
ADDITION_OPERATORS = (
    ModOperator.mod_add,
    ModOperator.mod_sub)
MULTIPLICATION_OPERATORS = (
    ModOperator.pre_mul,
    ModOperator.pre_div,
    ModOperator.post_mul,
    ModOperator.post_mul_immune,
    ModOperator.post_div,
    ModOperator.post_percent)

# Following attributes have limited precision - only to second digit after
# decimal separator
LIMITED_PRECISION_ATTR_IDS = (
    AttrId.cpu,
    AttrId.power,
    AttrId.cpu_output,
    AttrId.power_output)

# List of exceptions calculate method may throw
CALCULATE_RAISABLE_EXCEPTIONS = (AttrMetadataError, BaseValueError)


class MutableAttrMap:
    """Map which contains modified attribute values.

    It provides some of facilities which help to calculate, store and provide
    access to modified attribute values.
    """

    def __init__(self, item):
        self.__item = item
        # Actual container of calculated attributes.
        # Format: {attribute ID: value}
        self.__modified_attrs = {}
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
            value = self.__modified_attrs[attr_id]
        # Else, we have to run full calculation process
        except KeyError:
            try:
                value = self.__calculate(attr_id)
            except CALCULATE_RAISABLE_EXCEPTIONS as e:
                raise KeyError(attr_id) from e
            else:
                self.__modified_attrs[attr_id] = value
        return value

    def __len__(self):
        return len(self.keys())

    def __contains__(self, attr_id):
        return attr_id in self.keys()

    def __iter__(self):
        for k in self.keys():
            yield k

    def _force_recalc(self, attr_id):
        """
        Force recalculation of attribute with passed ID.

        Returns:
            True if attribute was calculated, False if it wasn't.
        """
        try:
            del self.__modified_attrs[attr_id]
        except KeyError:
            return False
        else:
            return True

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
            value = self.__modified_attrs[attr_id]
        except KeyError:
            try:
                value = self.__calculate(attr_id)
            except CALCULATE_RAISABLE_EXCEPTIONS:
                return default
            else:
                self.__modified_attrs[attr_id] = value
        return value

    def keys(self):
        # Return union of attributes from base, modified and override dictionary
        return set(chain(
            self.__item._type_attrs, self.__modified_attrs,
            self.__override_callbacks or {}))

    def items(self):
        return set((attr_id, self.get(attr_id)) for attr_id in self.keys())

    def _clear(self):
        """
        Reset map to its initial state.

        Overrides are not removed. Messages for cleared attributes are not sent.
        """
        self.__modified_attrs.clear()
        self.__cap_map = None

    def __calculate(self, attr_id):
        """Run calculations to find the actual value of attribute.

        Args:
            attr_id: ID of attribute to be calculated.

        Returns:
            Calculated attribute value.

        Raises:
            AttrMetadataError: If metadata of attribute being calculated cannot
                be fetched.
            BaseValueError: If base value for attribute being calculated cannot
                be found.
        """
        item = self.__item
        # Attribute object for attribute being calculated
        try:
            attr = item._fit.solar_system.source.cache_handler.get_attr(attr_id)
        # Raise error if we can't get metadata for requested attribute
        except (AttributeError, AttrFetchError) as e:
            msg = (
                'unable to fetch metadata for attribute {}, '
                'requested for item type {}'
            ).format(attr_id, item._type_id)
            logger.warning(msg)
            raise AttrMetadataError(attr_id) from e
        # Base attribute value which we'll use for modification
        try:
            value = item._type_attrs[attr_id]
        # If attribute isn't available on item type, base off its default value
        except KeyError:
            value = attr.default_value
            # If item type attribute is not specified and default value isn't
            # available, raise error - without valid base we can't keep going
            if value is None:
                msg = (
                    'unable to find base value for attribute {} on item type {}'
                ).format(attr_id, item._type_id)
                logger.info(msg)
                raise BaseValueError(attr_id)
        # Format: {operator: [values]}
        stack = {}
        # Format: {operator: [values]}
        stack_penalized = {}
        # Format: {(operator, aggregate key): [(value, penalize)]}
        aggregate_min = {}
        # Format: {(operator, aggregate key): [(value, penalize)]}
        aggregate_max = {}
        # Now, go through all affectors affecting our item
        for (
            mod_operator, mod_value, resist_value,
            mod_aggregate_mode, mod_aggregate_key, affector_item) in (
                item._fit.solar_system._calculator.get_modifications(
                    item, attr_id)
        ):
            # Normalize operations to just three types: assignments, additions,
            # reduced multiplications
            try:
                normalization_func = NORMALIZATION_MAP[mod_operator]
            # Log error on any unknown operator types
            except KeyError:
                msg = (
                    'malformed modifier on item type {}: unknown operator {}'
                ).format(affector_item._type_id, mod_operator)
                logger.warning(msg)
                continue
            # Resistance attribute actually defines resonance, where 1 means 0%
            # resistance and 0 means 100% resistance
            mod_value = normalization_func(mod_value) * resist_value
            # Decide if modification should be stacking penalized or not
            penalize = (
                not attr.stackable and
                affector_item._type.category_id not in
                PENALTY_IMMUNE_CATEGORY_IDS and
                mod_operator in PENALIZABLE_OPERATORS)
            if mod_aggregate_mode == ModAggregateMode.stack:
                if penalize:
                    stack_penalized.setdefault(mod_operator, []).append(
                        mod_value)
                else:
                    stack.setdefault(mod_operator, []).append(mod_value)
            elif mod_aggregate_mode == ModAggregateMode.minimum:
                aggregate_min.setdefault(
                    (mod_operator, mod_aggregate_key), []).append(
                    (mod_value, penalize))
            elif mod_aggregate_mode == ModAggregateMode.maximum:
                aggregate_max.setdefault(
                    (mod_operator, mod_aggregate_key), []).append(
                    (mod_value, penalize))
        for container, aggregate_func, sort_func in (
            (aggregate_min, min, lambda i: (i[0], i[1])),
            (aggregate_max, max, lambda i: (i[0], not i[1]))
        ):
            for k, v in container.items():
                mod_operator = k[0]
                mod_value, penalize = aggregate_func(v, key=sort_func)
                if penalize:
                    stack_penalized.setdefault(mod_operator, []).append(
                        mod_value)
                else:
                    stack.setdefault(mod_operator, []).append(mod_value)
        # When data gathering is complete, process penalized modifications. They
        # are penalized on per-operator basis
        for mod_operator, mod_values in stack_penalized.items():
            penalized_value = self.__penalize_values(mod_values)
            stack.setdefault(mod_operator, []).append(penalized_value)
        # Calculate value of non-penalized modifications, according to operator
        # order
        for mod_operator in sorted(stack):
            mod_values = stack[mod_operator]
            # Pick best modification for assignments, based on high_is_good
            # value
            if mod_operator in ASSIGNMENT_OPERATORS:
                if attr.high_is_good:
                    value = max(mod_values)
                else:
                    value = min(mod_values)
            elif mod_operator in ADDITION_OPERATORS:
                for mod_value in mod_values:
                    value += mod_value
            elif mod_operator in MULTIPLICATION_OPERATORS:
                for mod_value in mod_values:
                    value *= 1 + mod_value
        # If attribute has upper cap, do not let its value to grow above it
        if attr.max_attr_id is not None:
            try:
                max_value = self[attr.max_attr_id]
            # If max value isn't available, don't cap anything
            except KeyError:
                pass
            else:
                value = min(value, max_value)
                # Let map know that capping attribute restricts current
                # attribute
                self._cap_set(attr.max_attr_id, attr_id)
        # Some of attributes are rounded for whatever reason, deal with it after
        # all the calculations
        if attr_id in LIMITED_PRECISION_ATTR_IDS:
            value = round(value, 2)
        return value

    def __penalize_values(self, mod_values):
        """Calculate aggregated reduced multiplier.

        Assuming all multipliers received should be stacking penalized, and that
        they are normalized to reduced multiplier form, calculate final
        reduced multiplier.

        Args:
            mod_values: Iterable with reduced multipliers.

        Returns:
            Final aggregated reduced multiplier.
        """
        # Gather positive multipliers into one chain, negative into another
        chain_positive = []
        chain_negative = []
        for mod_value in mod_values:
            if mod_value >= 0:
                chain_positive.append(mod_value)
            else:
                chain_negative.append(mod_value)
        # Strongest modifications always go first
        chain_positive.sort(reverse=True)
        chain_negative.sort()
        # Base final multiplier on 1
        value = 1
        for penalization_chain in (chain_positive, chain_negative):
            # Same for intermediate per-chain value
            chain_value = 1
            for pos, mod_value in enumerate(penalization_chain):
                # Ignore 12th modification and further as non-significant
                if pos > 10:
                    break
                # Apply stacking penalty based on modification position
                chain_value *= 1 + mod_value * PENALTY_BASE ** (pos ** 2)
            value *= chain_value
        return value - 1

    # Override-related methods
    @property
    def _override_callbacks(self):
        return self.__override_callbacks or {}

    def _set_override_callback(self, attr_id, callback):
        """Set override for the attribute in the form of callback."""
        if self.__override_callbacks is None:
            self.__override_callbacks = {}
        # If the same callback is set, do nothing
        if self.__override_callbacks.get(attr_id) == callback:
            return
        self.__override_callbacks[attr_id] = callback
        # Exposed attribute value may change after setting/resetting override
        self.__publish(AttrsValueChanged({self.__item: {attr_id}}))

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
        self.__publish(AttrsValueChanged({self.__item: {attr_id}}))

    def _override_value_may_change(self, attr_id):
        """Notify everyone that callback value may change.

        When originator of callback knows that callback return value may (or
        will) change for an attribute, it should invoke this method.
        """
        self.__publish(AttrsValueChanged({self.__item: {attr_id}}))

    def _get_without_overrides(self, attr_id, default=None):
        """Get attribute value without using overrides."""
        # Partially borrowed from get() method
        try:
            value = self.__modified_attrs[attr_id]
        except KeyError:
            try:
                value = self.__calculate(attr_id)
            except CALCULATE_RAISABLE_EXCEPTIONS:
                return default
            else:
                self.__modified_attrs[attr_id] = value
        return value

    # Cap-related methods
    @property
    def _cap_map(self):
        """Returns map which defines value caps.

        It includes attributes which cap something, and attributes being capped
        by them.
        """
        # Format {capping attribute ID: {capped attribute IDs}}
        return self.__cap_map or {}

    def _cap_set(self, capping_attr_id, capped_attr_id):
        if self.__cap_map is None:
            self.__cap_map = KeyedStorage()
        self.__cap_map.add_data_entry(capping_attr_id, capped_attr_id)

    def _cap_del(self, capping_attr_id, capped_attr_id):
        self.__cap_map.rm_data_entry(capping_attr_id, capped_attr_id)
        if not self.__cap_map:
            self.__cap_map = None

    # Auxiliary methods
    def __publish(self, msg):
        try:
            publish_func = self.__item._fit._publish
        except AttributeError:
            pass
        else:
            publish_func(msg)
