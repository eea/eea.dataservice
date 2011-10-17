""" Catalog custom indexes
"""
from zipfile import ZipFile
from StringIO import StringIO
from zope.interface import Interface
from plone.indexer import indexer
from plone.app.blob.utils import guessMimetype
from eea.dataservice.config import FILE_FIELDS
from eea.dataservice.interfaces import IDataset, IDatatable
from Products.CMFCore.utils import getToolByName

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

@indexer(IDatatable)
def getDatatableFileTypes(obj, **kwargs):
    """ Index for datatables containing mime-types.
    """
    mimetypes = set()
    try:
        path = '/'.join(obj.getPhysicalPath())
    except Exception:
        return tuple(mimetypes)

    ctool = getToolByName(obj, 'portal_catalog', None)
    if not ctool:
        return tuple(mimetypes)

    brains = ctool(
        portal_type='DataFile',
        path=path)

    for brain in brains:
        mimetypes.update(brain.filetype)

    return tuple(mimetypes)

@indexer(IDataset)
def getDatasetFileTypes(obj, **kwargs):
    """ Index for dataset containing mime-types.
    """
    return getDatatableFileTypes(obj, **kwargs)

@indexer(Interface)
def getFileType(obj, **kwargs):
    """
    Index for file mime-type. If the file is a zip archive,
    try to unzip it and get mime-types for all the files in the archive.
    """
    mimetypes = set()
    for field in FILE_FIELDS:
        try:
            mimetypes.update(getMimeTypes(obj, field))
        except Exception:
            continue
    return tuple(mimetypes)

def getMimeTypes(obj, fieldname):
    """ Get mime-types from object field
    """
    getField = getattr(obj, 'getField', None)
    mimetypes = set()
    if not getField:
        return mimetypes

    field = getField(fieldname)
    if not field:
        return mimetypes

    mimetype = field.getContentType(obj)
    mimetypes.add(mimetype)

    if 'zip' not in mimetype.lower():
        return mimetypes

    # Handle ZIP archive
    zfile = field.getAccessor(obj)()
    zfile = StringIO(zfile.data)
    zfile = ZipFile(zfile)

    for zchild in zfile.infolist():
        data = StringIO(zchild.FileHeader())
        filename = zchild.filename
        mimetype = guessMimetype(data, filename)

        if not mimetype:
            continue

        mimetypes.add(mimetype)

    return mimetypes
