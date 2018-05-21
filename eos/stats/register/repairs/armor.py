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


from eos.eve_obj.effect.repairs.base import LocalArmorRepairEffect
from eos.eve_obj.effect.repairs.base import RemoteArmorRepairEffect
from eos.pubsub.message import EffectsStarted
from eos.pubsub.message import EffectsStopped
from .base import BaseRepairRegister


class ArmorRepairerRegister(BaseRepairRegister):

    def __init__(self, fit):
        self.__fit = fit
        # Format: {(item, effect), (item, effect)}
        self.__local_repairers = set()
        fit._subscribe(self, self._handler_map.keys())

    def get_rps(self, item, dmg_profile, reload):
        rps = 0
        for rep_item, rep_effect in self.__local_repairers:
            if item is not rep_item._solsys_carrier:
                continue
            rps += rep_effect.get_rps(rep_item, reload)
        proj_reg = (
            self.__fit.solar_system._calculator.
            _CalculationService__projections)
        for rep_item, rep_effect in proj_reg.get_tgt_projectors(item):
            if not isinstance(rep_effect, RemoteArmorRepairEffect):
                continue
            rps += rep_effect.get_rps(rep_item, reload)
        rps *= item._get_tanking_efficiency(dmg_profile, item.resists.armor)
        return rps

    def _handle_effects_started(self, msg):
        item_effects = msg.item._type_effects
        for effect_id in msg.effect_ids:
            effect = item_effects[effect_id]
            if isinstance(effect, LocalArmorRepairEffect):
                self.__local_repairers.add((msg.item, effect))

    def _handle_effects_stopped(self, msg):
        item_effects = msg.item._type_effects
        for effect_id in msg.effect_ids:
            effect = item_effects[effect_id]
            if isinstance(effect, LocalArmorRepairEffect):
                self.__local_repairers.remove((msg.item, effect))

    _handler_map = {
        EffectsStarted: _handle_effects_started,
        EffectsStopped: _handle_effects_stopped}
