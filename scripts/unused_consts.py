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


"""Find all defined constants which are not actually used in eos code"""


import ast
import os


class EnumSeeker(ast.NodeVisitor):

    def __init__(self, enums):
        self.enums = enums

    def visit_ClassDef(self, enum_class_node):
        # Check only enums inherited from IntEnum class
        if (
            len(enum_class_node.bases) != 1 or
            not isinstance(enum_class_node.bases[0], ast.Name) or
            enum_class_node.bases[0].id != 'IntEnum'
        ):
            return
        for enum_assignment_node in enum_class_node.body:
            # Only assignments to name are recorded
            if not isinstance(enum_assignment_node, ast.Assign):
                continue
            for enum_item_name_node in enum_assignment_node.targets:
                if not isinstance(enum_item_name_node, ast.Name):
                    continue
                item_names = self.enums.setdefault(enum_class_node.name, set())
                item_names.add(enum_item_name_node.id)


def get_enums(base_path):
    # Format: {enum name: {enum item names}}
    enums = {}
    # Cycle through all .py files in consts directory
    const_path = os.path.join(base_path, 'eos', 'const')
    for dir_path, dirs, files in os.walk(const_path):
        for file in filter(lambda f: os.path.splitext(f)[1] == '.py', files):
            with open(os.path.join(dir_path, file)) as f:
                data = f.read()
            ast_root = ast.parse(data)
            EnumSeeker(enums).visit(ast_root)
    return enums


if __name__ == '__main__':

    script_dir = os.path.dirname(os.path.abspath(__file__))
    eos_dir = os.path.abspath(os.path.join(script_dir, '..'))

    enums = get_enums(eos_dir)
