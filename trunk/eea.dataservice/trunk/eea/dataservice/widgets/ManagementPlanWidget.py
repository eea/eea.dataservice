# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget


class ManagementPlanWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'format': "flex", # possible values: flex, select, radio
        'macro' : "management_plan_widget",
        })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker='',
                     emptyReturnsMarker=False, validating=True):
        """ process form """
        name = field.getName()
        mp_year = form.get('%sYear' % name, None)
        mp_code = form.get('%sCode' % name, None)

        if mp_year is None or mp_code is None:
            return empty_marker

        return (mp_year, mp_code), {}

registerWidget(ManagementPlanWidget,
               title='EEA Management Plan Code',
               description=('Renders a HTML selection widget, to'
                            ' allow you enter the year and the'
                            ' EEA management plan code'),
               used_for=('eea.dataservice.fields.ManagementPlanField.ManagementPlanField')
               )