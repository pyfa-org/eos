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


import logging
from unittest.mock import patch

from tests.cache_generator.generator_testcase import GeneratorTestCase


@patch('eos.data.cache_generator.converter.ModifierBuilder')
class TestConversionModifier(GeneratorTestCase):
    """
    As modifiers generated by modifier builder have custom
    processing in converter, we have to test it too.
    """

    def test_fields(self, mod_builder):
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 111})
        self.dh.data['dgmeffects'].append({
            'effectID': 111, 'preExpression': 1,
            'postExpression': 11, 'effectCategory': 111,
            'modifierInfo': 'YAML stuff'
        })
        mod = self.mod(
            tgt_filter=3, tgt_domain=4, tgt_filter_extra_arg=5,
            tgt_attr=6, operator=7, src_attr=8
        )
        mod_builder.return_value.build.return_value = ([mod], 0)
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        idzing_stats = self.log[0]
        self.assertEqual(idzing_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(idzing_stats.levelno, logging.WARNING)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(len(data['modifiers']), 1)
        self.assertIn(1, data['modifiers'])
        expected = {
            'modifier_id': 1, 'tgt_filter': 3, 'tgt_domain': 4, 'tgt_filter_extra_arg': 5,
            'tgt_attr': 6, 'operator': 7, 'src_attr': 8
        }
        self.assertEqual(data['modifiers'][1], expected)
        self.assertIn(111, data['effects'])
        modifiers = data['effects'][111]['modifiers']
        self.assertEqual(modifiers, [1])

    def test_numbering_single_effect(self, mod_builder):
        # Check how multiple modifiers generated out of single effect are numbered
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 111})
        self.dh.data['dgmeffects'].append({
            'effectID': 111, 'preExpression': 21,
            'postExpression': 21, 'effectCategory': 21,
            'modifierInfo': 'YAML stuff'
        })
        mod1 = self.mod(
            tgt_filter=30, tgt_domain=40, tgt_filter_extra_arg=50,
            tgt_attr=60, operator=70, src_attr=80
        )
        mod2 = self.mod(
            tgt_filter=300, tgt_domain=400, tgt_filter_extra_arg=500,
            tgt_attr=600, operator=700, src_attr=800
        )
        mod_builder.return_value.build.return_value = ([mod1, mod2], 0)
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        idzing_stats = self.log[0]
        self.assertEqual(idzing_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(idzing_stats.levelno, logging.WARNING)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(len(data['modifiers']), 2)
        self.assertIn(1, data['modifiers'])
        expected = {
            'modifier_id': 1, 'tgt_filter': 30, 'tgt_domain': 40, 'tgt_filter_extra_arg': 50,
            'tgt_attr': 60, 'operator': 70, 'src_attr': 80
        }
        self.assertEqual(data['modifiers'][1], expected)
        self.assertIn(2, data['modifiers'])
        expected = {
            'modifier_id': 2, 'tgt_filter': 300, 'tgt_domain': 400, 'tgt_filter_extra_arg': 500,
            'tgt_attr': 600, 'operator': 700, 'src_attr': 800
        }
        self.assertEqual(data['modifiers'][2], expected)
        self.assertIn(111, data['effects'])
        modifiers = data['effects'][111]['modifiers']
        self.assertEqual(sorted(modifiers), [1, 2])

    def test_numbering_multiple_effects(self, mod_builder):
        # Check how multiple modifiers generated out of two effects are numbered
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 333})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 444})
        self.dh.data['dgmeffects'].append({
            'effectID': 333, 'preExpression': 1,
            'postExpression': 11, 'effectCategory': 111,
            'modifierInfo': 'YAML stuff'
        })
        self.dh.data['dgmeffects'].append({
            'effectID': 444, 'preExpression': 111,
            'postExpression': 1, 'effectCategory': 111,
            'modifierInfo': 'YAML stuff'
        })
        mod1 = self.mod(
            tgt_filter=3, tgt_domain=4, tgt_filter_extra_arg=5,
            tgt_attr=6, operator=7, src_attr=8
        )
        mod2 = self.mod(
            tgt_filter=33, tgt_domain=44, tgt_filter_extra_arg=55,
            tgt_attr=66, operator=77, src_attr=88
        )
        arg_map = {333: mod1, 444: mod2}
        mod_builder.return_value.build.side_effect = lambda eff_row: ([arg_map[eff_row['effect_id']]], 0)
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        idzing_stats = self.log[0]
        self.assertEqual(idzing_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(idzing_stats.levelno, logging.WARNING)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(len(data['modifiers']), 2)
        self.assertIn(1, data['modifiers'])
        expected = {
            'modifier_id': 1, 'tgt_filter': 3, 'tgt_domain': 4, 'tgt_filter_extra_arg': 5,
            'tgt_attr': 6, 'operator': 7, 'src_attr': 8
        }
        self.assertEqual(data['modifiers'][1], expected)
        self.assertIn(2, data['modifiers'])
        expected = {
            'modifier_id': 2, 'tgt_filter': 33, 'tgt_domain': 44, 'tgt_filter_extra_arg': 55,
            'tgt_attr': 66, 'operator': 77, 'src_attr': 88
        }
        self.assertEqual(data['modifiers'][2], expected)
        self.assertIn(333, data['effects'])
        modifiers = data['effects'][333]['modifiers']
        self.assertEqual(modifiers, [1])
        self.assertIn(444, data['effects'])
        modifiers = data['effects'][444]['modifiers']
        self.assertEqual(modifiers, [2])

    def test_merge_single_effect(self, mod_builder):
        # Check that if modifiers with the same values are generated on single effect,
        # they're assigned to single identifier and it is listed twice in list of
        # modifiers
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 111})
        self.dh.data['dgmeffects'].append({
            'effectID': 111, 'preExpression': 22,
            'postExpression': 22, 'effectCategory': 22,
            'modifierInfo': 'YAML stuff'
        })
        mod1 = self.mod(
            tgt_filter=43, tgt_domain=54, tgt_filter_extra_arg=65,
            tgt_attr=76, operator=87, src_attr=98
        )
        mod2 = self.mod(
            tgt_filter=43, tgt_domain=54, tgt_filter_extra_arg=65,
            tgt_attr=76, operator=87, src_attr=98
        )
        mod_builder.return_value.build.return_value = ([mod1, mod2], 0)
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        idzing_stats = self.log[0]
        self.assertEqual(idzing_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(idzing_stats.levelno, logging.WARNING)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(len(data['modifiers']), 1)
        self.assertIn(1, data['modifiers'])
        expected = {
            'modifier_id': 1, 'tgt_filter': 43, 'tgt_domain': 54, 'tgt_filter_extra_arg': 65,
            'tgt_attr': 76, 'operator': 87, 'src_attr': 98
        }
        self.assertEqual(data['modifiers'][1], expected)
        self.assertIn(111, data['effects'])
        modifiers = data['effects'][111]['modifiers']
        self.assertEqual(modifiers, [1, 1])

    def test_merge_multiple_effects(self, mod_builder):
        # Check that if modifiers with the same values are generated on multiple effects,
        # they're assigned to single identifier
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 333})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 444})
        self.dh.data['dgmeffects'].append({
            'effectID': 333, 'preExpression': 1,
            'postExpression': 11, 'effectCategory': 111,
            'modifierInfo': 'YAML stuff'
        })
        self.dh.data['dgmeffects'].append({
            'effectID': 444, 'preExpression': 111,
            'postExpression': 11, 'effectCategory': 1,
            'modifierInfo': 'YAML stuff'
        })
        mod1 = self.mod(
            tgt_filter=3, tgt_domain=4, tgt_filter_extra_arg=5,
            tgt_attr=6, operator=7, src_attr=8
        )
        mod2 = self.mod(
            tgt_filter=3, tgt_domain=4, tgt_filter_extra_arg=5,
            tgt_attr=6, operator=7, src_attr=8
        )
        arg_map = {333: mod1, 444: mod2}
        mod_builder.return_value.build.side_effect = lambda eff_row: ([arg_map[eff_row['effect_id']]], 0)
        data = self.run_generator()
        self.assertEqual(len(self.log), 2)
        idzing_stats = self.log[0]
        self.assertEqual(idzing_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(idzing_stats.levelno, logging.WARNING)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        self.assertEqual(len(data['modifiers']), 1)
        self.assertIn(1, data['modifiers'])
        expected = {
            'modifier_id': 1, 'tgt_filter': 3, 'tgt_domain': 4, 'tgt_filter_extra_arg': 5,
            'tgt_attr': 6, 'operator': 7, 'src_attr': 8
        }
        self.assertEqual(data['modifiers'][1], expected)
        self.assertIn(333, data['effects'])
        modifiers = data['effects'][333]['modifiers']
        self.assertEqual(modifiers, [1])
        self.assertIn(333, data['effects'])
        modifiers = data['effects'][333]['modifiers']
        self.assertEqual(modifiers, [1])
        self.assertIn(444, data['effects'])
        modifiers = data['effects'][444]['modifiers']
        self.assertEqual(modifiers, [1])

    def test_builder_usage(self, mod_builder):
        # Check that modifier builder is properly used
        self.dh.data['evetypes'].append({'typeID': 1, 'groupID': 1, 'typeName_en-us': ''})
        self.dh.data['dgmtypeeffects'].append({'typeID': 1, 'effectID': 111})
        self.dh.data['dgmeffects'].append({
            'effectID': 111, 'preExpression': 56, 'postExpression': 107,
            'effectCategory': 108, 'modifierInfo': 'some YAML'
        })
        self.dh.data['dgmexpressions'].append({
            'expressionID': 107, 'operandID': None, 'arg1': None, 'arg2': None,
            'expressionValue': None, 'expressionTypeID': None,
            'expressionGroupID': None, 'expressionAttributeID': None
        })
        self.dh.data['dgmexpressions'].append({
            'expressionID': 56, 'operandID': None, 'arg1': None, 'arg2': None,
            'expressionValue': None, 'expressionTypeID': None,
            'expressionGroupID': None, 'expressionAttributeID': None
        })
        builder_args = []
        self._setup_args_capture(mod_builder.return_value.build, builder_args)
        mod_builder.return_value.build.return_value = ([], 0)
        self.run_generator()
        self.assertEqual(len(self.log), 2)
        idzing_stats = self.log[0]
        self.assertEqual(idzing_stats.name, 'eos.data.cache_generator.converter')
        self.assertEqual(idzing_stats.levelno, logging.WARNING)
        clean_stats = self.log[1]
        self.assertEqual(clean_stats.name, 'eos.data.cache_generator.cleaner')
        self.assertEqual(clean_stats.levelno, logging.INFO)
        call1, call2 = mod_builder.mock_calls
        # Check initialization
        name, args, kwargs = call1
        self.assertEqual(name, '')
        self.assertEqual(len(args), 1)
        self.assertEqual(len(kwargs), 0)
        expressions = args[0]
        # Expression order isn't stable in passed list, so verify
        # passed argument using membership check
        self.assertEqual(len(expressions), 2)
        expression_ids = set(row['expressionID'] for row in expressions)
        self.assertEqual(expression_ids, {56, 107})
        # Check request for building
        name, _, _ = call2
        self.assertEqual(len(builder_args), 1)
        args, kwargs = builder_args[0]
        self.assertEqual(name, '().build')
        self.assertEqual(len(args), 1)
        self.assertEqual(len(kwargs), 0)
        expected = {
            'effect_id': 111,
            'pre_expression': 56,
            'post_expression': 107,
            'effect_category': 108,
            'modifier_info': 'some YAML'
        }
        # Filter out fields we do not want to check
        actual = dict((k, args[0][k]) for k in filter(lambda k: k in expected, args[0]))
        self.assertEqual(actual, expected)
