from Products.CMFPlone.CatalogTool import registerIndexableAttribute

def getFileName(object, portal, **kwargs):
    """ Index for filename
    """
    if not getattr(object, 'getField', None):
        return ''

    file_field = object.getField('file')
    if not file_field:
        return ''

    if not getattr(file_field, 'getFilename', None):
        return ''

    return file_field.getFilename(object)

registerIndexableAttribute('filename', getFileName)
