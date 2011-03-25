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
        brains = [brain for brain in brains]
        for brain in brains:
            #ptype = getattr(brain, 'portal_type', None)
            version_id = getattr(brain, 'getVersionId', '')
            if version_id:
            #if ptype == 'Data' and len(version_id):
                effective_date = getattr(brain, 'EffectiveDate', DateTime(1970))
                if len(version_id):
                    if last_versions.has_key(version_id):
                        current_date = getattr(last_versions[version_id], 'EffectiveDate', DateTime(1970))
                        if current_date < effective_date:
                            last_versions[version_id] = brain
                    else:
                        last_versions[version_id] = brain

        versions = [k.data_record_id_ for k in last_versions.values()]
        for brain in brains:
            version_id = getattr(brain, 'getVersionId', '')
            #if ptype == 'Data' and len(version_id):
            if version_id:
                if brain.data_record_id_ in versions:
                    yield brain
            else:
                yield brain
