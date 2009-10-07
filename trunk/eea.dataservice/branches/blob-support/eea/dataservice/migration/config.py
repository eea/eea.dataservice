""" Migration constants
"""
import os

### Default locations
DATASERVICE_CONTAINER = 'data'
ORGANISATIONS_CONTAINER = 'organisations'
TEMPLATE_CONTAINER = 'templates'

### XML dump
DATASETS_XML = 'Data_for_XML.xml'

### Files dump
# To match Whiteshark location
#DATAFILES_PATH = os.path.join('/var/eeawebtest/DSstorage/dataservicefiles')

# To match demo dump in ../src/eea.dataservice/eea/dataservice/migration
DATAFILES_PATH = os.path.join(os.path.dirname(__file__), 'import_files')

# To match remote devel location
#DATAFILES_PATH = os.path.join('/var/local/tmp/dataservicefiles_sharedfiles')
