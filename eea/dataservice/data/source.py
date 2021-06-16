""" figure multi data provenance
"""
from zope.interface import implements

from eea.app.visualization.interfaces import IMultiDataProvenance
from eea.app.visualization.data.source import MultiDataProvenance


class EEAFigureMultiDataProvenance(MultiDataProvenance):
    """ eea figure multi data provenance from relations
    """
    implements(IMultiDataProvenance)

    def defaultProvenances(self):
        """ default provenances
        """

        relatedProvenances = []
        relatedItems = self.context.getRelatedItems()
        for item in relatedItems:
            if item.portal_type != 'ExternalDataSpec':
                continue
            related_dict = {
                'title': getattr(item, 'title', ''),
                'owner': getattr(item, 'provider_url', ''),
                'link': getattr(item, 'dataset_url', ''),
            }
            relatedProvenances.append(related_dict)

        return relatedProvenances
