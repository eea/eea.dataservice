""" Migrate old dataservice to plone.
"""
from Products.statusmessages.interfaces import IStatusMessage
from parser import extract_data
from eea.dataservice.config import DATASERVICE_SUBOBJECTS
from config import (
    DATASERVICE_CONTAINER,
    DATASETS_XML,
    MAPS_AND_GRAPHS_XML
)
import logging
logger = logging.getLogger('eea.dataservice.migration')
info = logger.info


def _redirect(obj, msg):
    """ Set status message and redirect to context absolute_url
    """
    if not obj.request:
        return msg
    context = getattr(obj.context, DATASERVICE_CONTAINER, obj.context)
    url = context.absolute_url()
    IStatusMessage(obj.request).addStatusMessage(msg, type='info')
    obj.request.response.redirect(url)

#
# Getters
#
def _get_container(obj, *args, **kwargs):
    """ Creates folder structure to import old dataservice
    """
    site = getattr(obj.context, 'SITE', obj.context)
    # Add dataservice folder
    if DATASERVICE_CONTAINER not in site.objectIds():
        info('Create folder %s/%s', site.absolute_url(1), DATASERVICE_CONTAINER)
        site.invokeFactory('Folder',
            id=DATASERVICE_CONTAINER, title=DATASERVICE_CONTAINER.title())
    dataservice = getattr(site, DATASERVICE_CONTAINER)
    dataservice.setConstrainTypesMode(1)
    dataservice.setImmediatelyAddableTypes(DATASERVICE_SUBOBJECTS)
    dataservice.setLocallyAllowedTypes(DATASERVICE_SUBOBJECTS)

    # Returns
    return dataservice
    
    
class MigrateDatasets(object):
    """ Class used to migrate datasets.
    """
    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        self.xmlfile = DATASETS_XML
        
    #
    # Browser interface
    #
    def __call__(self):
        container = _get_container(self)
        index = 0
        info('Import datasets using xml file: %s', self.xmlfile)
        for index, dataset in enumerate(extract_data(self.xmlfile)):
            self.add_dataset(container, dataset)
        msg = '%d datasets imported !' % (index + 1)
        info(msg)
        return _redirect(self, msg)

    
    
        
class MigrateMapsAndGraphs(object):
    """ """
    pass