""" Base test cases
"""
import logging
from plone.testing import z2
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile

logger = logging.getLogger('eea.dataservice.tests')


class EEAFixture(PloneSandboxLayer):
    """ Custom fixture
    """
    def setUpZope(self, app, configurationContext):
        """ Setup Zope
        """
        import eea.dataservice
        import eea.dataservice.tests
        import eea.workflow
        import eea.depiction
        import eea.rdfmarshaller
        import Products.EEAContentTypes
        import Products.EEAPloneAdmin

        self.loadZCML(package=eea.dataservice)
        self.loadZCML(package=eea.dataservice.tests, name="testing.zcml")
        self.loadZCML(package=eea.workflow)
        self.loadZCML(package=eea.depiction)
        self.loadZCML(package=eea.rdfmarshaller)
        self.loadZCML(package=Products.EEAContentTypes)
        self.loadZCML(package=Products.EEAPloneAdmin)

        z2.installProduct(app, 'Products.ATVocabularyManager')
        z2.installProduct(app, 'Products.CMFPlacefulWorkflow')
        z2.installProduct(app, 'collective.quickupload')
        z2.installProduct(app, 'eea.dataservice')
        z2.installProduct(app, 'eea.depiction')
        z2.installProduct(app, 'eea.rdfmarshaller')

    def tearDownZope(self, app):
        """ Uninstall Zope
        """
        z2.uninstallProduct(app, 'Products.ATVocabularyManager')
        z2.uninstallProduct(app, 'Products.CMFPlacefulWorkflow')
        z2.uninstallProduct(app, 'collective.quickupload')
        z2.uninstallProduct(app, 'eea.dataservice')
        z2.uninstallProduct(app, 'eea.depiction')
        z2.uninstallProduct(app, 'eea.rdfmarshaller')


    def setUpPloneSite(self, portal):
        """ Setup Plone
        """
        applyProfile(portal, 'eea.dataservice:default')
        applyProfile(portal, 'eea.dataservice.tests:testfixture')
        applyProfile(portal, 'eea.depiction:default')
        applyProfile(portal, 'eea.rdfmarshaller:default')

EEAFIXTURE = EEAFixture()
FUNCTIONAL_TESTING = FunctionalTesting(bases=(EEAFIXTURE,),
                                       name='EEADataservice:Functional')
