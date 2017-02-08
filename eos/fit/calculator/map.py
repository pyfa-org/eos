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


from collections import namedtuple
from logging import getLogger
from math import exp

from eos.const.eos import ModifierOperator
from eos.const.eve import Category, Attribute
from eos.data.cache_handler.exception import AttributeFetchError
from eos.fit.null_source import NoSourceError
from eos.fit.messages import AttrValueChanged, AttrValueChangedMasked
from eos.util.keyed_set import KeyedSet
from .exception import AttributeMetaError, BaseValueError


OverrideData = namedtuple('OverrideData', ('value', 'persistent'))


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
    ModifierOperator.pre_mul,
    ModifierOperator.post_mul,
    ModifierOperator.post_percent,
    ModifierOperator.pre_div,
    ModifierOperator.post_div
)

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
    ModifierOperator.post_assign: lambda val: val
}

# List operator types, according to their already normalized values
ASSIGNMENTS = (
    ModifierOperator.pre_assign,
    ModifierOperator.post_assign
)
ADDITIONS = (
    ModifierOperator.mod_add,
    ModifierOperator.mod_sub
)
MULTIPLICATIONS = (
    ModifierOperator.pre_mul,
    ModifierOperator.pre_div,
    ModifierOperator.post_mul,
    ModifierOperator.post_mul_immune,
    ModifierOperator.post_div,
    ModifierOperator.post_percent
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
    item -- item, to which this map is assigned
    """

    def __init__(self, item):
        # Reference to item for internal needs
        self.__item = item
        # Actual container of calculated attributes
        # Format: {attribute ID: value}
        self.__modified_attributes = {}
        # Override and cap maps are initialized as None
        # to save memory, as they are not needed most of
        # the time
        self.__overridde_callbacks = None
        self.__cap_map = None

    def __getitem__(self, attr):
        # Overridden values are priority
        if attr in self._override_callbacks:
            callback, args, kwargs = self._override_callbacks[attr]
            return callback(*args, **kwargs)
        # If no override is set, use modified value
        return self.__get_modified_value(attr)

    def __len__(self):
        return len(self.keys())

    def __contains__(self, attr):
        return attr in self.keys()

    def __iter__(self):
        for k in self.keys():
            yield k

    def __delitem__(self, attr):
        # Clear the value in our calculated attributes dictionary
        try:
            del self.__modified_attributes[attr]
        # Do nothing if it wasn't calculated
        except KeyError:
            return
        # And make sure services are aware of changed value if it
        # actually was changed
        else:
            # Special message type if modified attribute is masked by override
            if attr in self._override_callbacks:
                self.__publish(AttrValueChangedMasked(item=self.__item, attr=attr))
            else:
                self.__publish(AttrValueChanged(item=self.__item, attr=attr))

    def get(self, attr, default=None):
        try:
            return self[attr]
        except KeyError:
            return default

    def keys(self):
        try:
            base_attrs = self.__item._eve_type.attributes
        except NoSourceError:
            base_attrs = {}
        # Return union of attributes from base, modified and override dictionary
        return self.__modified_attributes.keys() | base_attrs.keys() | self._override_callbacks.keys()

    def clear(self):
        """Reset map to its initial state."""
        for attr in self.__modified_attributes:
            del self[attr]
        self.__cap_map = None

    def __get_modified_value(self, attr):
        """Get modified value of an attribute, skipping overrides"""
        # If value is stored in modified map, it's considered as valid
        try:
            val = self.__modified_attributes[attr]
        # Else, we have to run full calculation process
        except KeyError:
            try:
                val = self.__modified_attributes[attr] = self.__calculate(attr)
            except (NoSourceError, AttributeMetaError, BaseValueError) as e:
                raise KeyError(attr) from e
            else:
                # Special message type if modified attribute is masked by override
                if attr in self._override_callbacks:
                    self.__publish(AttrValueChangedMasked(item=self.__item, attr=attr))
                else:
                    self.__publish(AttrValueChanged(item=self.__item, attr=attr))
        return val

    def __calculate(self, attr):
        """
        Run calculations to find the actual value of attribute.

        Required arguments:
        attr -- ID of attribute to be calculated

        Return value:
        Calculated attribute value

        Possible exceptions:
        NoSourceError -- cannot fetch info about base item
        AttributeMetaError -- cannot fetch metadata of attribute
            being calculated
        BaseValueError -- cannot find base value for attribute
            being calculated
        """
        # Assign eve type attributes first to make sure than in case when we're
        # calculating attribute for item without source, it fails with null
        # source error (triggered by accessing eve type attribute)
        base_attrs = self.__item._eve_type.attributes
        # Attribute object for attribute being calculated
        try:
            attr_meta = self.__item._fit.source.cache_handler.get_attribute(attr)
        # Raise error if we can't get metadata for requested attribute
        except (AttributeError, AttributeFetchError) as e:
            msg = 'unable to fetch metadata for attribute {}, requested for eve type {}'.format(
                attr, self.__item._eve_type_id)
            logger.error(msg)
            raise AttributeMetaError(attr) from e
        # Base attribute value which we'll use for modification
        try:
            result = base_attrs[attr]
        # If attribute isn't available on eve type, base off its default value
        except KeyError:
            result = attr_meta.default_value
            # If eve type attribute is not specified and default
            # value isn't available, raise error - without valid
            # base we can't go on
            if result is None:
                msg = 'unable to find base value for attribute {} on eve type {}'.format(
                    attr, self.__item._eve_type_id)
                logger.warning(msg)
                raise BaseValueError(attr)
        # Container for non-penalized modifications
        # Format: {operator: [values]}
        normal_mods = {}
        # Container for penalized modifications
        # Format: {operator: [values]}
        penalized_mods = {}
        # Now, go through all affectors affecting our item
        for operator, mod_value, carrier_item in self.__item._fit._calculator.get_modifications(self.__item, attr):
            # Decide if it should be stacking penalized or not, based on stackable property,
            # carrier item eve type category and operator
            penalize = (
                attr_meta.stackable is False and
                carrier_item._eve_type.category not in PENALTY_IMMUNE_CATEGORIES and
                operator in PENALIZABLE_OPERATORS
            )
            # Normalize operations to just three types:
            # assignments, additions, multiplications
            try:
                normalization_func = NORMALIZATION_MAP[operator]
            # Log error on any unknown operator types
            except KeyError:
                msg = 'malformed modifier on eve type {}: unknown operator {}'.format(
                    carrier_item._eve_type_id, operator)
                logger.warning(msg)
                continue
            mod_value = normalization_func(mod_value)
            # Add value to appropriate dictionary
            if penalize is True:
                mod_list = penalized_mods.setdefault(operator, [])
            else:
                mod_list = normal_mods.setdefault(operator, [])
            mod_list.append(mod_value)
        # When data gathering is complete, process penalized modifications
        # They are penalized on per-operator basis
        for operator, mod_list in penalized_mods.items():
            penalized_value = self.__penalize_values(mod_list)
            normal_mods.setdefault(operator, []).append(penalized_value)
        # Calculate result of normal dictionary, according to operator order
        for operator in sorted(normal_mods):
            mod_list = normal_mods[operator]
            # Pick best modification for assignments, based on high_is_good value
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
                self._cap_set(attr_meta.max_attribute, attr)
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
        # Gather positive modifications into one chain, negative
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
        # Strongest modifications always go first
        chain_positive.sort(reverse=True)
        chain_negative.sort()
        # Base final multiplier on 1
        list_result = 1
        for chain in (chain_positive, chain_negative):
            # Same for intermediate per-chain result
            chain_result = 1
            for position, modification in enumerate(chain):
                # Ignore 12th modification and further as non-significant
                if position > 10:
                    break
                # Apply stacking penalty based on modification position
                chain_result *= 1 + modification * PENALTY_BASE ** (position ** 2)
            list_result *= chain_result
        return list_result

    # Override-related methods
    @property
    def _override_callbacks(self):
        # Container for overriden attributes
        # Format: {attribute ID: (function, (args), {kw: args})}
        return self.__overridde_callbacks or {}

    def _set_override_callback(self, attr, callback):
        """Set override for the attribute in the form of callback"""
        if self.__overridde_callbacks is None:
            self.__overridde_callbacks = {}
        # If the same callback is set, do nothing
        if self.__overridde_callbacks.get(attr) == callback:
            return
        self.__overridde_callbacks[attr] = callback
        self.__publish(AttrValueChanged(item=self.__item, attr=attr))

    def _del_override_callback(self, attr):
        """Remove override callback from attribute"""
        overrides = self._override_callbacks
        if attr not in overrides:
            return
        del overrides[attr]
        # Set overrides map to None if there're none left to save some memory
        if len(overrides) == 0:
            self.__overridde_callbacks = None
        self.__publish(AttrValueChanged(item=self.__item, attr=attr))

    def _override_value_may_change(self, attr):
        """
        When originator of callback knows that callback return
        value may (or will) change for an attribute, it should
        invoke this method.
        """
        self.__publish(AttrValueChanged(item=self.__item, attr=attr))

    def _get_without_overrides(self, attr, default=None):
        """Get attribute value without using overrides"""
        try:
            return self.__get_modified_value(attr)
        except KeyError:
            return default

    # Cap-related methods
    @property
    def _cap_map(self):
        # Returns map of attributes which cap something, and attributes
        # capped by them
        # Format {capping attribute ID: {capped attribute IDs}}
        return self.__cap_map or {}

    def _cap_set(self, capping_attr, capped_attr):
        if self.__cap_map is None:
            self.__cap_map = KeyedSet()
        self.__cap_map.add_data(capping_attr, capped_attr)

    def _cap_del(self, capping_attr, capped_attr):
        self.__cap_map.rm_data(capping_attr, capped_attr)
        if len(self.__cap_map) == 0:
            self.__cap_map = None

    # Auxiliary methods
    def __publish(self, message):
        fit = self.__item._fit
        if fit is not None:
            fit._publish(message)
