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


from collections.abc import Iterable
from itertools import chain
from logging import getLogger

from eos.const.eve import AttrId
from eos.const.eve import TypeCategoryId
from eos.const.eve import TypeGroupId


logger = getLogger(__name__)


class Cleaner:
    """Removes unnecessary data."""

    def clean(self, data):
        """Remove unnecessary data.

        Process is automatic and needs no external configuration, it uses data
        relationships hardcoded in class' methods.

        Args:
            data: Dictionary in {table name: {table, rows}} format.
        """
        self.data = data
        # Container to store signs of so-called strong data, such rows are
        # immune to removal. Dictionary structure is the same as structure of
        # general data container
        self.strong_data = {}
        # Move some rows to strong data container
        self._pump_evetypes()
        # Also contains data in the very same format, but tables/rows in this
        # table are considered as pending for removal
        self.trashed_data = {}
        self._autocleanup()
        self._report_results()

    def _pump_evetypes(self):
        """Mark some hardcoded item types as strong."""
        # Tuple with category IDs of item types we want to keep
        strong_category_ids = (
            TypeCategoryId.charge,
            TypeCategoryId.drone,
            TypeCategoryId.fighter,
            TypeCategoryId.implant,
            TypeCategoryId.module,
            TypeCategoryId.ship,
            TypeCategoryId.skill,
            TypeCategoryId.subsystem)
        # Set with group IDs of item types we want to keep
        strong_group_ids = {TypeGroupId.character, TypeGroupId.effect_beacon}
        # Go through table data, filling valid groups set according to valid
        # categories
        for datarow in self.data['evegroups']:
            if datarow.get('categoryID') in strong_category_ids:
                strong_group_ids.add(datarow['groupID'])
        rows_to_pump = set()
        for datarow in self.data['evetypes']:
            if datarow.get('groupID') in strong_group_ids:
                rows_to_pump.add(datarow)
        self._pump_data('evetypes', rows_to_pump)

    def _autocleanup(self):
        """Run auto-cleanup"""
        self._kill_weak()
        self._changed = True
        # Cycle as long as we have changes during previous iteration. We need
        # this because contents of even evetypes may change, which, in turn,
        # will need to pull additional data into other tables
        while self._changed is True:
            self._changed = False
            self._reanimate_auxiliary_friends()
            self._reestablish_broken_relationships()

    def _kill_weak(self):
        """Trash all data which isn't marked as strong."""
        for table_name, table in self.data.items():
            to_trash = set()
            strong_rows = self.strong_data.get(table_name, set())
            to_trash.update(table.difference(strong_rows))
            self._trash_data(table_name, to_trash)

    def _reanimate_auxiliary_friends(self):
        """Move auxiliary rows from trash into actual data.

        Restore rows in tables, which complement evetypes or serve as m:n
        mapping between evetypes and other tables.
        """
        # As we filter whole database using evetypes table, gather type IDs we
        # currently have in there
        type_ids = {row['typeID'] for row in self.data['evetypes']}
        # Auxiliary tables are those which do not define any entities, they just
        # map one entities to others or complement entities with additional data
        aux_tables = ('dgmtypeattribs', 'dgmtypeeffects', 'typefighterabils')
        for table_name in aux_tables:
            to_restore = set()
            # Restore rows which map other entities to types
            for row in self.trashed_data[table_name]:
                if row['typeID'] in type_ids:
                    to_restore.add(row)
            if to_restore:
                self._changed = True
                self._restore_data(table_name, to_restore)

    def _reestablish_broken_relationships(self):
        """Restore all trashed rows which are referenced from actual data."""
        # Container for 'target data', matches with which are going to be
        # restored
        # Format: {(target table name, target column name): {values to have}}}
        tgt_data = {}
        self._get_tgts_relational(tgt_data)
        self._get_tgts_modinfo(tgt_data)
        self._get_tgts_attr_autocharge(tgt_data)
        self._get_tgts_attr_buff(tgt_data)
        self._get_tgts_buff(tgt_data)
        # Now, when we have all the target data values, we may look for rows,
        # which have matching values, and restore them
        for tgt_spec, tgt_values in tgt_data.items():
            tgt_table_name, tgt_column_name = tgt_spec
            to_restore = set()
            for row in self.trashed_data[tgt_table_name]:
                if row.get(tgt_column_name) in tgt_values:
                    to_restore.add(row)
            if to_restore:
                self._changed = True
                self._restore_data(tgt_table_name, to_restore)

    def _get_tgts_relational(self, tgt_data):
        """Find out which data relationally is referenced from actual data.

        In this method, we get only references defined in 'relational' format,
        that is, references defined as foreign keys. Foreign keys scheme is
        hardcoded in this method and needs to be updated if it changes.

        Args:
            tgt_data: Dictionary which will be filled during the process. Its
                contents should specify target field and which values this field
                should have.
        """
        # Format: {source table: {source column: (target table, target column)}}
        foreign_keys = {
            'dgmattribs': {
                'maxAttributeID': ('dgmattribs', 'attributeID')},
            'dgmeffects': {
                'durationAttributeID': ('dgmattribs', 'attributeID'),
                'trackingSpeedAttributeID': ('dgmattribs', 'attributeID'),
                'dischargeAttributeID': ('dgmattribs', 'attributeID'),
                'rangeAttributeID': ('dgmattribs', 'attributeID'),
                'falloffAttributeID': ('dgmattribs', 'attributeID'),
                'fittingUsageChanceAttributeID': ('dgmattribs', 'attributeID'),
                'resistanceID': ('dgmattribs', 'attributeID')},
            'dgmtypeattribs': {
                'typeID': ('evetypes', 'typeID'),
                'attributeID': ('dgmattribs', 'attributeID')},
            'dgmtypeeffects': {
                'typeID': ('evetypes', 'typeID'),
                'effectID': ('dgmeffects', 'effectID')},
            'evetypes': {
                'groupID': ('evegroups', 'groupID')},
            'typefighterabils': {
                'typeID': ('evetypes', 'typeID')}}
        for src_table_name, table_fks in foreign_keys.items():
            for src_column_name, fk_tgt in table_fks.items():
                tgt_table_name, tgt_column_name = fk_tgt
                for row in self.data[src_table_name]:
                    fk_value = row.get(src_column_name)
                    # If there's no such field in a row or it is None, this is
                    # not a valid FK reference
                    if fk_value is None:
                        continue
                    tgt_spec = (tgt_table_name, tgt_column_name)
                    tgt_data.setdefault(tgt_spec, set()).add(fk_value)

    def _get_tgts_modinfo(self, tgt_data):
        """Find out which data is referenced from modinfo in actual data.

        Method knows where to look for modinfo data and which references it
        contains. If modinfo data format is somehow changed, this method also
        needs to be updated.

        Args:
            tgt_data: Dictionary which will be filled during the process. Its
                contents should specify target field and which values this field
                should have.
        """
        modinfo_relations = self._modinfo_relations()
        for effect_row in self.data['dgmeffects']:
            effect_id = effect_row['effectID']
            try:
                relations = modinfo_relations[effect_id]
            except KeyError:
                continue
            type_ids, group_ids, attr_ids = relations
            for references, tgt_table_name, tgt_column_name in (
                (type_ids, 'evetypes', 'typeID'),
                (group_ids, 'evegroups', 'groupID'),
                (attr_ids, 'dgmattribs', 'attributeID')
            ):
                # If there're any references for given entity, add them to
                # dictionary
                if references:
                    tgt_spec = (tgt_table_name, tgt_column_name)
                    tgt_data.setdefault(tgt_spec, set()).update(references)

    def _modinfo_relations(self):
        """Helper method for modinfo reference getter.

        Generates auxiliary map to avoid re-parsing YAML on each cleanup cycle.

        Returns:
            Dictionary in {effect ID: ({type IDs}, {group IDs}, {attribute
            IDs})} format.
        """

        # Helper function to fetch actual attribute values from modinfo dicts
        def add_entity(mod_info, attr_name, entities):
            try:
                entity_id = mod_info[attr_name]
            except KeyError:
                pass
            else:
                entities.add(entity_id)

        # Format: {effect ID: ({type IDs}, {group IDs}, {attribute IDs})}
        relations = {}
        # Cycle through both data and trashed data, to make sure all rows are
        # processed regardless of stage during which this property is accessed
        for effect_row in chain(
            self.data['dgmeffects'],
            self.trashed_data['dgmeffects']
        ):
            # We do not need anything here if modifier info is empty
            mod_infos = effect_row.get('modifierInfo')
            if not mod_infos:
                continue
            # Modifier infos should be basic python iterable
            if not isinstance(mod_infos, Iterable):
                continue
            type_ids = set()
            group_ids = set()
            attr_ids = set()
            # Fill in sets with IDs from each modifier info dict
            for mod_info in mod_infos:
                add_entity(mod_info, 'skillTypeID', type_ids)
                add_entity(mod_info, 'groupID', group_ids)
                add_entity(mod_info, 'modifyingAttributeID', attr_ids)
                add_entity(mod_info, 'modifiedAttributeID', attr_ids)
            # If all of the sets are empty, do not add anything to primary
            # container
            if not type_ids and not group_ids and not attr_ids:
                continue
            # Otherwise, add all the data we've gathered for current effect to
            # container
            relations[effect_row['effectID']] = (type_ids, group_ids, attr_ids)
        return relations

    def _get_tgts_attr_autocharge(self, tgt_data):
        """Find out which types are referred via 'ammo loaded' attributes.

        Some item types specify which ammo is loaded into them, and here we
        ensure these ammo types are kept.

        Args:
            tgt_data: Dictionary which will be filled during the process. Its
                contents should specify target field and which values this field
                should have.
        """
        for row in self.data['dgmtypeattribs']:
            if row['attributeID'] not in (
                AttrId.ammo_loaded,
                AttrId.fighter_ability_launch_bomb_type
            ):
                continue
            value = row.get('value')
            try:
                ammo_type_id = int(value)
            except TypeError:
                continue
            tgt_spec = ('evetypes', 'typeID')
            tgt_data.setdefault(tgt_spec, set()).add(ammo_type_id)

    def _get_tgts_attr_buff(self, tgt_data):
        """Find out which warfare buffs are referenced from item types we keep.

        Args:
            tgt_data: Dictionary which will be filled during the process. Its
                contents should specify target field and which values this field
                should have.
        """
        for row in self.data['dgmtypeattribs']:
            if row['attributeID'] not in (
                AttrId.warfare_buff_1_id,
                AttrId.warfare_buff_2_id,
                AttrId.warfare_buff_3_id,
                AttrId.warfare_buff_4_id
            ):
                continue
            value = row.get('value')
            try:
                buff_id = int(value)
            except TypeError:
                continue
            tgt_spec = ('dbuffcollections', 'buffID')
            tgt_data.setdefault(tgt_spec, set()).add(buff_id)

    def _get_tgts_buff(self, tgt_data):
        """Find out which entities are used in warfare buff data.

        Args:
            tgt_data: Dictionary which will be filled during the process. Its
                contents should specify target field and which values this field
                should have.
        """
        def add_attr(mod_row):
            attr_id = mod_row.get('dogmaAttributeID')
            if attr_id is not None:
                tgt_spec = ('dgmattribs', 'attributeID')
                tgt_data.setdefault(tgt_spec, set()).add(attr_id)

        def add_group(mod_row):
            group_id = mod_row.get('groupID')
            if group_id is not None:
                tgt_spec = ('evegroups', 'groupID')
                tgt_data.setdefault(tgt_spec, set()).add(group_id)

        def add_type(mod_row):
            type_id = mod_row.get('skillID')
            if type_id is not None:
                tgt_spec = ('evetypes', 'typeID')
                tgt_data.setdefault(tgt_spec, set()).add(type_id)

        for row in self.data['dbuffcollections']:
            for mod_row in row.get('itemModifiers', ()):
                add_attr(mod_row)
            for mod_row in row.get('locationModifiers', ()):
                add_attr(mod_row)
            for mod_row in row.get('locationGroupModifiers', ()):
                add_attr(mod_row)
                add_group(mod_row)
            for mod_row in row.get('locationRequiredSkillModifiers', ()):
                add_attr(mod_row)
                add_type(mod_row)

    def _report_results(self):
        """Log cleanup results."""
        table_msgs = []
        for table_name in sorted(self.data):
            data_len = len(self.data[table_name])
            trashed_len = len(self.trashed_data[table_name])
            try:
                ratio = trashed_len / (data_len + trashed_len)
            # Skip results if table was empty
            except ZeroDivisionError:
                continue
            table_msgs.append('{:.1%} from {}'.format(ratio, table_name))
        if table_msgs:
            msg = 'cleaned: {}'.format(', '.join(table_msgs))
            logger.info(msg)

    def _pump_data(self, table_name, rows):
        """Mark data rows as strong.

        Rows marked as strong are immune to removal.

        Args:
            table_name: Name of a table where data for marking resides.
            rows: iterable with data rows from the table.
        """
        self.strong_data.setdefault(table_name, set()).update(rows)

    def _trash_data(self, table_name, rows):
        """Move data rows into trash.

        Data is moved into trash with ability to be restored later, if needed.

        Args:
            table_name: Name of a table where data for marking resides.
            rows: iterable with data rows from the table.
        """
        data_table = self.data[table_name]
        trash_table = self.trashed_data.setdefault(table_name, set())
        trash_table.update(rows)
        data_table.difference_update(rows)

    def _restore_data(self, table_name, rows):
        """Restore data rows from trash into actual data.

        Args:
            table_name: Name of a table where data for marking resides.
            rows: iterable with data rows from the table.
        """
        data_table = self.data[table_name]
        trash_table = self.trashed_data[table_name]
        data_table.update(rows)
        trash_table.difference_update(rows)
