"""  Upgrade steps to version 10.2
"""

import logging
from Products.CMFCore.utils import getToolByName
import transaction
from zope.annotation import IAnnotations

logger = logging.getLogger(__name__)


def cleanup_convert_figure_jobs(context):
    """ Cleanup Async jobs saved on EEAFIgureFile
    """
    ctool = getToolByName(context, 'portal_catalog')
    brains = ctool.unrestrictedSearchResults(
        portal_type=['EEAFigureFile'])

    logger.info('Removing async jobs')
    count = 0
    for brain in brains:
        try:
            doc = brain.getObject()
            if getattr(doc, '_convertjob', None):
                del doc._convertjob
            try:
                anno = IAnnotations(doc)
            except TypeError:
                continue
            convert_job = anno.get('convert_figure_job')
            if convert_job and not isinstance(convert_job, dict):
                del anno['convert_figure_job']
            else:
                continue
            logger.info('Removing async for %s', brain.getURL())
            count += 1
            if count % 100 == 0:
                logger.info('INFO: Transaction committed to zodb %s',
                            count)
                transaction.commit()
        except Exception, err:
            logger.warn('Couldn\'t remove async for %s', brain.getURL())
            # ctool.uncatalog_object(brain.getPath())
            logger.exception(err)
            continue

    logger.info('EEAFigureFile async removal... DONE')
    return 'Done cleaning %s EEAFigureFile' % count
