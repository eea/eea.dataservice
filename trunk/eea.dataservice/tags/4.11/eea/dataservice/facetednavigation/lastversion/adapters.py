""" Adapters
"""
from zope.component import queryMultiAdapter
from zope.interface import implements
from eea.facetednavigation.interfaces import IWidgetFilterBrains


class WidgetFilterBrains(object):
    """ Filter brains after query
    """
    implements(IWidgetFilterBrains)

    def __init__(self, context):
        self.widget = context

    def __call__(self, brains, form):
        """ Filter brains
        """
        for brain in brains:
            versions = queryMultiAdapter(
                (brain.getObject(), self.widget.request), name=u'getVersions')

            if not versions:
                continue

            if not versions.isLatest():
                continue

            yield brain
