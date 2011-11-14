""" Templates interfaces
"""
from zope.interface import Interface

class IProvideTemplates(Interface):
    """ All objects that should have the ability to use templates service
        implemented in eea.dataservice
    """
