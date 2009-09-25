from zope.event import notify
from eea.dataservice.events import FileUploadedEvent
from Products.Archetypes import atapi

class EventFileField(atapi.FileField):
    """ Raise an event on file upload
    """
    def set(self, instance, value, **kwargs):
        notify(FileUploadedEvent(instance, value))
        return atapi.FileField.set(self, instance, value, **kwargs)
