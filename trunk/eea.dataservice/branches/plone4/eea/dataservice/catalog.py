""" Catalog custom indexes
"""
from zope.interface import Interface
from plone.indexer import indexer
from eea.dataservice.config import FILE_FIELDS

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

@indexer(Interface)
def getMimeTypes(obj, **kwargs):
    """
    Index for file mime-type. If the file is a zip archive,
    try to unzip it and get mime-types for all the files in the archive.
    """
    getField = getattr(obj, 'getField', None)
    mimetypes = ()
    if not getField:
        return mimetypes


    fieldname = kwargs.pop('fieldname', None)

    if not fieldname:
        for field in FILE_FIELDS:
            mimetypes += getMimeTypes(obj, fieldname=field, **kwargs)
        return mimetypes

    field = getField(fieldname)
    if not field:
        return mimetypes

    # Get mimetypes?
    return mimetypes
