__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from zope.app.annotation.interfaces import IAnnotations
from eea.versions.versions import (
    VERSION_ID,
    _reindex,
    _get_random
)


def versionIdHandler(obj, event):
    """ Set a versionId as annotation without setting the
        version marker interface just to have a perma link
        to last version
    """
    hasVersions = obj.unrestrictedTraverse('@@hasVersions')
    if not hasVersions():
        verId = _get_random(10)
        anno = IAnnotations(obj)
        ver = anno.get(VERSION_ID)
        #TODO: tests fails with ver = None when adding an EEAFigure,
        #      remove "if ver:" after fix
        if ver:
            if not ver.values()[0]:
                ver[VERSION_ID] = verId
                _reindex(obj)
