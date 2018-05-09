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


from abc import ABCMeta
from abc import abstractmethod

from eos.const.eve import EffectCategoryId
from .base import BaseItemMixin


class BaseTgtMixin(metaclass=ABCMeta):

    @abstractmethod
    def _get_effects_targets(self, effect_ids):
        ...


class SingleTgtMixin(BaseItemMixin, BaseTgtMixin):

    def __init__(self, **kwargs):
        self.__target = None
        super().__init__(**kwargs)

    @property
    def target(self):
        return self.__target

    @target.setter
    def target(self, new_tgt):
        self.__target = new_tgt

    def _get_effects_targets(self, effect_ids):
        effect_targets = {}
        tgt = self.__target
        if tgt is not None:
            item_effects = self._type_effects
            for effect_id in effect_ids:
                effect = item_effects[effect_id]
                if effect.category_id == EffectCategoryId.target:
                    effect_targets[effect_id] = tgt
        return effect_targets


class MultiTgtMixin(BaseTgtMixin):
    ...
