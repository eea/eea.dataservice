import os
from StringIO import StringIO
from Products.Five import zcml
from Globals import package_home
from plone.app.blob.tests import db
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from zope.app.component.hooks import setSite
from eea.dataservice.config import product_globals

# Let Zope know about the two products we require above-and-beyond a basic
# Plone install (PloneTestCase takes care of these).

ztc.installProduct('PloneLanguageTool')
ztc.installProduct('LinguaPlone')
ztc.installProduct('Five')
ztc.installProduct('FiveSite')
ztc.installProduct('ATVocabularyManager')

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite
from Products.PloneTestCase.layer import onsetup
from cgi import FieldStorage
from ZPublisher.HTTPRequest import FileUpload


@onsetup
def setup_eea_dataservice():
    """Set up the additional products required for the Dataservice Content.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    fiveconfigure.debug_mode = True
    import Products.Five
    zcml.load_config('meta.zcml', Products.Five)
    import Products.FiveSite
    zcml.load_config('configure.zcml', Products.FiveSite)
    # Load the ZCML configuration for the eea.dataservice package.
    # This includes the other products below as well.

    import eea.dataservice
    zcml.load_config('configure.zcml', eea.dataservice)
    fiveconfigure.debug_mode = False

    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.

    try:
        ztc.installPackage('eea.dataservice')
    except AttributeError:
        # Old ZopeTestCase
        pass

# The order here is important: We first call the (deferred) function which
# installs the products we need for the Optilux package. Then, we let
# PloneTestCase set up this product on installation.

setup_eea_dataservice()
EXTRA_PRODUCTS = [
    'ATVocabularyManager',
    'PloneLanguageTool',
    'LinguaPlone',
    'EEAContentTypes',
]
try:
    import plone.app.blob
except ImportError, error:
    # No plone.app.blob installed
    pass
else:
    EXTRA_PRODUCTS.append('plone.app.blob')

setupPloneSite(products=EXTRA_PRODUCTS,
               extension_profiles=('eea.dataservice:default',))

class DataserviceTestCase(PloneTestCase):
    """Base class for integration tests for the 'eea.dataservice' product.
    """
    def _setup(self):
        """ Setup test case
        """
        PloneTestCase._setup(self)
        # Set the local component registry
        setSite(self.portal)

        from Products.Five.pythonproducts import patch_ProductDispatcher__bobo_traverse__
        patch_ProductDispatcher__bobo_traverse__()

        setup = getattr(self.portal, 'portal_setup', None)
        profile = 'ThemeCentre:themecentre'
        if not self.portal._installed_profiles.has_key(profile):
            setup.setImportContext('profile-%s' % (profile,))
            setup.runImportStep('catalog')
            self.portal._installed_profiles[profile] = 1
        setup.runImportStep('eeacontenttypes_various')

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
        size = len(file_data)
        filename = file_path.split('/')[-1]
        filename = str(filename)
        fp = StringIO(file_data)
        fp.filename = filename
        context.setFile(fp)

        return 'File uploaded.'
