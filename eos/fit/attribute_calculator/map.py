# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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


from logging import getLogger
from math import exp

from eos.const.eos import Operator
from eos.const.eve import Category, Attribute
from eos.data.cache_handler.exception import AttributeFetchError
from eos.util.keyed_set import KeyedSet
from .exception import BaseValueError, AttributeMetaError, OperatorError


logger = getLogger(__name__)


# Stacking penalty base constant, used in attribute calculations
PENALTY_BASE = 1 / exp((1 / 2.67) ** 2)

# Items belonging to these categories never have
# their effects stacking penalized
PENALTY_IMMUNE_CATEGORIES = (
    Category.ship,
    Category.charge,
    Category.skill,
    Category.implant,
    Category.subsystem
)

# Tuple with penalizable operators
PENALIZABLE_OPERATORS = (
    Operator.pre_mul,
    Operator.post_mul,
    Operator.post_percent,
    Operator.pre_div,
    Operator.post_div
)

# Map which helps to normalize modifiers
NORMALIZATION_MAP = {
    Operator.pre_assign: lambda val: val,
    Operator.pre_mul: lambda val: val,
    Operator.pre_div: lambda val: 1 / val,
    Operator.mod_add: lambda val: val,
    Operator.mod_sub: lambda val: -val,
    Operator.post_mul: lambda val: val,
    Operator.post_div: lambda val: 1 / val,
    Operator.post_percent: lambda val: val / 100 + 1,
    Operator.post_assign: lambda val: val
}

# List operator types, according to their already normalized values
ASSIGNMENTS = (
    Operator.pre_assign,
    Operator.post_assign
)
ADDITIONS = (
    Operator.mod_add,
    Operator.mod_sub
)
MULTIPLICATIONS = (
    Operator.pre_mul,
    Operator.pre_div,
    Operator.post_mul,
    Operator.post_div,
    Operator.post_percent
)

# Following attributes have limited precision - only
# to second number after point
LIMITED_PRECISION = (
    Attribute.cpu,
    Attribute.power,
    Attribute.cpu_output,
    Attribute.power_output
)


