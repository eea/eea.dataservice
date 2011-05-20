from Products.CMFPlone.CatalogTool import registerIndexableAttribute

def getFileName(obj, portal, **kwargs):
    """ Index for filename
    """
    if not getattr(obj, 'getField', None):
        return ''

    file_field = obj.getField('file')
    if not file_field:
        return ''

    if not getattr(file_field, 'getFilename', None):
        return ''

    return file_field.getFilename(obj)

registerIndexableAttribute('filename', getFileName)
