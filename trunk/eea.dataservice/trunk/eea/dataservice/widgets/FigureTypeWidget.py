# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget
from zope.interface import alsoProvides, directlyProvides, directlyProvidedBy

from eea.dataservice.interfaces import *


class FigureTypeWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'format': "flex", # possible values: flex, select, radio
        'macro' : "widgets/selection",
        })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """Basic impl for form processing in a widget"""

        value = form.get(field.getName(), empty_marker)
        old_value = instance.getFigureType()

        if value == 'map':
            alsoProvides(instance, IEEAFigureMap)
        elif value == 'graph':
            alsoProvides(instance, IEEAFigureGraph)
        elif value == 'table':
            alsoProvides(instance, IEEAFigureTable)

        if old_value == 'map':
            directlyProvides(instance, directlyProvidedBy(instance)-IEEAFigureMap)
        elif old_value == 'graph':
            directlyProvides(instance, directlyProvidedBy(instance)-IEEAFigureGraph)
        elif old_value == 'table':
            directlyProvides(instance, directlyProvidedBy(instance)-IEEAFigureTable)

        if value is empty_marker:
            return empty_marker
        if emptyReturnsMarker and value == '':
            return empty_marker
        return value, {}

registerWidget(FigureTypeWidget,
               title='EEA Fugure Type',
               description=('EEA Figure Type description.'),
               used_for=('Products.Archetypes.Field.StringField',
                         'Products.Archetypes.Field.LinesField',)
               )