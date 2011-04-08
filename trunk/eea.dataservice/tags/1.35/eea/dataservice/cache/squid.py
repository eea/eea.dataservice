from Products.CMFCore.utils import getToolByName

def invalidate_file_cache(instance, evt):
    """ EVENT
        called on new file upload. Tries to invalidate squid cache
    """
    stool = getToolByName(instance, 'portal_squid', None)
    if not stool:
        return
    key = instance.absolute_url(1) + '/at_download/file'
    res = stool.pruneUrls([
        key,
        'http/localhost/81/%s' % key
    ])
