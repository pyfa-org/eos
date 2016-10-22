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


from eos.const.eos import Domain, State
from eos.const.eve import Attribute
from eos.fit.holder.mixin.state import ImmutableStateMixin
from eos.util.repr import make_repr_str


class Booster(ImmutableStateMixin):
    """
    Booster with all its special properties.

    Required arguments:
    type_id -- type ID of item which should serve as base
    for this item.

    Cooperative methods:
    __init__
    """

    def __init__(self, type_id, **kwargs):
        super().__init__(type_id=type_id, state=State.offline, **kwargs)

    @property
    def slot(self):
        return self.attributes.get(Attribute.boosterness)

    # Side-effect methods
    @property
    def side_effects(self):
        """
        Get map with data about booster side-effects.

        Return value as dictionary:
        {side-effect ID: (effect=effect object for this side-effect,
        chance=chance of setting in, status=side-effect status)}
        """
        side_effects = {}
        for effect_id, data in self._effect_data.items():
            if data.chance is not None:
                side_effects[effect_id] = data
        return side_effects

    def set_side_effect_status(self, effect_id, status):
        """
        Enable or disable side-effect.

        Required arguments:
        effect_id -- ID of side-effect
        status -- True for enabling, False for disabling
        """
        self._set_effects_status((effect_id,), status)

    def randomize_side_effects(self):
        """
        Randomize side-effects' status according to their
        chances to set in.
        """
        self._randomize_effects_status(effect_filter=set(self.side_effects))

    def enable_non_side_effects(self):
        """
        In certain circumstances non-side-effect can become disabled.
        Statuses of such effects are not exposed via Booster API, but
        fit with these will fail validation. This method enables all
        such effects.
        """
        to_enable = self._disabled_effects.difference(self.side_effects)
        self._set_effects_status(to_enable, True)

    # Auxiliary methods
    @property
    def _domain(self):
        return Domain.character

    def __repr__(self):
        spec = [['type_id', '_type_id']]
        return make_repr_str(self, spec)
