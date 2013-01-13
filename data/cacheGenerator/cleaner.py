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


from eos.eve.const import Group, Category


class Cleaner:
    """
    Class responsible for cleaning up unnecessary data
    from the database in automatic mode, using several
    pre-defined data relations.

    Positional arguments:
    logger -- logger to use
    """

    def __init__(self, logger):
        self._logger = logger

    def clean(self, data):
        self.data = data
        # Container to store signs of so-called strong data,
        # such rows are immune to removal. Dictionary structure
        # is the same as structure of general data container
        self.strongData = {}
        # Move some rows to strong data container
        self._pumpInvtypes()
        # Also contains data in the very same format, but tables/rows
        # in this table are considered as pending for removal
        self.trashedData = {}
        self._autocleanup()
        self._reportResults()

    def _pumpInvtypes(self):
        """
        Mark some hardcoded invtypes as strong.
        """
        # Tuple with categoryIDs of items we want to keep
        strongCategories = (Category.ship, Category.module, Category.charge,
                            Category.skill, Category.drone, Category.implant,
                            Category.subsystem)
        # Set with groupIDs of items we want to keep
        # It is set because we will need to modify it
        strongGroups = {Group.character, Group.effectBeacon}
        # Go through table data, filling valid groups set according to valid categories
        for datarow in self.data['invgroups']:
            if datarow.get('categoryID') in strongCategories:
                strongGroups.add(datarow['groupID'])
        rowsToPump = set()
        for datarow in self.data['invtypes']:
            if datarow.get('groupID') in strongGroups:
                rowsToPump.add(datarow)
        self._pumpData('invtypes', rowsToPump)

    def _autocleanup(self):
        """
        Define auto-cleanup workflow.
        """
        self._killWeak()
        self._changed = True
        # Cycle as long as we have changes during previous iteration.
        # We need this because contents of even invtypes may change, which,
        # in turn, will need to pull additional data into other tables
        while self._changed is True:
            self._changed = False
            self._reanimateAuxiliaryFriends()
            self._reestablishBrokenRelationships()

    def _killWeak(self):
        """
        Trash all data which isn't marked as strong.
        """
        for tableName, table in self.data.items():
            toTrash = set()
            strongRows = self.strongData.get(tableName, set())
            toTrash.update(table.difference(strongRows))
            self._trashData(tableName, toTrash)

    def _reanimateAuxiliaryFriends(self):
        """
        Restore rows in tables, which complement invtypes
        or serve as m:n mapping between invtypes and other tables.
        """
        # As we filter whole database using invtypes table,
        # gather invtype IDs we currently have in there
        typeIds = set(row['typeID'] for row in self.data['invtypes'])
        # Auxiliary tables are those which do not define
        # any entities, they just map one entities to others
        # or complement entities with additional data
        auxTables = ('dgmtypeattribs', 'dgmtypeeffects')
        for tableName in auxTables:
            toRestore = set()
            # Restore rows which map other entities to types
            for row in self.trashedData[tableName]:
                if row['typeID'] in typeIds:
                    toRestore.add(row)
            if toRestore:
                self._changed = True
                self._restoreData(tableName, toRestore)

    def _reestablishBrokenRelationships(self):
        """
        Restore all rows targeted by FKs of rows, which
        exist in actual data.
        """
        foreignKeys = {'dgmattribs':     {'maxAttributeID': ('dgmattribs', 'attributeID')},
                       'dgmeffects':     {'preExpression': ('dgmexpressions', 'expressionID'),
                                          'postExpression': ('dgmexpressions', 'expressionID'),
                                          'durationAttributeID': ('dgmattribs', 'attributeID'),
                                          'trackingSpeedAttributeID': ('dgmattribs', 'attributeID'),
                                          'dischargeAttributeID': ('dgmattribs', 'attributeID'),
                                          'rangeAttributeID': ('dgmattribs', 'attributeID'),
                                          'falloffAttributeID': ('dgmattribs', 'attributeID'),
                                          'fittingUsageChanceAttributeID': ('dgmattribs', 'attributeID')},
                       'dgmexpressions': {'arg1': ('dgmexpressions', 'expressionID'),
                                          'arg2': ('dgmexpressions', 'expressionID'),
                                          'expressionTypeID': ('invtypes', 'typeID'),
                                          'expressionGroupID': ('invgroups', 'groupID'),
                                          'expressionAttributeID': ('dgmattribs', 'attributeID')},
                       'dgmtypeattribs': {'typeID': ('invtypes', 'typeID'),
                                          'attributeID': ('dgmattribs', 'attributeID')},
                       'dgmtypeeffects': {'typeID': ('invtypes', 'typeID'),
                                          'effectID': ('dgmeffects', 'effectID')},
                       'invtypes':       {'groupID': ('invgroups', 'groupID')}}
        # Container for 'target data', matches with which are
        # going to be restored
        # Format: {(target table name, target column name): {data}}}
        targetData = {}
        for sourceTableName, tableFks in foreignKeys.items():
            for sourceFieldName, fkTarget in tableFks.items():
                targetTableName, targetFieldName = fkTarget
                for row in self.data[sourceTableName]:
                    fkValue = row.get(sourceFieldName)
                    # If there's no such field in a row or it is None,
                    # this is not a valid FK reference
                    if fkValue is None:
                        continue
                    dataSet = targetData.setdefault((targetTableName, targetFieldName), set())
                    dataSet.add(fkValue)
        # Now, when we have all the target data values, we may look for
        # rows, which have matching values, and restore them
        for targetSpec, targetValues in targetData.items():
            targetTableName, targetFieldName = targetSpec
            toRestore = set()
            for row in self.trashedData[targetTableName]:
                if row.get(targetFieldName) in targetValues:
                    toRestore.add(row)
            if toRestore:
                self._changed = True
                self._restoreData(targetTableName, toRestore)

    def _reportResults(self):
        """
        Run calculations to report about cleanup results
        to the logger.
        """
        tableMsgs = []
        for tableName in sorted(self.data):
            datalen = len(self.data[tableName])
            trashedlen = len(self.trashedData[tableName])
            try:
                ratio = trashedlen / (datalen + trashedlen)
            # Skip results if table was empty
            except ZeroDivisionError:
                continue
            tableMsgs.append('{:.1%} from {}'.format(ratio, tableName))
        if tableMsgs:
            msg = 'cleaned: {}'.format(', '.join(tableMsgs))
            self._logger.info(msg, childName='cacheGenerator')

    def _pumpData(self, tableName, datarows):
        """
        Auxiliary method, mark data rows as strong.

        Positional arguments:
        tableName -- name of table for which we're pumping data
        datarows -- set with rows to pump
        """
        strongRows = self.strongData.setdefault(tableName, set())
        strongRows.update(datarows)


    def _trashData(self, tableName, datarows):
        """
        Auxiliary method, mark data rows as pending removal.

        Positional arguments:
        tableName -- name of table for which we're removing data
        datarows -- set with rows to remove
        """
        dataTable = self.data[tableName]
        trashTable = self.trashedData.setdefault(tableName, set())
        # Update both trashed data and source data
        trashTable.update(datarows)
        dataTable.difference_update(datarows)

    def _restoreData(self, tableName, datarows):
        """
        Auxiliary method, move data from trash back to actual
        data container.

        Positional arguments:
        tableName -- name of table for which we're restoring data
        datarows -- set with rows to restore
        """
        dataTable = self.data[tableName]
        trashTable = self.trashedData[tableName]
        # Update both trashed data and source data
        dataTable.update(datarows)
        trashTable.difference_update(datarows)
