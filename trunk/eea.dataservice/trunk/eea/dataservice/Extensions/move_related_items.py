""" Script used to copy values from relatedProducts field to
    relatedItems field for EEAFigure and Data objects and
    related to the migration/merge/fix of relations
"""
from Products.CMFPlone.utils import getToolByName
import transaction
import logging

logger = logging.getLogger("eea.dataservice.migration")

to_migrate = [
'/www/SITE/data-and-maps/figures/final-energy-consumption-by-sector-6',
'/www/SITE/data-and-maps/figures/changes-in-wastewater-treatment-in-regions'
'-of-europe-between-1990-and-1',
'SITE/data-and-maps/figures/ozone-2010-target-value-for-2',
'/www/SITE/data-and-maps/figures/index-of-final-energy-intensity-5',
'/www/SITE/data-and-maps/figures/publications-on-natura-2000-per',
'/www/SITE/data-and-maps/figures/benzene-2010-annual-limit-value-2',
]


def info_related_items(self):
    """ Migration related items """
    catalog = getToolByName(self, "portal_catalog")
    query = {'Language': 'all',
             'portal_type': ['EEAFigure']}

    count = 0
    brains = catalog(**query)
    logger.info('Start info for %s', str(len(brains)))

    for brain in brains:
        count += 1
        obj = brain.getObject()
        rel_prod = obj.getRelatedProducts()
        rel_item = obj.getRelatedItems()
        for k in rel_prod:
            if k not in rel_item:
                logger.info('Exception: %s', obj.absolute_url())
                logger.info(rel_item)
                logger.info(rel_prod)
                break

        if not count % 20:
            transaction.commit()
            logger.info('Another 20 processed')

    transaction.commit()
    logger.info('Done info')
    return "Done"


def move_related_items(self):
    """ Copy values from relatedProducts field to relatedItems
        field for EEAFigure and Data objects
    """
    catalog = getToolByName(self, "portal_catalog")
    query = {'Language': 'all',
             # 'portal_type': ['Data', 'EEAFigure'],
             'path': to_migrate}

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
            logger.info('Relations merged: %s', obj.absolute_url())

        if not count % 20:
            transaction.commit()

    transaction.commit()
    logger.info('Done moving data from relatedProducts to relatedItems')
    return "Done"


def migrate_relations(self):
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
                logger.info('Fixing relations for: /%s', obj.absolute_url(1))
                relations.remove(rel)
                fig_rel = rel.getRelatedItems()
                fig_rel.append(obj)
                rel.setRelatedItems(fig_rel)

        obj.setRelatedItems(relations)
        if not count % 20:
            transaction.commit()

    transaction.commit()
    logger.info('Done fixing relations')
    return "Done"
