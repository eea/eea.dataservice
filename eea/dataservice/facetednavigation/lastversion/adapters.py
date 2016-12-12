""" Adapters
"""
from zope.interface import implements
from eea.facetednavigation.interfaces import IWidgetFilterBrains
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
import operator
import logging

logger = logging.getLogger('faceted_lastest_version')


class WidgetFilterBrains(object):
    """ Filter brains after query
    """
    implements(IWidgetFilterBrains)

    def __init__(self, context):
        self.widget = context

    @property
    def catalog(self):
        """ Catalog
        """
        return getToolByName(self.widget, 'portal_catalog')

    def __call__(self, brains, form):
        """ Filter brains
        """
        last_versions = {}
        seventies = DateTime(1970)
        for i, item in enumerate(brains):
            version_id = getattr(item, 'getVersionId', '')
            # #17812 the brain can be a discussion object which
            # returns Missing.Value when retrieving the getVersionId
            if not version_id:
                continue

            if not isinstance(version_id, basestring):
                logger.warning('%s has a wrong version_id', item.getURL())
            # #75032 the search returns for some brains the lower version,
            # because for the higher version some search criteria are missed.
            # to fix, for all brains we need to run a new query by version_id
            # to have the latest version of these
            if version_id in last_versions:
                continue

            versions = self.catalog(getVersionId=version_id)

            for brain in versions:
                effective_date = (
                    getattr(brain, 'EffectiveDate', None) or
                    getattr(brain, 'CreationDate', None) or
                    seventies
                )
                if last_versions.has_key(version_id):
                    current_date = (
                        getattr(last_versions[version_id][0],
                                'EffectiveDate', None) or
                        getattr(last_versions[version_id][0],
                                'CreationDate', None) or
                        seventies
                    )
                    # 69328 compare DateTime objects instead of 'None' strings
                    effective = DateTime(effective_date) if effective_date and \
                                    effective_date != 'None' else \
                        DateTime(getattr(brain, 'CreationDate', 1000))
                    current = DateTime(current_date) if current_date and \
                                    current_date != 'None' else DateTime(1000)
                    if current < effective:
                        last_versions[version_id] = (brain, i)
                else:
                    last_versions[version_id] = (brain, i)

        return [res[0] for res in
                   sorted(last_versions.values(), key=operator.itemgetter(1))]
