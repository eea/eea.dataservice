""" Widget Controller
"""
import json
from zope.interface import implements

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from eea.dataservice.widgets.interfaces import IReferenceWidgetController

class ReferenceWidgetController(BrowserView):
    """ Reference Widget Controller
    """
    implements(IReferenceWidgetController)

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request
        self.catalog = getToolByName(context, 'portal_catalog')
        self.utils = getToolByName(context, 'plone_utils', None)
    #
    # Search
    #
    def _search(self, title):
        """ Search catalog for
        """
        query = {
            'Title': title,
            'object_provides': 'eea.reports.interfaces.IReportContainerEnhanced'
        }
        brains = self.catalog(**query)
        res = []
        for brain in brains:
            doc = brain.getObject()
            uid = getattr(doc.aq_explicit, 'UID', None)
            if not uid:
                continue

            uid = uid()
            res.append({
                'title': brain.Title.strip(),
                'url': brain.getURL(),
                'uid': uid
            })
        return res

    def search(self, **kwargs):
        """ See interface
        """
        if self.request:
            kwargs.update(self.request.form)

        title = kwargs.get('title', None)
        if not title:
            res = []
        else:
            res = self._search(title)
        return json.dumps(res)
    #
    # Add
    #
    def _add(self, title, eeaid=''):
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

        fid = container.invokeFactory('Report', new_id, title=title)
        publication = container._getOb(fid)
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
