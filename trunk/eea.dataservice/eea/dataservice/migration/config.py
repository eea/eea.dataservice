""" Migration constants
"""
import os

DATASERVICE_CONTAINER = 'data'
ORGANISATIONS_CONTAINER = 'organisations'

DATASETS_XML = 'Data_for_XML.xml'
MAPS_AND_GRAPHS_XML = 'Maps_graphs_for_XML.xml'

DATAFILES_PATH =  os.path.join(os.path.dirname(__file__), 'import_files')
