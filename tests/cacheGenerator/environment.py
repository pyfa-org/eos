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


from eos.eve.modifier import Modifier


class DataHandler:

    def __init__(self):
        self.data = {'invtypes': [],
                     'invgroups': [],
                     'dgmattribs': [],
                     'dgmtypeattribs': [],
                     'dgmeffects': [],
                     'dgmtypeeffects': [],
                     'dgmexpressions': []}

    def getInvtypes(self):
        return self.data['invtypes']

    def getInvgroups(self):
        return self.data['invgroups']

    def getDgmattribs(self):
        return self.data['dgmattribs']

    def getDgmtypeattribs(self):
        return self.data['dgmtypeattribs']

    def getDgmeffects(self):
        return self.data['dgmeffects']

    def getDgmtypeeffects(self):
        return self.data['dgmtypeeffects']

    def getDgmexpressions(self):
        return self.data['dgmexpressions']


class ModifierBuilder:

    def __init__(self, expressions, logger):
        self.exps = expressions
        self.logger =  logger

    def buildEffect(self, preExpressionId, postExpressionId, effectCategoryId):
        args = (preExpressionId, postExpressionId, effectCategoryId)
        modifiers = []
        buildStatus = 0
        # Generate single modifier
        if args == (500, 600, 700) or args == (200, 400, 800):
            modifier = Modifier(state=2, context=3, sourceAttributeId=4, operator=5,
                                targetAttributeId=6, location=7, filterType=8, filterValue=9)
            modifiers.append(modifier)
            buildStatus = 29
        if args == (555, 666, 777):
            modifier1 = Modifier(state=32, context=43, sourceAttributeId=54, operator=65,
                                 targetAttributeId=76, location=87, filterType=98, filterValue=90)
            modifiers.append(modifier1)
            modifier2 = Modifier(state=32, context=43, sourceAttributeId=54, operator=65,
                                 targetAttributeId=76, location=87, filterType=98, filterValue=90)
            modifiers.append(modifier2)
        # Generate another single modifier
        elif args == (100, 200, 300):
            modifier = Modifier(state=22, context=33, sourceAttributeId=44, operator=55,
                                targetAttributeId=66, location=77, filterType=88, filterValue=99)
            modifiers.append(modifier)
        # Generate multiple modifiers
        elif args == (5000, 6000, 7000):
            modifier1 = Modifier(state=20, context=30, sourceAttributeId=40, operator=50,
                                targetAttributeId=60, location=70, filterType=80, filterValue=90)
            modifiers.append(modifier1)
            modifier2 = Modifier(state=200, context=300, sourceAttributeId=400, operator=500,
                                targetAttributeId=600, location=700, filterType=800, filterValue=900)
            modifiers.append(modifier2)
        # Check passed expressions, result is detectable by build status
        elif args == (700, 800, None):
            expected1 = {'expressionId': 800, 'operandId': 6, 'arg1Id': 1009, 'arg2Id': 15,
                         'expressionValue': None, 'expressionTypeId': 502,
                         'expressionGroupId': 451, 'expressionAttributeId': 90}
            expected2 = {'expressionId': 700, 'operandId': 33, 'arg1Id': 5007, 'arg2Id': 66,
                         'expressionValue': 'Kurr', 'expressionTypeId': 551,
                         'expressionGroupId': 567, 'expressionAttributeId': 102}
            if len(self.exps) == 2 and expected1 in self.exps and expected2 in self.exps:
                buildStatus = 8000
        elif args == (100, 101, 8888):
            expected1 = {'expressionId': 100, 'operandId': 6, 'arg1Id': 102, 'arg2Id': 103,
                         'expressionValue': None, 'expressionTypeId': 2,
                         'expressionGroupId': 500, 'expressionAttributeId': 1007}
            expected2 = {'expressionId': 101, 'operandId': 6, 'arg1Id': 102, 'arg2Id': 103,
                         'expressionValue': None, 'expressionTypeId': None,
                         'expressionGroupId': None, 'expressionAttributeId': None}
            expected3 = {'expressionId': 102, 'operandId': 6, 'arg1Id': None, 'arg2Id': None,
                         'expressionValue': None, 'expressionTypeId': None,
                         'expressionGroupId': None, 'expressionAttributeId': None}
            expected4 = {'expressionId': 103, 'operandId': 6, 'arg1Id': None, 'arg2Id': None,
                         'expressionValue': None, 'expressionTypeId': None,
                         'expressionGroupId': None, 'expressionAttributeId': None}
            if (len(self.exps) == 4 and expected1 in self.exps and expected2 in self.exps
                and expected3 in self.exps and expected4 in self.exps):
                buildStatus = 8888
        elif args == (101, None, 8888):
            expected = {'expressionId': 101, 'operandId': 6, 'arg1Id': None, 'arg2Id': None,
                        'expressionValue': None, 'expressionTypeId': 2,
                        'expressionGroupId': None, 'expressionAttributeId': None}
            if len(self.exps) == 1 and expected in self.exps:
                buildStatus = 7777
        elif args == (123, 456, 789):
            expected = {'expressionId': 456, 'operandId': 75, 'arg1Id': 1009, 'arg2Id': 15,
                        'expressionValue': None, 'expressionTypeId': 502,
                        'expressionGroupId': 451, 'expressionAttributeId': 90}
            if len(self.exps) == 1 and expected in self.exps:
                buildStatus = 888
        # Used to check that proper logger is passed to modifier builder
        elif args == (555, 555, 555):
            self.logger.warning('modbuilder warning', childName='modifierBuilder')
        return modifiers, buildStatus
