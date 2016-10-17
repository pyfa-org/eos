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


from eos.util.frozen_dict import FrozenDict
from .checker import Checker
from .cleaner import Cleaner
from .converter import Converter


class CacheGenerator:
    """
    Refactors and optimizes data into format suitable
    for Eos.
    """

    def __init__(self):
        self._checker = Checker()
        self._cleaner = Cleaner()
        self._converter = Converter()

    def run(self, data_handler):
        """
        Generate cache out of passed data.

        Required arguments:
        data_handler - data handler to use for getting data

        Return value:
        Dictionary in {entity type: [{field name: field value}]
        format
        """
        # Put all the data we need into single dictionary
        # Format, as usual, {table name: table}, where table
        # is set of rows, which are represented by frozendicts
        # {fieldName: fieldValue}. Combination of sets and
        # frozendicts is used to speed up several stages of
        # the generator.
        data = {}
        tables = {
            'evetypes': data_handler.get_evetypes,
            'evegroups': data_handler.get_evegroups,
            'dgmattribs': data_handler.get_dgmattribs,
            'dgmtypeattribs': data_handler.get_dgmtypeattribs,
            'dgmeffects': data_handler.get_dgmeffects,
            'dgmtypeeffects': data_handler.get_dgmtypeeffects,
            'dgmexpressions': data_handler.get_dgmexpressions
        }

        for tablename, method in tables.items():
            table_pos = 0
            # For faster processing of various operations,
            # freeze table rows and put them into set
            table = set()
            for row in method():
                # During  further generator stages. some of rows
                # may fall in risk groups, where all rows but one
                # need to be removed. To deterministically remove rows
                # based on position in original data, write position
                # to each row
                row['table_pos'] = table_pos
                table_pos += 1
                table.add(FrozenDict(row))
            data[tablename] = table

        # Run pre-cleanup checks, as cleaning and further stages
        # rely on some assumptions about the data
        self._checker.pre_cleanup(data)

        # Also normalize the data to make data structure
        # more consistent, and thus easier to clean properly
        self._converter.normalize(data)

        # Clean our container out of unwanted data
        self._cleaner.clean(data)

        # Verify that our data is ready for conversion
        self._checker.pre_convert(data)

        # Convert data into Eos-specific format. Here tables are
        # no longer represented by sets of frozendicts, but by
        # list of dicts
        data = self._converter.convert(data)

        return data
