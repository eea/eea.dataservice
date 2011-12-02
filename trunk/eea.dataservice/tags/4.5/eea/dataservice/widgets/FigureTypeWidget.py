""" Figure type
"""
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import TypesWidget
from zope.interface import alsoProvides, directlyProvides, directlyProvidedBy
from eea.dataservice import interfaces

class FigureTypeWidget(TypesWidget):
    """ Figure Type Widget
    """
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'format': "flex", # possible values: flex, select, radio
        'macro' : "widgets/selection",
        })

    security = ClassSecurityInfo()

    def getName(self):
        return "SelectionWidget"

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """Basic impl for form processing in a widget"""

        value = form.get(field.getName(), empty_marker)
        old_value = instance.getFigureType()

        if old_value == 'map':
            directlyProvides(instance,
                directlyProvidedBy(instance)-interfaces.IEEAFigureMap)
        elif old_value == 'graph':
            directlyProvides(instance,
                directlyProvidedBy(instance)-interfaces.IEEAFigureGraph)
        elif old_value == 'table':
            directlyProvides(instance,
                directlyProvidedBy(instance)-interfaces.IEEAFigureTable)

        if value == 'map':
            alsoProvides(instance, interfaces.IEEAFigureMap)
        elif value == 'graph':
            alsoProvides(instance, interfaces.IEEAFigureGraph)
        elif value == 'table':
            alsoProvides(instance, interfaces.IEEAFigureTable)

        if value is empty_marker:
            return empty_marker
        if emptyReturnsMarker and value == '':
            return empty_marker
        return value, {}
