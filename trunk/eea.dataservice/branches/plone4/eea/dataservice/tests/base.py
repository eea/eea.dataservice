import os
from StringIO import StringIO
from Products.Five import zcml
from plone.app.blob.tests import db
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from zope.app.component.hooks import setSite

#ztc.installProduct('LinguaPlone')
ztc.installProduct('ATVocabularyManager')

from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_eea_dataservice():
    """Set up the additional products required for the Dataservice Content.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    fiveconfigure.debug_mode = True
    import eea.dataservice
    zcml.load_config('configure.zcml', eea.dataservice)
    fiveconfigure.debug_mode = False

setup_eea_dataservice()
setupPloneSite(extension_profiles=('eea.dataservice:default', ))

class DataserviceTestCase(PloneTestCase):
    """Base class for integration tests for the 'eea.dataservice' product.
    """
    #def _setup(self):
        #""" Setup test case
        #"""
        #PloneTestCase._setup(self)
        ## Set the local component registry
        #setSite(self.portal)

        #from Products.Five.pythonproducts import patch_ProductDispatcher__bobo_traverse__
        #patch_ProductDispatcher__bobo_traverse__()

        #setup = getattr(self.portal, 'portal_setup', None)
        #profile = 'ThemeCentre:themecentre'
        #if not self.portal._installed_profiles.has_key(profile):
            #setup.setImportContext('profile-%s' % (profile,))
            #setup.runImportStep('catalog')
            #self.portal._installed_profiles[profile] = 1
        #setup.runImportStep('eeacontenttypes_various')

class DataserviceFunctionalTestCase(FunctionalTestCase, DataserviceTestCase):
    """Base class for functional integration tests for the 'eea.dataservice' product.
    """

    def loadblobfile(self, context, rel_filename, ctype='application/pdf'):
        """ load a file
        """
        storage_path = os.path.join(os.path.dirname(__file__))
        file_path = os.path.join(storage_path, rel_filename)
        file_ob = open(file_path, 'rb')
        file_data = file_ob.read()
        #size = len(file_data)
        filename = file_path.split('/')[-1]
        filename = str(filename)
        fp = StringIO(file_data)
        fp.filename = filename
        context.setFile(fp)

        return 'File uploaded.'
