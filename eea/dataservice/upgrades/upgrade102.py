"""  Upgrade steps to version 10.2
"""

import logging
from Products.CMFCore.utils import getToolByName
import transaction

logger = logging.getLogger(__name__)


def cleanup_convert_figure_jobs(context):
    """ Cleanup Async jobs saved on EEAFIgureFile
    """
    ctool = getToolByName(context, 'portal_catalog')
    brains = ctool.unrestrictedSearchResults(
        portal_type=['EEAFigureFile'])

    total = len(brains)
    logger.info('Removing async jobs', total)
    count = 0
    for brain in brains:
        try:
            doc = brain.getObject()
            if getattr(doc, '_convertjob', None):
                del(doc._convertjob)
            else:
                continue
            logger.info('Removing async for %s', brain.getURL())
            count += 1
            if count % 100 == 0:
                logger.info('INFO: Transaction committed to zodb (%s/%s)',
                            count, total)
                transaction.commit()
        except Exception, err:
            logger.warn('Couldn\'t remove async for %s', brain.getURL())
            logger.exception(err)
            continue

    logger.info('EEAFigureFile async removal... DONE')
    return 'Done cleaning %s EEAFigureFile' % total
