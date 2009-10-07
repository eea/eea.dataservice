""" New events
"""
from zope.interface import Attribute
from zope.app.event.interfaces import IObjectEvent
from zope.interface import implements

class IFileUploadedEvent(IObjectEvent):
    """ Objects file uploaded
    """
    object = Attribute("The subject of the event.")
    value = Attribute("File value.")

class FileUploadedEvent(object):
    """ Sent if file was changed """
    implements(IFileUploadedEvent)

    def __init__(self, context, value):
        self.object = context
        self.value = value
