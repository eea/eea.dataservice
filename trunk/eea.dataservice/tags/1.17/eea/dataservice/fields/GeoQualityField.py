# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from Products.Archetypes.atapi import ObjectField, StringField
from Products.Archetypes.Field import decode, encode


class GeoQualityField(StringField):
    """ Save geographic information quality data
    """

    def set(self, instance, value, **kwargs):
        """
        Set geographic information quality data
        """
        ObjectField.set(self, instance, value, **kwargs)

    def get(self, instance, **kwargs):
        """
        Get geographic information quality data
        """
        value = ObjectField.get(self, instance, **kwargs) or ()
        data = [encode(v, instance, **kwargs) for v in value]
        return tuple(data)
