""" Base test cases
"""
import os
from StringIO import StringIO
from Products.Five import zcml
from plone.app.blob.tests import db
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc

ztc.installProduct('ATVocabularyManager')

from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup

@property
def blobstorage():
    """ Return blobstorage database """
    return db

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
PloneTestCase.setupPloneSite(extension_profiles=('eea.dataservice:default', ))

class DataserviceFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """ Base class for functional integration tests for
        the 'eea.dataservice' product.
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
