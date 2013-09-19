""" Adapters
"""
from zope.interface import implements
from eea.facetednavigation.interfaces import IWidgetFilterBrains
from DateTime import DateTime

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

        for brain in brains:
            version_id = getattr(brain, 'getVersionId', '')
            effective_date = (
                getattr(brain, 'EffectiveDate', None) or
                getattr(brain, 'CreationDate', None) or
                seventies
            )

            if last_versions.has_key(version_id):
                current_date = (
                    getattr(last_versions[version_id],
                            'EffectiveDate', None) or
                    getattr(last_versions[version_id],
                            'CreationDate', None) or
                    seventies
                )
                if current_date < effective_date:
                    last_versions[version_id] = brain
            else:
                last_versions[version_id] = brain

        return last_versions.values()
