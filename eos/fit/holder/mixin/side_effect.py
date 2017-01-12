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


from .holder.holder import HolderBase


class SideEffectMixin(HolderBase):
    """
    Mixin intended to be used for holders which can have
    side-effects.
    """

    @property
    def side_effects(self):
        """
        Get map with data about holder side-effects.

        Return data as dictionary:
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
