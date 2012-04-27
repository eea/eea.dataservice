""" Safely get IRelations
"""
try:
    from Products.EEAContentTypes import interfaces
    IRelations = interfaces.IRelations
except ImportError:
    from zope.interface import Interface
    class IRelations(Interface):
        """ EEA ContentTypes is not installed """
