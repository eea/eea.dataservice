""" Script used to copy values from relatedProducts fiels to
    relatedItems field for EEAFigure and Data objects
"""
from Products.CMFPlone.utils import getToolByName
import logging

logger = logging.getLogger("eea.dataservice.migration")

def move_related_items(self, **kw):
    """ Copy values from relatedProducts fiels to relatedItems
        field for EEAFigure and Data objects
    """
    catalog = getToolByName(self, "portal_catalog")
    query = {'Language': 'all',
             'portal_type': ['Data', 'EEAFigure']}

    brains = catalog(**query)
    logger.info('Start moving data from relatedProducts to relatedItems')

    for brain in brains:
        obj = brain.getObject()

    logger.info('Done moving data from relatedProducts to relatedItems')
    return "Done"
