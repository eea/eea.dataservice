""" Base test cases
"""
from plone.testing import z2
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
import logging

logger = logging.getLogger('eea.dataservice.tests')


class EEAFixture(PloneSandboxLayer):
    """ Custom fixture
    """
    def setUpZope(self, app, configurationContext):
        """ Setup Zope
        """
        import eea.dataservice
        import eea.workflow
        self.loadZCML(package=eea.dataservice)
        self.loadZCML(package=eea.workflow)

        try:
            import eea.rdfmarshaller
            self.loadZCML(package=eea.rdfmarshaller)
        except ImportError:
            logger.debug("Disabling tests that depend on eea.rdfmarshaller")

        z2.installProduct(app, 'Products.ATVocabularyManager')
        z2.installProduct(app, 'Products.CMFPlacefulWorkflow')
        z2.installProduct(app, 'eea.dataservice')

    def tearDownZope(self, app):
        """ Uninstall Zope
        """
        z2.uninstallProduct(app, 'Products.ATVocabularyManager')
        z2.uninstallProduct(app, 'Products.CMFPlacefulWorkflow')
        z2.uninstallProduct(app, 'eea.dataservice')

    def setUpPloneSite(self, portal):
        """ Setup Plone
        """
        applyProfile(portal, 'eea.dataservice:default')

EEAFIXTURE = EEAFixture()
FUNCTIONAL_TESTING = FunctionalTesting(bases=(EEAFIXTURE,),
                                       name='EEADataservice:Functional')
