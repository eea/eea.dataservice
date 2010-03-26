# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from zope.interface import implements
from Products.Archetypes.atapi import *
from Products.CMFCore import permissions
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Field import decode
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema

from eea.dataservice.config import *
from eea.dataservice.interfaces import IOrganisation
from eea.dataservice.fields.OrganisationField import OrganisationField
from eea.locationwidget.locationwidget import LocationWidget


schema = Schema((

    OrganisationField(
        name='organisationUrl',
        languageIndependent=True,
        accessor='org_url',
        validators=(['isURL', 'unique_organisation_url_validator',]),
        required=True,
        widget = StringWidget(
            label="Organisation url",
            description = ("Web address with more info about this organisation. "
                           "Add http:// for external links."),
            label_msgid='dataservice_label_url',
            description_msgid='dataservice_help_url',
            i18n_domain='eea.dataservice',
        )
    ),

    StringField(
        name='location',
        searchable=True,
        widget = LocationWidget(
            description = "Use the address to retrieve the location <em>(e.g. Kongens Nytorv 6, 1050 Copenhagen K, Denmark)</em>",
            description_msgid = "dataservice_help_address",
            label = "Organisation address",
            label_msgid = "dataservice_label_address",
            i18n_domain = "eea.dataservice"
        )
    ),

    TextField(
        name='data_policy',
        searchable=True,
        widget=TextAreaWidget(
            label="Data policy",
            description="Data policy description.",
            label_msgid='dataservice_label_policy',
            description_msgid='dataservice_help_policy',
            i18n_domain='eea.dataservice',
        )
    ),
),
)

Organisation_schema = ATFolderSchema.copy() + schema.copy()

class Organisation(ATFolder):
    """ Organisation Content Type
    """
    implements(IOrganisation)
    security = ClassSecurityInfo()

    archetype_name  = 'Organisation'
    portal_type     = 'Organisation'
    meta_type       = 'Organisation'
    _at_rename_after_creation = True

    schema = Organisation_schema

    # Map view compatibility methods
    security.declareProtected(permissions.View, 'event_url')
    def event_url(self):
        """ """
        field = self.getField('organisationUrl')
        return field.getAccessor(self)()

    security.declareProtected(permissions.View, 'getUrl')
    def getUrl(self):
        """ """
        field = self.getField('organisationUrl')
        return field.getAccessor(self)()

registerType(Organisation, PROJECTNAME)