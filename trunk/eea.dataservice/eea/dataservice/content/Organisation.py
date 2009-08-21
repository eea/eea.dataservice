# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.atapi import *
from Products.Archetypes.Field import decode
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from zope.interface import implements

from eea.dataservice.config import *
from eea.dataservice.interfaces import IOrganisation
from eea.locationwidget.locationwidget import LocationWidget


class OrganisationField(StringField):
    """ """
    def set(self, instance, value, **kwargs):
        old_url = getattr(instance, 'organisationUrl', '')
        kwargs['field'] = self
        # Remove acquisition wrappers
        if not getattr(self, 'raw', False):
            value = decode(aq_base(value), instance, **kwargs)
        self.getStorage(instance).set(self.getName(), instance, value, **kwargs)

        # Update organisation URL to depedencies
        #TODO: make the below dynamic
        if len(old_url):
         cat = getToolByName(instance, 'portal_catalog')
         brains1 = cat.searchResults({'getDataOwner': old_url})
         if len(brains1):
            for k in brains1:
                val = [value]
                k_ob = k.getObject()
                for url in k_ob.getDataOwner():
                    if url != old_url: val.append(url)
                values = {'dataOwner': val}
                k_ob.processForm(data=1, metadata=1, values=values)
                k_ob.reindexObject()
         brains2 = cat.searchResults({'getProcessor': old_url})
         if len(brains2):
            for k in brains2:
                val = [value]
                k_ob = k.getObject()
                for url in k_ob.getProcessor():
                    if url != old_url: val.append(url)
                values = {'processor': val}
                k_ob.processForm(data=1, metadata=1, values=values)
                k_ob.reindexObject()

schema = Schema((

    OrganisationField(
        name='organisationUrl',
        languageIndependent=True,
        accessor='org_url',
        validators=('isURL',),
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

    # Getters
    security.declareProtected(permissions.View, 'getDataRows')
    def getDataRows(self):
        """ """
        res = []
        field = self.getField('organisationUrl')
        url = field.getAccessor(self)()
        cat = getToolByName(self, 'portal_catalog')
        brains = cat.searchResults({'portal_type' : 'Data',
                                    'getDataOwner': url})
        if brains: res.extend(brains)
        return res

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