"""  Upgrade steps to version 15.0
"""

import logging
import transaction
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger(__name__)


def cleanup_geographicCoverage(context):
    """ upgrade script to cleanup geographicCoverage field values
    """
    ctool = getToolByName(context, 'portal_catalog')
    query = {
        'portal_type': ['Data', 'EEAFigure'],
    }
    brains = ctool.unrestrictedSearchResults(**query)
    
    count = 0
    for brain in brains:
        obj = brain.getObject()
        getField = getattr(obj, 'getField', None)
        field = getField('geographicCoverage')
        value = field.getAccessor(obj)()
        if value:
            field.getMutator(obj)(())
            obj._p_changed = True
            logger.info('cleanup_geographicCoverage: %s' % obj.absolute_url())
            count += 1
            if count % 100 == 0:
                logger.info('cleanup_geographicCoverage: Transaction committed to zodb %s', count)
                transaction.commit()

    logger.info('cleanup_geographicCoverage: %s objects were cleanup.' % count)
