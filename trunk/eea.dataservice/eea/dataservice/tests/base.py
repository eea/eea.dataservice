""" Base test cases
"""
import os
from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from StringIO import StringIO
from Globals import package_home
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

    # It seems that files are automatically blobs, but my test won't
    # run without this. (Plone3.1?)
    try:
        #ztc.installPackage('plone.app.blob')
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

        setup = getattr(self.portal, 'portal_setup', None)
        profile = 'ThemeCentre:themecentre'
        if not self.portal._installed_profiles.has_key(profile):
            setup.setImportContext('profile-%s' % (profile,))
            setup.runImportStep('catalog')
            self.portal._installed_profiles[profile] = 1

class DataserviceFunctionalTestCase(FunctionalTestCase, DataserviceTestCase):
    """Base class for functional integration tests for the 'eea.dataservice' product.
    """
    def loadfile(self, rel_filename, ctype='application/pdf'):
        """ load a file
        """
        home = package_home(product_globals)
        filename = os.path.sep.join([home, rel_filename])
        data = open(filename, 'r').read()

        fp = StringIO(data)
        fp.seek(0)

        env = {'REQUEST_METHOD':'PUT'}
        headers = {'content-type' : ctype,
                   'content-length': len(data),
                   'content-disposition':'attachment; filename=test.txt'}

        fs = FieldStorage(fp=fp, environ=env, headers=headers)
        return FileUpload(fs)
