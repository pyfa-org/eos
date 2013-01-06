#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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


from eos.util.frozendict import frozendict
from .checker import Checker
from .cleaner import Cleaner
from .converter import Converter


class CacheUpdater:
    """
    Refactors and optimizes data into format suitable
    for Eos.

    Positional keywords:
    logger -- logger to use for errors
    """

    def __init__(self, logger):
        self._logger = logger

    def run(self, dataHandler):
        """
        Refactor data.

        Positional arguments:
        dataHandler - data handler to use for getting data

        Return value:
        Dictionary in {table name: {table key: table row}} format
        """
        # Put all the data we need into single dictionary
        # Format, as usual, {table name: table}, where table
        # is set of rows, which are represented by frozendicts
        # {fieldName: fieldValue}
        data = {}
        tables = {'invtypes': dataHandler.getInvtypes,
                  'invgroups': dataHandler.getInvgroups,
                  'dgmattribs': dataHandler.getDgmattribs,
                  'dgmtypeattribs': dataHandler.getDgmtypeattribs,
                  'dgmeffects': dataHandler.getDgmeffects,
                  'dgmtypeeffects': dataHandler.getDgmtypeeffects,
                  'dgmexpressions': dataHandler.getDgmexpressions}
        for tablename, method in tables.items():
            # For faster processing of various operations,
            # freeze table rows and put them into set
            table = set()
            for row in method():
                table.add(frozendict(row))
            data[tablename] = table

        # First, we need to normalize data before any checks,
        # because data which is not normalized may cause check
        # failures or incomplete checks
        converter = Converter(self._logger)
        converter.normalize(data)

        # Now, run pre-cleanup checks, as cleaner relies
        # on some assumptions about the data
        checker = Checker(self._logger)
        checker.preCleanup(data)

        # Clean our container out of unwanted data
        cleaner = Cleaner(self._logger)
        cleaner.clean(data)

        # Verify that our data is ready for conversion
        checker.preConvert(data)

        # Convert data into Eos-specific format
        data = converter.convert(data)

        return data
