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
from eos.pubsub.message import EffectApplied
from eos.pubsub.message import EffectUnapplied
from .base import BaseItemMixin


class BaseTargetableMixin(metaclass=ABCMeta):

    @abstractmethod
    def _get_effects_tgts(self, effect_ids):
        ...


class SingleTargetableMixin(BaseItemMixin, BaseTargetableMixin):

    def __init__(self, **kwargs):
        self.__target = None
        super().__init__(**kwargs)

    @property
    def target(self):
        return self.__target

    @target.setter
    def target(self, new_tgt):
        old_tgt = self.__target
        if old_tgt is new_tgt:
            return
        fit = self._fit
        if fit is not None:
            projectable_effects = set()
            item_effects = self._type_effects
            for effect_id in self._running_effect_ids:
                effect = item_effects[effect_id]
                if effect.is_projectable:
                    projectable_effects.add(effect_id)
            if old_tgt is not None:
                msgs = []
                for effect_id in projectable_effects:
                    msgs.append(EffectUnapplied(self, effect_id, (old_tgt,)))
                fit._publish_bulk(msgs)
            self.__target = new_tgt
            if new_tgt is not None:
                msgs = []
                for effect_id in projectable_effects:
                    msgs.append(EffectApplied(self, effect_id, (new_tgt,)))
                fit._publish_bulk(msgs)
        else:
            self.__target = new_tgt

    def _get_effects_tgts(self, effect_ids):
        effect_tgts = {}
        tgt = self.__target
        if tgt is not None:
            item_effects = self._type_effects
            for effect_id in effect_ids:
                effect = item_effects[effect_id]
                if effect.category_id == EffectCategoryId.target:
                    effect_tgts[effect_id] = tgt,
        return effect_tgts


class MultiTargetableMixin(BaseTargetableMixin):
    ...
