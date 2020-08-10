"""  Upgrade steps to version 14.8
"""

import logging
import transaction
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger(__name__)


def publish_datasets_content(context):
    """ Publish datatables + children
    """
    ctool = getToolByName(context, 'portal_catalog')
    wtool = getToolByName(context, 'portal_workflow')
    query = {
        'portal_type': 'DataTable',
        'review_state': 'visible',
    }
    brains = ctool.unrestrictedSearchResults(
        portal_type=['Data'], review_state=['published'])

    logger.info('Publishing datasets contents')
    count = 0

    for brain in brains:
        dataset = brain.getObject()

        for datatable in dataset.getFolderContents(query, full_objects=1):
            children = datatable.getFolderContents(full_objects=1)

            for child in children:
                try:
                    wtool.doActionFor(child, "publish")
                    logger.info('Publishing %s', child.absolute_url())
                    count += 1
                except Exception, err:
                    logger.warn('Couldn\'t publish: %s', child.absolute_url())
                    logger.exception(err)
                    continue

                if count % 100 == 0:
                    logger.info('INFO: Transaction committed to zodb %s',
                                count)
                    transaction.commit()
            try:
                wtool.doActionFor(datatable, "publish")
                logger.info('Publishing datatable %s', datatable.absolute_url())
                count += 1
            except Exception, err:
                logger.warn('Couldn\'t publish: %s', datatable.absolute_url())
                logger.exception(err)
                continue

            if count % 100 == 0:
                logger.info('INFO: Transaction committed to zodb %s',
                            count)
                transaction.commit()

    logger.info('Publishing datasets contents... DONE')
    return 'Done publishing %s datasets items' % count
