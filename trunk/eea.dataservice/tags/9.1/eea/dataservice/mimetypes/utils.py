""" Mimetypes utilities
"""
from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem
from Products.MimetypesRegistry.common import MimeTypeException

def register_mimetypes(registry, mimetypes):
    """Find things that are not in the specially registered mimetypes
    and add them using some default policy:

    Params:
    registry  -- Plone mimetypes_registry
    mimetypes -- a tuple of dictionaries with mimetypes metadata.
                 See database.py
    """
    for mimetype in mimetypes:
        extensions = mimetype.get('extensions')
        mt = mimetype.get('mimetype')
        title = mimetype.get('title')
        icon = mimetype.get('icon')

        ext_exists = False
        for ext in extensions:
            if registry.lookupExtension(ext):
                ext_exists = True
                break

        # Extension already registered, skip it
        if ext_exists:
            continue

        try:
            mto = registry.lookup(mt)
        except MimeTypeException:
            # malformed MIME type
            continue

        # Add new mimetype
        if not mto:
            isBin = mt.split('/', 1)[0] != "text"
            registry.register(
                MimeTypeItem(title, (mt,), tuple(extensions), isBin, icon))
            continue

        # Edit existing mimetype
        mto = mto[0]
        for ext in extensions:
            if not ext in mto.extensions:
                registry.register_extension(ext, mto)
                mto.extensions += (ext, )
