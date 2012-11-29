""" Script used to copy values from relatedProducts field to
    relatedItems field for EEAFigure and Data objects and
    related to the migration/merge/fix of relations
"""
from Products.CMFPlone.utils import getToolByName
import transaction
import logging

logger = logging.getLogger("eea.dataservice.migration")

def move_related_items(self, **kw):
    """ Copy values from relatedProducts field to relatedItems
        field for EEAFigure and Data objects
    """
    catalog = getToolByName(self, "portal_catalog")
    query = {'Language': 'all',
             'portal_type': ['Data', 'EEAFigure']}

    count = 0
    brains = catalog(**query)
    logger.info('Start moving data from relatedProducts to relatedItems')

    for brain in brains:
        count += 1
        obj = brain.getObject()
        rel_prod = obj.getRelatedProducts()
        if rel_prod:
            rel = obj.getRelatedItems()
            rel.extend(rel_prod)
            obj.setRelatedItems(rel)
            logger.info('Relations merged: %s' % obj.absolute_url())

        if not (count % 20):
            transaction.commit()

    transaction.commit()
    logger.info('Done moving data from relatedProducts to relatedItems')
    return "Done"

def migrate_relations(self, **kw):
    """ Script used to migrate/fix relations for Data objects
        once relatedProducts field is deprecated
    """
    catalog = getToolByName(self, "portal_catalog")

    # Fix bad relations of Data objects
    query = {'Language': 'all',
             'portal_type': ['Data']}

    count = 0
    brains = catalog(**query)
    logger.info('Start fixing relations')

    for brain in brains:
        count += 1
        obj = brain.getObject()
        relations = obj.getRelatedItems()

        for rel in obj.getRelatedItems():
            if rel.portal_type == 'EEAFigure':
                logger.info('Fixing relations for: /%s' % obj.absolute_url(1))
                relations.remove(rel)
                fig_rel = rel.getRelatedItems()
                fig_rel.append(obj)
                rel.setRelatedItems(fig_rel)

        obj.setRelatedItems(relations)
        if not (count % 20):
            transaction.commit()

    transaction.commit()
    logger.info('Done fixing relations')
    return "Done"
