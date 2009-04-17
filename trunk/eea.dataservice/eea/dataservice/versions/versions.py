from DateTime import DateTime

from zope.interface import implements
from zope.interface import alsoProvides, directlyProvides, directlyProvidedBy
from zope.component import adapts
from zope.app.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone import utils

from eea.dataservice.migration.migrate import _generateNewId
from eea.dataservice.migration.parser import _get_random
from eea.dataservice.versions.interfaces import IVersionControl, IVersionEnhanced

VERSION_ID = 'versionId'

def _reindex(obj):
    """ Reindex document
    """
    ctool = getToolByName(obj, 'portal_catalog')
    ctool.reindexObject(obj)

class VersionControl(object):
    """ Version adapter
    """
    implements(IVersionControl)
    adapts(IVersionEnhanced)

    def __init__(self, context):
        """ Initialize adapter. """
        self.context = context
        annotations = IAnnotations(context)

        #Version ID
        ver = annotations.get(VERSION_ID)
        if ver is None:
            verData = {VERSION_ID: ''}
            annotations[VERSION_ID] = PersistentDict(verData)

    def getVersionId(self):
        """ Get version id. """
        anno = IAnnotations(self.context)
        ver = anno.get(VERSION_ID)
        return ver[VERSION_ID]

    def setVersionId(self, value):
        """ Set version id. """
        anno = IAnnotations(self.context)
        ver = anno.get(VERSION_ID)
        ver[VERSION_ID] = value

    versionId = property(getVersionId, setVersionId)

    def getVersionNumber(self):
        """ Return version number """
        #TODO: to be implemented
        pass

class GetVersions(object):
    """ Get all versions
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        res = {}
        ver = IVersionControl(self.context)
        verId = ver.getVersionId()

        if verId:
            cat = getToolByName(self, 'portal_catalog')
            brains = cat.searchResults({'getVersionId' : verId,
                                        'sort_on': 'effective'})

        for index, brain in enumerate(brains):
            res[index+1] = brain.getObject()
        return res

class HasVersions(object):
    """ Check if object has versions
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if IVersionEnhanced.providedBy(self.context):
            return True
        return False

class CreateVersion(object):
    """ Create a new version
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        pu = getToolByName(self.context, 'plone_utils')
        obj_uid = self.context.UID()
        obj_id = self.context.getId()
        obj_title = self.context.Title()
        obj_type = self.context.portal_type
        parent = utils.parent(self.context)

        # Adapt version parent (if case)
        if not IVersionEnhanced.providedBy(self.context):
            alsoProvides(self.context, IVersionEnhanced)
        verparent = IVersionControl(self.context)
        verId = verparent.getVersionId()
        if not verId:
            verId = _get_random(10)
            verparent.setVersionId(verId)
            _reindex(self.context)

        # Create version object
        #TODO: copy/paste object (all properties should be copyed)
        new_id = _generateNewId(parent, obj_title, obj_uid+'1')
        parent.invokeFactory(obj_type, id=new_id, title=obj_title, relatedItem=obj_uid)
        message = _(u'New version created.')
        pu.addPortalMessage(message, 'structure')

        ver = getattr(parent, new_id)
        # Set effective date today
        ver.setEffectiveDate(DateTime())

        # Adapt new version object
        #TODO: if parent copy/paste -ed no need for mark/adapt
        if not IVersionEnhanced.providedBy(ver):
            alsoProvides(ver, IVersionEnhanced)
        verobject = IVersionControl(ver)
        verobject.setVersionId(verId)
        _reindex(ver)

        return self.request.RESPONSE.redirect(ver.absolute_url())

class RevokeVersion(object):
    """ Revoke the context as being a version
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        obj = self.context
        verparent = IVersionControl(obj)
        verparent.setVersionId('')
        directlyProvides(obj, directlyProvidedBy(obj)-IVersionEnhanced)

        pu = getToolByName(self.context, 'plone_utils')
        message = _(u'Version revoked.')
        pu.addPortalMessage(message, 'structure')

        return self.request.RESPONSE.redirect(self.context.absolute_url())