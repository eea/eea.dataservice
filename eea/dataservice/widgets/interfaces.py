""" Widgets custom interfaces
"""
from zope.interface import Interface

class IReferenceWidgetController(Interface):
    """
    Controller to be use within ReferenceBrowserWidget
    macro figure_referencebrowser
    """
    def search(title):
        """ Search for publications with given title. Returns a json object.
        """

    def add(title, eeaid='', **kwargs):
        """ Add publication with given title. Returns a string message.
        """
