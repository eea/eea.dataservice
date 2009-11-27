import simplejson as json
from zope.interface import Interface
from zope.interface import implements
from p4a.subtyper.interfaces import ISubtyper
from zope.component import getUtility

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

class IReferenceWidgetController(Interface):
    """
    Controller to be use within ReferenceBrowserWidget
    macro figure_referencebrowser
    """
    def search(eeaid):
        """ Search for publications with given eeaid. Returns a json object.
        """

    def add(title, eeaid, **kwargs):
        """ Add publication with given. Returns a string message.
        """

class ReferenceWidgetController(BrowserView):
    """ Reference Widget Controller
    """
    implements(IReferenceWidgetController)
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.catalog = getToolByName(context, 'portal_catalog')
        self.utils = getToolByName(context, 'plone_utils', None)
    #
    # Search
    #
    def _search(self, eeaid):
        """ Search catalog for
        """
        query = {
            'eeaid': eeaid,
            'object_provides': 'eea.reports.interfaces.IReportContainerEnhanced'
        }
        brains = self.catalog(**query)
        for brain in brains:
            doc = brain.getObject()
            uid = getattr(doc.aq_explicit, 'UID', None)
            if not uid:
                continue

            uid = uid()
            return {
                'title': brain.Title.strip(),
                'url': brain.getURL(),
                'uid': uid
            }
        return {}

    def search(self, **kwargs):
        """ See interface
        """
        if self.request:
            kwargs.update(self.request.form)

        eeaid = kwargs.get('eeaid', None)
        if not eeaid:
            res = {}
        else:
            res = self._search(eeaid)
        return json.dumps(res)
    #
    # Add
    #
    def _add(self, title, eeaid):
        """ Add publication
        """
        site = getattr(self.context, 'SITE', None)
        if not site:
            return "Can't find the root of the site"

        container = getattr(site, 'publications', None)
        if not container:
            return "No publications container found"

        uid = self.utils.normalizeString(title)
        if not uid:
            uid = 'publication'

        new_id = uid
        index = 0
        while new_id in container.objectIds():
            index += 1
            new_id = '%s-%d' % (uid, index)

        fid = container.invokeFactory('Folder', new_id, title=title)
        publication = container._getOb(fid)
        subtyper = getUtility(ISubtyper)
        subtyper.change_type(publication, 'eea.reports.FolderReport')
        publication.getField('eeaid').getMutator(publication)(eeaid)
        self.catalog.reindexObject(publication)
        return 'Publication added'

    def add(self, **kwargs):
        """ See interface
        """
        if self.request:
            kwargs.update(self.request.form)

        title = kwargs.get('title', '')
        eeaid = kwargs.get('eeaid', '')
        return self._add(title=title, eeaid=eeaid)
