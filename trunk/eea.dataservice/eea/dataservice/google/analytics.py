import logging
from zope.component import getMultiAdapter
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('eea.dataservice.google')

class TopDatasets(BrowserView):
    """ Get top datasets downloads
    """
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
            logger.exception('Empty google_analytics_report path')
            return []

        report = self.context.unrestrictedTraverse(report_path, None)
        if not report:
            logger.exception('Invalid google_analytics_report path')
            return []

        table = getMultiAdapter((report, self.request), name=u'index.table')
        if not table:
            logger.exception('No index.table for report %s' % report.absolute_url())
            return []
        datasets = table()

        res = []
        for dimensions, metrics in datasets:
            path = dimensions.get('ga:pagePath', '')
            version_id = path.split('/')[-1]
            dataset = self.get_dataset(version_id)
            if not dataset:
                continue

            key = ('ga:pageviews' in metrics.keys()) \
                and 'ga:pageviews' or metrics.keys()[0]
            dataset['views'] = metrics.get(key)
            res.append(dataset)
        return res
