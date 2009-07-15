""" Migration constants
"""
import os

DATASERVICE_CONTAINER = 'data'
ORGANISATIONS_CONTAINER = 'organisations'

DATASETS_XML = 'Data_for_XML.xml'
MAPS_AND_GRAPHS_XML = 'Maps_graphs_for_XML.xml'

### To match Whiteshark location
#DATAFILES_PATH = os.path.join('/var/eeawebtest/dataservicefiles')

### To match demo dump in ../src/eea.dataservice/eea/dataservice/migration
#DATAFILES_PATH = os.path.join(os.path.dirname(__file__), 'import_files')

### To match remote devel location
DATAFILES_PATH = os.path.join('/var/local/tmp/dataservicefiles_sharedfiles')
