""" Catalog custom indexes
"""
from zope.interface import Interface
from plone.indexer import indexer

@indexer(Interface)
def getFileName(obj, **kwargs):
    """ Index for filename
    """
    getField = getattr(obj, 'getField', None)
    if not getField:
        return ''

    field = getField('file')
    if not field:
        return ''

    getFilename = getattr(field, 'getFilename', None)
    if not getFilename:
        return ''

    return getFilename(obj)
