""" Test workflow events
"""
import unittest

from eea.dataservice.tests.base import EEAFIXTURE
from plone.app.testing import TEST_USER_NAME, TEST_USER_ID
from plone.app.testing import login
from plone.app.testing import ploneSite
from plone.app.testing import setRoles


class TestWorkflowEvents(unittest.TestCase):
    """ Tests the workflow events triggers
    """
    layer = EEAFIXTURE

    def test_figurefile_publishing_date(self):
        """ Test effective date of EEAFigureFiles which should
            receive the same effective date from the EEAFigure parents
        """
        with ploneSite() as portal:
            print portal
            setRoles(portal, TEST_USER_ID, ['Manager'])
            login(portal, TEST_USER_NAME)
            wftool = portal.portal_workflow
            wftool.setDefaultChain("simple_publication_workflow")
            wftool.setChainForPortalTypes(('EEAFigure',),
                                          'simple_publication_workflow')
            if not hasattr(portal, 'sandbox1'):
                portal.invokeFactory('Folder', 'sandbox1')
            sandbox = portal['sandbox1']
            sandbox.invokeFactory('EEAFigure', 'test1')
            figure = sandbox.objectValues()[0]
            figure.invokeFactory('EEAFigureFile', 'figurefile-test')
            figurefile = figure.objectValues()[0]
            before_figurefile_date = figurefile.effective_date
            wftool.doActionFor(figure, 'publish')
            after_figurefile_date = figurefile.effective_date
            figure_date = figure.effective_date
            condition = before_figurefile_date != after_figurefile_date and \
                        after_figurefile_date == figure_date
            self.failIf(condition,
              "FigureFile should have same effective date as EEAFigure parent")


def test_suite():
    """ Test suite
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestWorkflowEvents))
    return suite

