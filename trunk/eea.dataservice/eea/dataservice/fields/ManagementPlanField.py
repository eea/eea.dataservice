# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from Products.Archetypes.atapi import ObjectField, StringField
from Products.Archetypes.Field import decode, encode


class ManagementPlanField(StringField):
    """ Save management plan year and code
    """

    def set(self, instance, value, **kwargs):
        """
        Set management plan code and year
        """
        mp_year = value[0]
        mp_code = value[1]
        value = (mp_year, mp_code)
        ObjectField.set(self, instance, value, **kwargs)

    def get(self, instance, **kwargs):
        """
        Get management plan code and year
        """
        value = ObjectField.get(self, instance, **kwargs) or ()
        data = [encode(v, instance, **kwargs) for v in value]
        return tuple(data)
