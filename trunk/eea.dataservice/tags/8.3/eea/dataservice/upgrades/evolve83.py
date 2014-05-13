"""  Upgrade steps to version 8.3
"""

import logging
from Products.CMFCore.utils import getToolByName
import transaction

logger = logging.getLogger(__name__)


def reindex_geo_coverage(context):
    """ Migrate to folderish
    """
    ctool = getToolByName(context, 'portal_catalog')
    brains = ctool.unrestrictedSearchResults(
        portal_type=['Data', 'EEAFigure'])

    total = len(brains)
    logger.info('Reindexing %s Data and EEAFigures...', total)
    count = 0
    for brain in brains:
        if not brain.location:
            continue
        logger.info('Reindexing %s', brain.getURL())
        try:
            doc = brain.getObject()
            doc.reindexObject(idxs=['getGeographicCoverage'])
            count += 1
            if count % 100 == 0:
                logger.info('INFO: Transaction committed to zodb (%s/%s)',
                         count, total)
                transaction.commit()
        except Exception, err:
            logger.warn('Couldn\'t migrate %s', brain.getURL())
            logger.exception(err)
            continue

    logger.info('Reindexing Data and EEAFigures... DONE')
    return 'Done migrating %s' % total
