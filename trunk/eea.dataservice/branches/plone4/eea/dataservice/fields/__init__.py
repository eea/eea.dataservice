""" Fields
"""
from Products.Archetypes.Registry import registerField
from eea.dataservice.fields.ManagementPlanField import ManagementPlanField
from eea.dataservice.fields.GeoQualityField import GeoQualityField
from eea.dataservice.fields.OrganisationField import OrganisationField

def register():
    """ Register custom fields
    """
    registerField(ManagementPlanField, title=u'Management Plan Field')
    registerField(GeoQualityField, title=u'Geo Quality Field')
    registerField(OrganisationField, title=u'Organisation Field')
