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


from unittest.mock import Mock

from eos.const.eos import State
from eos.fit.holder.item import Charge, ModuleHigh
from eos.fit.holder.mixin.state import MutableStateMixin
from eos.util.volatile_cache import InheritableVolatileMixin


class BaseHolder(MutableStateMixin):

    def __init__(self, type_id, state=State.offline, **kwargs):
        super().__init__(type_id=type_id, state=state, **kwargs)


class CachingHolder(BaseHolder, InheritableVolatileMixin):
    pass


class OtherCachingHolder(MutableStateMixin, InheritableVolatileMixin):

    def __init__(self, type_id, state=State.offline, **kwargs):
        super().__init__(type_id=type_id, state=state, **kwargs)


class CachingModule(ModuleHigh, InheritableVolatileMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._clear_volatile_attrs = Mock()


class CachingCharge(Charge, InheritableVolatileMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._clear_volatile_attrs = Mock()
