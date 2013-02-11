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

# Container for expressions passed to modifier builder,
# necessary to make them accessible by tests
builderExpressions = []

class ModifierBuilder:

    def __init__(self, expressions, logger):
        builderExpressions.clear()
        for expression in expressions:
            builderExpressions.append(expression)
        self.logger =  logger

    def buildEffect(self, preExpressionId, postExpressionId, effectCategoryId):
        args = (preExpressionId, postExpressionId, effectCategoryId)
        modifiers = []
        buildStatus = 0
        # Generate single modifier
        if args in ((1, 11, 111), (111, 11, 1)):
            modifier = Modifier(state=2, context=3, sourceAttributeId=4, operator=5,
                                targetAttributeId=6, location=7, filterType=8, filterValue=9)
            modifiers.append(modifier)
            buildStatus = 29
        # Generate another single modifier
        elif args == (111, 1, 111):
            modifier = Modifier(state=22, context=33, sourceAttributeId=44, operator=55,
                                targetAttributeId=66, location=77, filterType=88, filterValue=99)
            modifiers.append(modifier)
        # Generate multiple duplicate modifiers
        elif args == (22, 22, 22):
            modifier1 = Modifier(state=32, context=43, sourceAttributeId=54, operator=65,
                                 targetAttributeId=76, location=87, filterType=98, filterValue=90)
            modifiers.append(modifier1)
            modifier2 = Modifier(state=32, context=43, sourceAttributeId=54, operator=65,
                                 targetAttributeId=76, location=87, filterType=98, filterValue=90)
            modifiers.append(modifier2)
        # Generate multiple different modifiers
        elif args == (21, 21, 21):
            modifier1 = Modifier(state=20, context=30, sourceAttributeId=40, operator=50,
                                targetAttributeId=60, location=70, filterType=80, filterValue=90)
            modifiers.append(modifier1)
            modifier2 = Modifier(state=200, context=300, sourceAttributeId=400, operator=500,
                                targetAttributeId=600, location=700, filterType=800, filterValue=900)
            modifiers.append(modifier2)
        # Used to check that proper logger is passed to modifier builder
        elif args == (108, 108, 108):
            self.logger.warning('modbuilder warning', childName='modifierBuilder')
        return modifiers, buildStatus
