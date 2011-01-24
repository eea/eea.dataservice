""" Evolve scripts
"""
import logging
import transaction
from zLOG import INFO
from zope.component import getMultiAdapter
from Products.CMFPlone.setup.SetupBase import SetupWidget
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('eea.dataservicemigration.evolve')

def evolve1(self, portal):
    """ Evolve
    """
    request = portal.REQUEST
    ctool = getToolByName(portal, 'portal_catalog')
    query = {
        'object_provides': 'eea.dataservice.interfaces.IEEAFigureFile',
        'show_inactive': True,
        'Language': 'all'
    }

    brains = ctool(**query)
    logger.info('Updating %s eea figure files ...', len(brains))
    counter = 0
    for brain in brains:
        doc = brain.getObject()
        convert = False
        for image in doc.objectIds():
            if '75dpi' in image:
                convert = True
                break

        if not convert:
            continue

        logger.info('Updating images for: %s', doc.absolute_url(1))

        convert = getMultiAdapter((doc, request), name=u'convertMap')
        if not convert:
            logger.exception('Invalid converter %s', convert)
            continue

        error = convert(cronjob=True)
        if not error.startswith('Done'):
            logger.exception(error)

        counter += 1
        if counter % 25 == 0:
            logger.info('Transaction commit: %s', counter)
            transaction.commit()

    logger.info('Updated %s eea figure files.', counter)

functions = {
    '#3595 - Fix low resolution images for EEA Figure Files': evolve1
}

class Evolve(SetupWidget):
    type = "EEA Dataservice"
    description = "EEA Dataservice updates"

    functions = functions

    def setup(self):
        pass

    def delItems(self, fns):
        out = []
        out.append(('Currently there is no way to remove a function', INFO))
        return out

    def addItems(self, fns):
        out = []
        for fn in fns:
            self.functions[fn](self, self.portal)
            out.append(('Function %s has been applied' % fn, INFO))
        return out

    def installed(self):
        return []

    def available(self):
        """ Go get the functions """
        return self.functions.keys()
