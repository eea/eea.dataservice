""" Fields
"""
from Products.Archetypes.Registry import registerField
from eea.dataservice.fields.GeoQualityField import GeoQualityField
from eea.dataservice.fields.OrganisationField import OrganisationField

def register():
    """ Register custom fields
    """
    registerField(GeoQualityField, title=u'Geo Quality Field')
    registerField(OrganisationField, title=u'Organisation Field')
