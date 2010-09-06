# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Field import decode, encode
from Products.Archetypes.atapi import ObjectField, StringField


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
