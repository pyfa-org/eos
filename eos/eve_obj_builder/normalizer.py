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


from logging import getLogger

from eos.const.eve import AttrId
from eos.const.eve import TypeGroupId
from eos.util.frozendict import frozendict


logger = getLogger(__name__)


class Normalizer:

    @classmethod
    def run(cls, data):
        """Normalize passed data.

        Data provided by data handler has been (deliberately) denormalized by
        CCP due to unknown reasons. As we do not care about reasons, normalize
        data for easier and hack-free code in other parts of Eos.

        Args:
            data: Dictionary in {table name: {table, rows}} format.
        """
        cls._move_attrs(data)

    @staticmethod
    def _move_attrs(data):
        """Normalize attribute value definitions.

        Some of item type attributes are defined in evetypes table. We do not
        need them there, for data consistency it's worth to move them to
        dgmtypeattribs table, where the rest of attributes are defined.

        Args:
            data: Dictionary in {table name: {table, rows}} format.
        """
        attr_map = {
            'radius': AttrId.radius,
            'mass': AttrId.mass,
            'volume': AttrId.volume,
            'capacity': AttrId.capacity}
        attr_ids = tuple(attr_map.values())
        # Here we will store pairs (typeID, attrID) already defined in
        # dgmtypeattribs
        defined_pairs = set()
        dgmtypeattribs = data['dgmtypeattribs']
        for row in dgmtypeattribs:
            if row['attributeID'] not in attr_ids:
                continue
            defined_pairs.add((row['typeID'], row['attributeID']))
        attrs_skipped = 0
        for row in data['evetypes']:
            type_id = row['typeID']
            for field, value in row.items():
                if field in attr_map:
                    # If row didn't have such attribute defined, skip it
                    if value is None:
                        continue
                    # If such attribute already exists in dgmtypeattribs, do not
                    # modify it - values from dgmtypeattribs table have priority
                    attr_id = attr_map[field]
                    if (type_id, attr_id) in defined_pairs:
                        attrs_skipped += 1
                        continue
                    # Generate row and add it to proper attribute table
                    dgmtypeattribs.add(frozendict({
                        'typeID': type_id,
                        'attributeID': attr_id,
                        'value': value}))
        if attrs_skipped:
            msg = (
                '{} built-in attributes already have had value '
                'in dgmtypeattribs and were skipped'
            ).format(attrs_skipped)
            logger.warning(msg)
