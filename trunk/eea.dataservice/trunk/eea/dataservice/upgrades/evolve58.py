import logging
from Products.CMFCore.utils import getToolByName


logger = logging.getLogger("eea.dataservice")


def evolve(context):

    catalog = getToolByName(context, 'portal_catalog')
    wftool = getToolByName(context, 'portal_workflow')

    wftool.setChainForPortalTypes("EEAFigureFile", ())
    logger.info("Changed workflow to None for EEAFigureFile")

    ffs = catalog.unrestrictedSearchResults(portal_type="EEAFigureFile")
    logger.info("Starting to update workflow mappings for %s figurefiles" % len(ffs))
    i = 0
    for brain in ffs:
        obj = brain.getObject()
        wftool._recursiveUpdateRoleMappings(obj, {})
        if (i % 100) == 0:
            transaction.savepoint()
            logger.info("Savepoint for 100 updated figurefiles")

    logger.info("Done updating workflow mappings for %s figurefiles" % len(ffs))

