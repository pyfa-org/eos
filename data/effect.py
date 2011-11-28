#===============================================================================
# Copyright (C) 2011 Diego Duclos
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
#===============================================================================

class Effect(object):
    """
    Represents a single effect. Effects are the building blocks of types and are what actualy make a type do something.
    In turn, each effect is made out of pre- and a post-expression
    This class is typically reused by the dataHandler if the same id is requested multiple times.
    As such, there shouldn't be ANY fit-specific data on it
    """

    def __init__(self, id, preExpression, postExpression, isOffensive, isAssistance):
        self.id = id
        """The unique ID of an effect. Can be anything, as long as its unique, typically, the IDs CCP assigned to them in the SDD are used"""

        self.preExpression = preExpression
        """PreExpression of the effect. A preExpression is the expression that gets run when the module is activated"""

        self.postExpression = postExpression
        """
        PostExpression of the effect. A postExpression gets run when the module gets disabled.
        We do not use them for our undo implementation, however, some modules that do their stuff at end of run need these (like armor reps)
        """

        self.isOffensive = isOffensive
        """Whether the module is offensive (e.g. guns)"""

        self.isAssistance = isAssistance
        """Whether the module is helpful (e.g. Remote reps)"""

    def _prepare(self, owner, fit):
        """
        Prepares the effect for execution
        """
        self.preExpression.prepare(owner, fit)

    def _apply(self, owner, fit):
        """
        Apply this effect onto the passed fit
        """
        self.preExpression.apply(owner, fit)

    def _undo(self, owner, fit):
        """
        Undo this effect from the passed fit
        """
        self.preExpression.undo(owner, fit)
