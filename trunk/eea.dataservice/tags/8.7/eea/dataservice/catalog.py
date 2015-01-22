""" Catalog custom indexes
"""
from tempfile import NamedTemporaryFile
from zipfile import ZipFile
from rarfile import RarFile
from StringIO import StringIO
from zope.component import getMultiAdapter
from zope.interface import Interface
from plone.indexer import indexer
from plone.app.blob.utils import guessMimetype
from eea.cache import cache
from eea.dataservice.config import FILE_FIELDS
from eea.dataservice.interfaces import IDataset, IDatatable, IEEAFigure
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

    # Handle archives
    blobfile = field.getAccessor(obj)()
    if 'zip' in mimetype.lower():
        mimetypes.update(getZipMimeTypes(blobfile))
    elif 'rar' in mimetype.lower():
        mimetypes.update(getRarMimeTypes(blobfile))
    return mimetypes
#
# Handle archives
#
def getZipMimeTypes(blobfile):
    """ Get mime-types from ZIP archive
    """
    filename = getattr(blobfile, 'filename', '')
    if hasattr(blobfile, 'getIterator'):
        blobfile = blobfile.getIterator()
    with NamedTemporaryFile(suffix=filename) as tmpfile:
        for chunk in blobfile:
            tmpfile.write(chunk)
        tmpfile.flush()
        zfile = ZipFile(tmpfile.name)
        for zchild in zfile.infolist():
            data = StringIO(zchild.FileHeader())
            filename = getattr(zchild, 'filename', None)
            mimetype = guessMimetype(data, filename)
            if not mimetype:
                continue
            yield mimetype

def getRarMimeTypes(blobfile):
    """ Get mime-types from RAR archive
    """
    filename = getattr(blobfile, 'filename', '')
    if hasattr(blobfile, 'getIterator'):
        blobfile = blobfile.getIterator()
    with NamedTemporaryFile(suffix=filename) as tmpfile:
        for chunk in blobfile:
            tmpfile.write(chunk)
        tmpfile.flush()
        zfile = RarFile(tmpfile.name)
        for zchild in zfile.infolist():
            data = StringIO(zchild.header_data)
            filename = getattr(zchild, 'filename', None)
            mimetype = guessMimetype(data, filename)
            if not mimetype:
                continue
            yield mimetype


@indexer(IEEAFigure)
def getEEAFigureGeographicCoverage(obj):
    """
    :param obj: Object to be indexed
    :return:  List with value of the location field
    """
    return _location(obj)

@indexer(IDataset)
def getDataGeographicCoverage(obj):
    """
    :param obj: Object to be indexed
    :return:  List with value of the location field
    """
    return _location(obj)


def _location(obj):
    """
    :param obj: Object to be indexed
    :return:  List with value of the location field
    """

    field = obj.getField('location')
    values = field.getAccessor(obj)()
    matches = []
    european_countries = _european_countries(obj)
    for value in values:
        match = value in european_countries
        if match:
            matches.append(value)
    return matches


@cache(lambda method, self: "1")
def _european_countries(obj):
    """  cached value of european countries
    """
    countries_view = getMultiAdapter((obj, obj.REQUEST),
                                     name=u'getGeotagsCountries')()
    countries_view = [i[0].encode('utf-8') for i in countries_view]
    return countries_view