class MutableAttributeMap:
    """
    Calculate, store and provide access to modified attribute values.

    Required arguments:
    holder -- holder, to which this map is assigned
    """

    def __init__(self, holder):
        # Reference to holder for internal needs
        self.__holder = holder
        # Actual container of calculated attributes
        # Format: {attribute ID: value}
        self.__modified_attributes = {}
        # This variable stores map of attributes which cap
        # something, and attributes capped by them. Initialized
        # to None to not waste memory, will be changed to dict
        # when needed.
        # Format {capping attribute ID: {capped attribute IDs}}
        self._cap_map = None

    def __getitem__(self, attr):
        # Special handling for skill level attribute
        if attr == Attribute.skill_level:
            # Attempt to return level attribute of holder
            try:
                val = self.__holder.level
            # Try regular way of getting attribute, if accessing
            # level attribute failed
            except AttributeError:
                pass
            else:
                return val
        # If carrier holder isn't assigned to any fit, then
        # we can use just item's original attributes
        if self.__holder._fit is None:
            val = self.__holder.item.attributes[attr]
            return val
        # If value is stored, it's considered valid
        try:
            val = self.__modified_attributes[attr]
        # Else, we have to run full calculation process
        except KeyError:
            try:
                val = self.__modified_attributes[attr] = self.__calculate(attr)
            except BaseValueError as e:
                msg = 'unable to find base value for attribute {} on item {}'.format(
                    e.args[0], self.__holder.item.id)
                logger.warning(msg)
                raise KeyError(attr) from e
            except AttributeMetaError as e:
                msg = 'unable to fetch metadata for attribute {}, requested for item {}'.format(
                    e.args[0], self.__holder.item.id)
                logger.error(msg)
                raise KeyError(attr) from e
            self.__holder._fit._link_tracker.clear_holder_attribute_dependents(self.__holder, attr)
        return val

    def __len__(self):
        return len(self.keys())

    def __contains__(self, attr):
        # Seek for attribute in both modified attribute container
        # and original item attributes
        result = attr in self.__modified_attributes or attr in self.__holder.item.attributes
        return result

    def __iter__(self):
        for k in self.keys():
            yield k

    def __delitem__(self, attr):
        # Clear the value in our calculated attributes dictionary
        try:
            del self.__modified_attributes[attr]
        # Do nothing if it wasn't calculated
        except KeyError:
            pass
        # And make sure all other attributes relying on it
        # are cleared too
        else:
            self.__holder._fit._link_tracker.clear_holder_attribute_dependents(self.__holder, attr)

    def __setitem__(self, attr, value):
        # Write value and clear all attributes relying on it
        self.__modified_attributes[attr] = value
        self.__holder._fit._link_tracker.clear_holder_attribute_dependents(self.__holder, attr)

    def get(self, attr, default=None):
        try:
            return self[attr]
        except KeyError:
            return default

    def keys(self):
        # Return union of both dicts
        return self.__modified_attributes.keys() | self.__holder.item.attributes.keys()

    def clear(self):
        """Reset map to its initial state."""
        self.__modified_attributes.clear()
        self._cap_map = None

    def __calculate(self, attr):
        """
        Run calculations to find the actual value of attribute.

        Required arguments:
        attr -- ID of attribute to be calculated

        Return value:
        Calculated attribute value

        Possible exceptions:
        BaseValueError -- attribute cannot be calculated, as its
        base value is not available
        """
        # Assign base item attributes first to make sure than in case when
        # we're calculating attribute for item/fit without source, it fails
        # with null source error (triggered by accessing item's attribute)
        item_attrs = self.__holder.item.attributes
        # Attribute object for attribute being calculated
        try:
            attr_meta = self.__holder._fit.source.cache_handler.get_attribute(attr)
        # Raise error if we can't get metadata for requested attribute
        except (AttributeError, AttributeFetchError) as e:
            raise AttributeMetaError(attr) from e
        # Base attribute value which we'll use for modification
        try:
            result = item_attrs[attr]
        # If attribute isn't available on base item,
        # base off its default value
        except KeyError:
            result = attr_meta.default_value
            # If original attribute is not specified and default
            # value isn't available, raise error - without valid
            # base we can't go on
            if result is None:
                raise BaseValueError(attr)
        # Container for non-penalized modifiers
        # Format: {operator: [values]}
        normal_mods = {}
        # Container for penalized modifiers
        # Format: {operator: [values]}
        penalized_mods = {}
        # Now, go through all affectors affecting our holder
        for affector in self.__holder._fit._link_tracker.get_affectors(self.__holder, attr=attr):
            try:
                source_holder, modifier = affector
                operator = modifier.operator
                # Decide if it should be stacking penalized or not, based on stackable property,
                # source item category and operator
                penalize = (
                    attr_meta.stackable is False and
                    source_holder.item.category not in PENALTY_IMMUNE_CATEGORIES and
                    operator in PENALIZABLE_OPERATORS
                )
                try:
                    mod_value = source_holder.attributes[modifier.src_attr]
                # Silently skip current affector: error should already
                # be logged by map before it raised KeyError
                except KeyError:
                    continue
                # Normalize operations to just three types:
                # assignments, additions, multiplications
                try:
                    normalization_func = NORMALIZATION_MAP[operator]
                # Raise error on any unknown operator types
                except KeyError as e:
                    raise OperatorError(operator) from e
                mod_value = normalization_func(mod_value)
                # Add value to appropriate dictionary
                if penalize is True:
                    mod_list = penalized_mods.setdefault(operator, [])
                else:
                    mod_list = normal_mods.setdefault(operator, [])
                mod_list.append(mod_value)
            # Handle operator type failure
            except OperatorError as e:
                msg = 'malformed modifier on item {}: unknown operator {}'.format(
                    source_holder.item.id, e.args[0])
                logger.warning(msg)
                continue
        # When data gathering is complete, process penalized modifiers
        # They are penalized on per-operator basis
        for operator, mod_list in penalized_mods.items():
            penalized_value = self.__penalize_values(mod_list)
            mod_list = normal_mods.setdefault(operator, [])
            mod_list.append(penalized_value)
        # Calculate result of normal dictionary, according to operator order
        for operator in sorted(normal_mods):
            mod_list = normal_mods[operator]
            # Pick best modifier for assignments, based on high_is_good value
            if operator in ASSIGNMENTS:
                result = max(mod_list) if attr_meta.high_is_good is True else min(mod_list)
            elif operator in ADDITIONS:
                for mod_val in mod_list:
                    result += mod_val
            elif operator in MULTIPLICATIONS:
                for mod_val in mod_list:
                    result *= mod_val
        # If attribute has upper cap, do not let
        # its value to grow above it
        if attr_meta.max_attribute is not None:
            try:
                max_value = self[attr_meta.max_attribute]
            # If max value isn't available, don't
            # cap anything
            except KeyError:
                pass
            else:
                result = min(result, max_value)
                # Let map know that capping attribute
                # restricts current attribute
                if self._cap_map is None:
                    self._cap_map = KeyedSet()
                # Fill cap map with data: capping attribute and capped attribute
                self._cap_map.add_data(attr_meta.max_attribute, attr)
        # Some of attributes are rounded for whatever reason,
        # deal with it after all the calculations
        if attr in LIMITED_PRECISION:
            result = round(result, 2)
        return result

    def __penalize_values(self, mod_list):
        """
        Calculate aggregated factor of passed factors, taking into
        consideration stacking penalty.

        Positional argument:
        mod_list -- list of factors

        Return value:
        Final aggregated factor of passed mod_list
        """
        # Gather positive modifiers into one chain, negative
        # into another
        chain_positive = []
        chain_negative = []
        for mod_val in mod_list:
            # Transform value into form of multiplier - 1 for ease of
            # stacking chain calculation
            mod_val -= 1
            if mod_val >= 0:
                chain_positive.append(mod_val)
            else:
                chain_negative.append(mod_val)
        # Strongest modifiers always go first
        chain_positive.sort(reverse=True)
        chain_negative.sort()
        # Base final multiplier on 1
        list_result = 1
        for chain in (chain_positive, chain_negative):
            # Same for intermediate per-chain result
            chain_result = 1
            for position, modifier in enumerate(chain):
                # Ignore 12th modifier and further as non-significant
                if position > 10:
                    break
                # Apply stacking penalty based on modifier position
                chain_result *= 1 + modifier * PENALTY_BASE ** (position ** 2)
            list_result *= chain_result
        return list_result
