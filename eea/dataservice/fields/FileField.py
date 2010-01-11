# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from zope.event import notify
from eea.dataservice.events import FileUploadedEvent
from plone.app.blob.field import BlobField

class EventFileField(BlobField):
    """ Raise an event on file upload
    """
    def set(self, instance, value, **kwargs):
        if '_migration_' not in kwargs.keys() and value:
            notify(FileUploadedEvent(instance, value))
        return BlobField.set(self, instance, value, **kwargs)
