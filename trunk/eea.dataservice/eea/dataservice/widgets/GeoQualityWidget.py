# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget


class GeoQualityWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'format': "flex", # possible values: flex, select, radio
        'macro' : "quality_widget",
        })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker='',
                     emptyReturnsMarker=False, validating=True):
        """ process form """
        name = field.getName()
        #mp_year = form.get('%sYear' % name, None)
        #mp_code = form.get('%sCode' % name, None)

        #if not (mp_year or mp_code):
        #    return empty_marker

        #return (mp_year, mp_code), {}
        return ('', '', '', '', ''), {}

registerWidget(GeoQualityWidget,
               title='Geographic information quality',
               description=('Geographic information quality label.'),
               used_for=('eea.dataservice.fields.GeoQualityField.GeoQualityField')
               )