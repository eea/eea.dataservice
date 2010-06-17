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
        'helper_js': ('quality_widget.js',),
        })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker='',
                     emptyReturnsMarker=False, validating=True):
        """ process form """
        name = field.getName()
        gq_completeness = form.get('%sCom' % name, None)
        gq_logical = form.get('%sLog' % name, None)
        gq_position = form.get('%sPos' % name, None)
        gq_temporal = form.get('%sTem' % name, None)
        gq_thematic = form.get('%sThe' % name, None)



        if not (gq_completeness or gq_logical or gq_position or gq_temporal or gq_thematic):
            return empty_marker

        return (gq_completeness, gq_logical, gq_position, gq_temporal, gq_thematic), {}

registerWidget(GeoQualityWidget,
               title='Geographic information quality',
               description=('Geographic information quality label.'),
               used_for=('eea.dataservice.fields.GeoQualityField.GeoQualityField')
               )