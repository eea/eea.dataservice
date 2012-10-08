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

    brains = catalog(**query)
    logger.info('Start moving data from relatedProducts to relatedItems')

    for brain in brains:
        obj = brain.getObject()
        rel_prod = obj.getRelatedProducts()
        if rel_prod:
            rel = obj.getRelatedItems()
            rel.extend(rel_prod)
            obj.setRelatedItems(rel)
            logger.info('Relations merged: %s' % obj.absolute_url())

    transaction.commit()
    logger.info('Done moving data from relatedProducts to relatedItems')
    return "Done"

def migrate_relations(self, **kw):
    """ Script used to migrate/fix relations for Data objects
        once relatedProducts field is deprecated
    """
    catalog = getToolByName(self, "portal_catalog")
    query = {'Language': 'all',
             'portal_type': ['Data']}

    brains = catalog(**query)
    logger.info('Start fixing bad relations')

    for brain in brains:
        obj = brain.getObject()
        relations = obj.getRelatedItems()

        for rel in relations:
            if rel.portal_type == 'EEAFigure':
                relations.remove(rel)
                fig_rel = rel.getRelatedItems()
                fig_rel.append(obj)
                rel.setRelatedItems(fig_rel)

        obj.setRelatedItems(relations)

    transaction.commit()
    logger.info('Done fixing bad relations')
    return "Done"
