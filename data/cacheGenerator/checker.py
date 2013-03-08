#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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


from eos.const.eve import Effect
from eos.util.frozendict import frozendict


class Checker:
    """
    Class responsible for conducting checks and making
    data consistent for further stages of processing.

    Positional arguments:
    logger -- logger to use
    """

    def __init__(self, logger):
        self._logger = logger

    def preCleanup(self, data):
        """
        Run checks which should be performed on
        data which is yet to be cleaned.

        Positional arguments:
        data -- data to check
        """
        self.data = data
        primaryKeys = {'dgmattribs': ('attributeID',),
                       'dgmeffects': ('effectID',),
                       'dgmexpressions': ('expressionID',),
                       'dgmtypeattribs': ('typeID','attributeID'),
                       'dgmtypeeffects': ('typeID','effectID'),
                       'invgroups': ('groupID',),
                       'invtypes': ('typeID',)}
        for tableName, keyNames in primaryKeys.items():
            self._tablePk(tableName, keyNames)

    def preConvert(self, data):
        """
        As data convertor and eos relies on some
        assumptions, check that data corresponds to them.

        Positional arguments:
        data -- data to check
        """
        self.data = data
        self._attributeValueType()
        self._multipleDefaultEffects()
        self._collidingModuleRacks()

    def _tablePk(self, tableName, keyNames):
        """
        Check if all primary keys in table are integers.

        Positional arguments:
        tableName -- name of table to check
        keyNames -- names of fields which are considerred
        as primary keys in iterable
        """
        table = self.data[tableName]
        # Contains keys used in current table
        usedKeys = set()
        # Storage for rows which should be removed
        invalidRows = set()
        for datarow in sorted(table, key=lambda row: row['tablePos']):
            self._rowPk(keyNames, datarow, usedKeys, invalidRows)
        # If any invalid rows were detected, remove them and
        # write corresponding message to log
        if invalidRows:
            msg = '{} rows in table {} have invalid PKs, removing them'.format(len(invalidRows), tableName)
            self._logger.warning(msg, childName='cacheGenerator')
            table.difference_update(invalidRows)

    def _rowPk(self, keyNames, datarow, usedKeys, invalidRows):
        """
        Check row primary key for validity.

        Positional arguments:
        keyNames -- names of fields which contain keys
        datarow -- row to check
        usedKeys -- container with alreaady used keys
        invalids -- container for invalid rows
        """
        rowKey = []
        for keyName in keyNames:
            try:
                keyValue = datarow[keyName]
            # Invalidate row if it doesn't have any component
            # of primary key
            except KeyError:
                invalidRows.add(datarow)
                return
            # If primary key is not an integer
            if not isinstance(keyValue, int):
                invalidRows.add(datarow)
                return
            rowKey.append(keyValue)
        rowKey = tuple(rowKey)
        # If specified key is already used
        if rowKey in usedKeys:
            invalidRows.add(datarow)
            return
        usedKeys.add(rowKey)

    def _attributeValueType(self):
        """
        Check all attributes of all items for validity.
        Only ints and floats are considered as valid. Eos
        attribute calculation engine relies on this assumption.
        """
        invalidRows = set()
        table = self.data['dgmtypeattribs']
        for row in table:
            if not isinstance(row.get('value'), (int, float)):
                invalidRows.add(row)
        if invalidRows:
            msg = '{} attribute rows have non-numeric value, removing them'.format(len(invalidRows))
            self._logger.warning(msg, childName='cacheGenerator')
            table.difference_update(invalidRows)

    def _multipleDefaultEffects(self):
        """
        Each type must have one default effect at max. Data
        conversion (and resulting data structure) relies on
        this assumption.
        """
        # Set with IDs of types, which have default effect
        defeff = set()
        table = self.data['dgmtypeeffects']
        invalidRows = set()
        for row in sorted(table, key=lambda row: row['tablePos']):
            isDefault = row.get('isDefault')
            # We're interested only in default effects
            if isDefault is not True:
                continue
            typeId = row['typeID']
            # If we already saw default effect for given type ID,
            # invalidate current row
            if typeId in defeff:
                invalidRows.add(row)
            else:
                defeff.add(typeId)
        # Process ivalid rows, if any
        if invalidRows:
            msg = 'data contains {} excessive default effects, marking them as non-default'.format(len(invalidRows))
            self._logger.warning(msg, childName='cacheGenerator')
            # Replace isDefault field value with False for invalid rows
            table.difference_update(invalidRows)
            for invalidRow in invalidRows:
                newRow = {}
                for field, value in invalidRow.items():
                    newRow[field] = False if field == 'isDefault' else value
                table.add(frozendict(newRow))

    def _collidingModuleRacks(self):
        """
        Type of slot into which module is placed is detected
        using module's effects. Engine relies on assumption that
        each module has at max one such effect. This type of check
        is better to be performed after data cleanup, because slot
        type effects are still used on many other items (and thus
        are not needed to be removed), and errors for items which
        won't be actually used won't be printed.
        """
        table = self.data['dgmtypeeffects']
        rackEffects = (Effect.hiPower, Effect.medPower, Effect.loPower)
        rackedItems = set()
        invalidRows = set()
        for row in sorted(table, key=lambda row: row['tablePos']):
            effectId = row['effectID']
            # We're not interested in anything besides
            # rack effects
            if effectId not in rackEffects:
                continue
            typeId = row['typeID']
            if typeId in rackedItems:
                invalidRows.add(row)
            else:
                rackedItems.add(typeId)
        if invalidRows:
            msg = '{} rows contain colliding module racks, removing them'.format(len(invalidRows))
            self._logger.warning(msg, childName='cacheGenerator')
            table.difference_update(invalidRows)
