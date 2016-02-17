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
