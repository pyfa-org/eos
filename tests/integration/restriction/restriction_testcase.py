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


from eos import ValidationError
from eos.const.eos import Restriction
from tests.integration.integration_testcase import IntegrationTestCase


class RestrictionTestCase(IntegrationTestCase):
    """
    Additional functionality provided:

    self.get_restriction_error -- get restriction error for passed
        item of passed restriction type. If no error occurred,
        return None
    """

    def get_restriction_error(self, fit, item, restriction):
        skip_checks = set(Restriction).difference([restriction])
        try:
            fit.validate(skip_checks)
        except ValidationError as e:
            error_data = e.args[0]
            if item not in error_data:
                return None
            item_error = error_data[item]
            if restriction not in item_error:
                return None
            return item_error[restriction]
        else:
            return None
