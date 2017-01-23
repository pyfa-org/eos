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


from .exception import HolderAlreadyAssignedError, HolderFitMismatchError
from eos.fit.messages import HolderAdded, HolderRemoved


class HolderContainerBase:
    """
    Base class for any containers which are intended
    to ease management of holders. Hides fit-specific
    logic under its hood, letting real containers (which
    should inherit it) implement just container type-
    specific logic.

    Required arguments:
    fit -- fit, to which container is attached
    holder_class -- class of holders this container
    is allowed to contain
    """

    def __init__(self, holder_class):
        self.__holder_class = holder_class

    def _handle_holder_addition(self, fit, holder):
        """
        Do all the generic work to add holder to container.
        Must be called after holder has been assigned to
        specific container.
        """
        # Make sure we're not adding holder which already
        # belongs to other fit
        if holder._fit is not None:
            raise HolderAlreadyAssignedError(holder)
        # Finalize linking holders before handling sub-holders
        # and firing an event. This way we ensure that all
        # services  which may rely on fit/holder links will
        # work properly
        holder._fit = fit
        # Do not check if charge has proper fit link, because
        # consistency is kept by charge descriptor. We should
        # never get an exception here
        charge = getattr(holder, 'charge', None)
        if charge is not None:
            self._handle_holder_addition(fit, charge)
        fit._publish(HolderAdded(holder))

    def _handle_holder_removal(self, fit, holder):
        """
        Do all the generic work to remove holder to container.
        Must be called before holder has been removed from
        specific container.
        """
        # If everything is alright, this should never
        # be raised regardless of user actions
        if holder._fit is not fit:
            raise HolderFitMismatchError(holder)
        # Fire removal event before unlinking, same reason
        # as in addition handling method
        fit._publish(HolderRemoved(holder))
        charge = getattr(holder, 'charge', None)
        if charge is not None:
            self._handle_holder_removal(fit, charge)
        holder._fit = None

    def _check_class(self, holder, allow_none=False):
        """
        Check if class of passed holder corresponds
        to our expectations.
        """
        if isinstance(holder, self.__holder_class):
            return
        if holder is None and allow_none is True:
            return
        msg = 'only {} {} accepted, not {}'.format(
            self.__holder_class,
            'or None are' if allow_none is True else 'is',
            type(holder)
        )
        raise TypeError(msg)
