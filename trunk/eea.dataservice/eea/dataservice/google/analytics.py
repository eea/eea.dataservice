import logging
from zope.component import getMultiAdapter
from xml.dom import minidom
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('eea.dataservice.google')

class TopDatasets(BrowserView):
    """ Get top datasets downloads
    """

    def parse_xml(self, xml):
        """ Parse data from xml
        """
        dom = minidom.parseString(xml)
        error = dom.getElementsByTagName('error')
        if error:
            logger.exception(("An error occured while trying to get top downloads. "
                              "Please check portal_google/analytics configuration"))
            return []

        entries = dom.getElementsByTagName('entry')
        res = []
        for entry in entries:
            key = value = None
            for prop in entry.childNodes:
                if prop.nodeName == u'dxp:dimension':
                    if prop.getAttribute('name') == u'ga:pagePath':
                        key = prop.getAttribute('value')
                if prop.nodeName == u'dxp:metric':
                    if prop.getAttribute('name') == u'ga:pageviews':
                        value = prop.getAttribute('value')
                        try:
                            value = int(value)
                        except (TypeError, ValueError):
                            value = 0
                if key and value:
                    res.append((key, value))
                    break
        return res

    def get_dataset(self, version_id):
        """ Get dataset from version id
        """
        if not version_id:
            return {}

        ctool = getToolByName(self.context, 'portal_catalog')
        query = {
            'getVersionId': version_id,
            'sort_on': 'effective',
            'sort_order': 'reverse',
        }
        brains = ctool(**query)
        for brain in brains:
            res = {
                'title': brain.Title,
                'link': brain.getURL(),
            }

            # Get image
            doc = brain.getObject()
            for child in doc.objectValues('EEAFigureFile'):
                for image in child.objectValues('ImageFS'):
                    if image.getId().lower().endswith('.gif'):
                        res['image'] = image.absolute_url()
                        break
                if res.get('image', None):
                    break
            return res
        return {}

    #XXX Cache
    def __call__(self, **kwargs):
        if self.request:
            kwargs.update(self.request.form)

        report_path = kwargs.get('google_analytics_report', '')
        if not report_path:
            return []

        report = self.context.unrestrictedTraverse(report_path, None)
        if not report:
            return []

        report_xml = getMultiAdapter((report, self.request), name=u'index_html')
        if not report_xml:
            return []

        xml = report_xml(content_type=None)
        datasets = self.parse_xml(xml)

        res = []
        for path, views in datasets:
            version_id = path.split('/')[-1]
            dataset = self.get_dataset(version_id)
            if not dataset:
                continue
            dataset['views'] = views
            res.append(dataset)
        return res
