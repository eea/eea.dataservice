""" Utilities for organisations control panel portlet
"""

import logging
import transaction
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

# Logging
logger = logging.getLogger('eea.dataservice.organisations')
info = logger.info
info_exception = logger.exception


class MoveOrganisationReferences(BrowserView):
    """ Transfer references from one organisation to another
    """

    def get_related_objects(self, org_url, cat):
        """ Related objects
        """
        data = []
        query = {
            'portal_type': ['EEAFigure', 'Data', 'DavizVisualization'],
            'getDataOwner': org_url,
            'show_inactive': True
        }

        owner_brains = cat(**query)
        for brain in owner_brains:
            data.append(brain.getObject())

        query = {
            'portal_type': ['EEAFigure', 'Data', 'DavizVisualization'],
            'getProcessor': org_url,
            'show_inactive': True
        }

        proc_brains = cat(**query)
        for brain in proc_brains:
            data.append(brain.getObject())

        query = {
            'portal_type': ['Specification'],
            'getOwnership': org_url,
            'show_inactive': True
        }

        spec_brains = cat(**query)
        for brain in spec_brains:
            data.append(brain.getObject())

        query = {
            'portal_type': ['ExternalDataSpec'],
            'show_inactive': True
        }

        externals = cat(**query)
        for ext in externals:
            ext_ob = ext.getObject()
            ext_org_url = ext_ob.getProvider_url()
            if ext_org_url and len(ext_org_url) == 1:
                ext_org_url = ext_org_url[0]
            if ext_org_url and ext_org_url == org_url:
                data.append(ext_ob)

        return data

    def __call__(self):
        cat = getToolByName(self.context, 'portal_catalog')
        transfer_from = self.request.get('transfer_from', None)
        transfer_to = self.request.get('transfer_to', None)
        tf_ob = None
        tt_ob = None

        info('starting moving organisation references')
        if transfer_from and transfer_to:
            query = {
                'getId': transfer_from,
                'portal_type': 'Organisation'
            }

            res = cat.searchResults(query)
            if res:
                tf_ob = res[0].getObject()

            query = {
                'getId': transfer_to,
                'portal_type': 'Organisation'
            }

            res = cat.searchResults(query)
            if res:
                tt_ob = res[0].getObject()
        tot = 0
        if tf_ob and tt_ob:
            related_objects = self.get_related_objects(tf_ob.getUrl(), cat)
            old_ref = tf_ob.getUrl()
            new_ref = tt_ob.getUrl()
            count = 0
            tot = len(related_objects)

            for obj in related_objects:
                count += 1
                ptype = obj.portal_type
                if ptype in ['EEAFigure', 'Data', 'DavizVisualization']:
                    references = obj.getDataOwner()
                    if old_ref in references:
                        references = list(references)
                        references.remove(old_ref)
                        references.append(new_ref)
                        references_tpl = tuple(references)
                        obj.setDataOwner(references_tpl)

                    references = obj.getProcessor()
                    if old_ref in references:
                        references = list(references)
                        references.remove(old_ref)
                        references.append(new_ref)
                        references_tpl = tuple(references)
                        obj.setProcessor(references_tpl)
                elif ptype == 'Specification':
                    references = obj.getOwnership()
                    if old_ref in references:
                        references = list(references)
                        references.remove(old_ref)
                        references.append(new_ref)
                        references_tpl = tuple(references)
                        obj.setOwnership(references_tpl)
                elif ptype == 'ExternalDataSpec':
                    if old_ref == obj.getProvider_url():
                        obj.setProvider_url(new_ref)
                else:
                    pass

                obj.reindexObject()
                # Reindex all child assessment objects
                if ptype == 'Specification':
                    for assessment in obj.objectValues('Assessment'):
                        assessment.reindexObject()

                transaction.commit()
                info('committed transaction %s of total %s', count, tot)

        msg = '%s references transferred from "%s" to "%s"' % \
              (tot, tf_ob.Title(), tt_ob.Title())
        info(msg)
        IStatusMessage(self.request).addStatusMessage(msg,
                                                      type='info')
        return self.request.RESPONSE.redirect(self.context.absolute_url() +
                '/organisations_overview?action=organisations-quick-overview')
