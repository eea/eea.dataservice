""" IMS
"""

from Products.CMFCore.utils import getToolByName
from eea.workflow.readiness import ObjectReadiness
from eea.versions.interfaces import IGetVersions
from zope.component import getMultiAdapter
from zope.publisher.interfaces import NotFound
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile as VPT
import json

class GetIMSimage(object):
    """ Get image to be displayed on IMS portal
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, gid='', image='preview'):
        cat = getToolByName(self.context, 'portal_catalog')
        query = {'UID': gid}
        brains = cat.unrestrictedSearchResults(**query)
        if brains:
            figure = self.context.unrestrictedTraverse(brains[0].getPath())
            GetImg = getMultiAdapter((figure, self.request), name='imgview')

            # Transform old IMS calls of image
            if image == 'bigthumb.png':
                image = 'preview'

            return GetImg(scalename=image).data
        else:
            raise NotFound(self.request, image)

class FigureObjectReadiness(ObjectReadiness):
    """ Object readiness state info for Figures
    """
    checks = {
        'published': [(
            lambda o: not bool(set(('Data', 'ExternalDataSpec')).intersection(
                set([x.portal_type for x in o.getRelatedItems()]))),
            'At least one references to a data source is required'
        )]
    }



class GetLegislationDatasets(object):
    """ Get all datasets sorted by legislation
    """
    
    template = VPT('../template/legislation_datasets_overview.pt')
    __call__ = template
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_datasets(self):
        """ Return datasets sorted by legislation
        """
        view = self.context.restrictedTraverse('all-datasets/daviz.json')()
        values = json.loads(view)
        datasets = values['items']
        results = {}
        legislation_titles = {}
        for data in datasets:
            legislation_label = data['instrument_label']
            legislation_url = data['instrument']
            legislation_title = data['instrument_title']
            key = (legislation_label, legislation_url, legislation_title)
            if key not in results:
                results[key] = []
                legislation_titles[legislation_label] = []

            # get dataset latest version only
            data_url = data['dataset']
            data_url_short = str(data_url.split('http://www.eea.europa.eu/')[1])
            data_obj = self.context.unrestrictedTraverse(data_url_short, None)
            if data_obj:
                api = IGetVersions(data_obj)
                latest_version = api.latest_version()
                latest_version_url = latest_version.absolute_url()
                data_url = latest_version_url
                data['dataset'] = latest_version_url


                date = latest_version.getEffectiveDate() or latest_version.creation_date
                if not date:
                    field = latest_version.getField('lastUpload')
                    if field:
                        date = field.getAccessor(latest_version)()
                data['publishing_date'] = date
            else:
                continue

            # avoid dataset duplicated since query returns same datasets with
            # several rod objects
            if not data_url in legislation_titles[legislation_label]:
                results[key].append(data)
                legislation_titles[legislation_label].append(data_url)
        return results 
