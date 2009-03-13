""" Migrate old dataservice to plone.
"""
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName
from parser import extract_data
from eea.dataservice.config import DATASERVICE_SUBOBJECTS
from eea.themecentre.interfaces import IThemeTagging
from config import (
    DATASERVICE_CONTAINER,
    DATASETS_XML,
    MAPS_AND_GRAPHS_XML
)
import logging
logger = logging.getLogger('eea.dataservice.migration')
info = logger.info

#
# Tools
#
def _redirect(obj, msg):
    """ Set status message and redirect to context absolute_url
    """
    if not obj.request:
        return msg
    context = getattr(obj.context, DATASERVICE_CONTAINER, obj.context)
    url = context.absolute_url()
    IStatusMessage(obj.request).addStatusMessage(msg, type='info')
    obj.request.response.redirect(url)

def _reindex(obj):
    """ Reindex document
    """
    ctool = getToolByName(obj.context, 'portal_catalog')
    ctool.reindexObject(obj)
    
def _publish(obj):
    """ Try to publish given document
    """
    wftool = getToolByName(obj.context, 'portal_workflow')
    state = wftool.getInfoFor(obj, 'review_state', '(Unknown)')
    if state == 'published':
        return
    try:
        wftool.doActionFor(obj, 'publish',
                           comment='Auto published by migration script.')
    except Exception, err:
        logger.warn('Could not publish %s, state: %s, error: %s',
                    obj.absolute_url(1), state, err)
    
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
    dataservice.selectViewTemplate(templateId='folder_summary_view')
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
        
    def add_dataset(self, context, datamodel):
        """ Add new dataset
        """
        ds_id = datamodel.getId()
        
        # Add dataset if it doesn't exists
        if ds_id not in context.objectIds():
            info('Adding dataset id: %s', ds_id)
            ds_id = context.invokeFactory('Data', id=ds_id)
        
        # Set properties
        ds = getattr(context, ds_id)
        self.update_properties(ds, datamodel)
        ds.setTitle(datamodel.get('title', ''))
        tagging = IThemeTagging(ds)
        tags = filter(None, datamodel.get('themes', ''))
        tagging.tags = tags

        return ds_id

    def update_properties(self, ds, datamodel):
        """ Update dataset properties
        """
        ds.setExcludeFromNav(True)
        form = datamodel()
        ds.processForm(data=1, metadata=1, values=form)

        # Publish
        #TODO: set proper state based on -1/0/1 from XML
        _publish(ds)

        # Reindex
        _reindex(ds)
        _reindex(ds.getParentNode())

    #
    # Browser interface
    #
    def __call__(self):
        container = _get_container(self)
        index = 0
        info('Import datasets using xml file: %s', self.xmlfile)

        #TODO: uncomment below, temporary commented
        #ds_info = extract_data(self.xmlfile, 1)['groups_index']
        ds_info = 20
        ds_range = 0
        ds_step = 10

        while ds_range < ds_info:
            ds_range += ds_step
            ds_data = extract_data(self.xmlfile, 0, ds_range-ds_step, ds_range)
            for ds_group_id in ds_data.keys():
                for ds in ds_data[ds_group_id]:
                    self.add_dataset(container, ds)
                    index += 1

        msg = '%d datasets imported !' % index
        info(msg)
        return _redirect(self, msg)

class MigrateMapsAndGraphs(object):
    """ """
    pass