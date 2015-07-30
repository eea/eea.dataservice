""" Adapters
"""
from zope.interface import implements
from eea.facetednavigation.interfaces import IWidgetFilterBrains
from DateTime import DateTime
import operator

class WidgetFilterBrains(object):
    """ Filter brains after query
    """
    implements(IWidgetFilterBrains)

    def __init__(self, context):
        self.widget = context

    def __call__(self, brains, form):
        """ Filter brains
        """
        last_versions = {}
        seventies = DateTime(1970)

        for i, brain in enumerate(brains):
            version_id = getattr(brain, 'getVersionId', '')
            # #17812 the brain can be a discussion object which
            # returns Missing.Value when retrieving the getVersionId
            if not version_id:
                continue
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
                if current_date < effective_date:
                    last_versions[version_id] = (brain, i)
            else:
                last_versions[version_id] = (brain, i)

        return [res[0] for res in
                   sorted(last_versions.values(), key=operator.itemgetter(1))]
