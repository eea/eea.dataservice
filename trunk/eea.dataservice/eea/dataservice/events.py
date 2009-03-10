""" New events
"""
from zope.app.event.interfaces import IObjectEvent
from zope.interface import implements

class IObjectPortalTypeChanged(IObjectEvent):
    """ Objects portal_type changed
    """

class ObjectPortalTypeChanged(object):
    """ Sent if portal_type was changed """
    implements(IObjectPortalTypeChanged)

    def __init__(self, context, portal_type):
        self.object = context
        self.portal_type = portal_type
