""" figure multi data provenance
"""
from zope.interface import implements
from zope.component import queryAdapter

from eea.app.visualization.interfaces import IMultiDataProvenance
from eea.app.visualization.data.source import MultiDataProvenance


class EEAFigureMultiDataProvenance(MultiDataProvenance):
    """ eea figure multi data provenance
    """
    implements(IMultiDataProvenance)

    def defaultProvenances(self):
        """ default provenances
        """
        relatedProvenances = ()
        relatedItems = self.context.getRelatedItems()
        orderindex = 0
        for item in relatedItems:
            if item.portal_type != 'ExternalDataSpec':
                continue
            source = queryAdapter(item, IMultiDataProvenance)

            is_provenance_info = False
            for provenance in source.provenances:
                if provenance['link'] == self.context.absolute_url():
                    is_provenance_info = True
            if is_provenance_info:
                continue

            item_provenances = getattr(source, 'provenances')
            for item_provenance in item_provenances:
                dict_item_provenance = dict(item_provenance)
                if dict_item_provenance.get('title', '') != '' and \
                    dict_item_provenance.get('link', '') != '' and \
                    dict_item_provenance.get('owner', '') != '':
                    dict_item_provenance['orderindex_'] = orderindex
                    orderindex = orderindex + 1
                    relatedProvenances = relatedProvenances + \
                                        (dict_item_provenance,)
        return relatedProvenances
