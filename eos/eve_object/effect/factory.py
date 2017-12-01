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


from .effect import Effect


class EffectFactory:
    """Produces eve effects."""

    _effect_id_map = {}

    @classmethod
    def make(cls, effect_id, *args, **kwargs):
        """Produce an effect.

        Args:
            effect_id: ID of the effect to produce.
            *args: Arguments to pass to the effect constructor.
            **kwargs: Keyword arguments to pass to the effect constructor.

        Returns:
            Effect instance.
        """
        effect_class = cls._effect_id_map.get(effect_id, Effect)
        effect = effect_class(effect_id, *args, **kwargs)
        return effect

    @classmethod
    def register(cls, effect_id, effect_class):
        """Register effect class against effect ID."""
        if effect_id in cls._effect_id_map:
            raise KeyError('effect ID {} is taken'.format(effect_id))
        cls._effect_id_map[effect_id] = effect_class

