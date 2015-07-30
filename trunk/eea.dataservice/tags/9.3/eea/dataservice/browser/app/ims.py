""" IMS
"""

from Products.CMFCore.utils import getToolByName
from eea.workflow.readiness import ObjectReadiness
from zope.component import getMultiAdapter
from zope.publisher.interfaces import NotFound

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
