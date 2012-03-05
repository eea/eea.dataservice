""" Fields
"""
from Products.Archetypes.Registry import registerField
from eea.dataservice.fields.OrganisationField import OrganisationField

def register():
    """ Register custom fields
    """
    registerField(OrganisationField, title=u'Organisation Field')
