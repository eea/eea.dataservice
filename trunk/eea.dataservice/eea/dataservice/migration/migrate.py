# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

import transaction
from DateTime import DateTime
from zope.interface import alsoProvides
from ZPublisher.HTTPRequest import FileUpload
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.config import UUID_ATTR
from Products.statusmessages.interfaces import IStatusMessage

from eea.themecentre.interfaces import IThemeTagging
from eea.dataservice.migration.parser import _get_random
from eea.dataservice.versions.interfaces import IVersionControl, IVersionEnhanced
from eea.dataservice.config import DATASERVICE_SUBOBJECTS, ORGANISATION_SUBOBJECTS
from parser import extract_data, extract_relations
from data import getOrganisationsData
from config import (
    DATASERVICE_CONTAINER,
    ORGANISATIONS_CONTAINER,
    DATASETS_XML,
    MAPS_AND_GRAPHS_XML,
    DATAFILES_PATH
)

import os
import operator
import logging
from cgi import FieldStorage
from cStringIO import StringIO

logger = logging.getLogger('eea.dataservice.migration')
info = logger.info

#
# Tools
#
def _generateNewId(context, title, uid):
    id = ''
    plone_tool = getToolByName(context, 'plone_utils', None)
    id = plone_tool.normalizeString(title)
    if id in context.objectIds():
        tmp_ds = getattr(context, id)
        if tmp_ds.UID() != uid:
            idx = 1
            while idx <= 100:
                new_id = "%s-%d" % (id, idx)
                new_ds = getattr(context, new_id, None)
                if new_ds:
                    if new_ds.UID() != uid:
                        idx += 1
                    else:
                        id = new_id
                        break
                else:
                    id = new_id
                    break
    if id == 'methodology': id = 'methodology-1'
    return id

def _redirect(obj, msg, container):
    """ Set status message and redirect to context absolute_url
    """
    if not obj.request:
        return msg
    context = getattr(obj.context, container, obj.context)
    url = context.absolute_url()
    IStatusMessage(obj.request).addStatusMessage(msg, type='info')
    obj.request.response.redirect(url)

def _reindex(obj):
    """ Reindex document
    """
    ctool = getToolByName(obj, 'portal_catalog')
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
    except:
        pass

#
# Getters
#
def _get_container(obj, container, subobjects, *args, **kwargs):
    """ Creates folder structure to import old dataservice
    """
    site = getattr(obj.context, 'SITE', obj.context)
    new = 0
    # Add dataservice folder
    if container not in site.objectIds():
        new = 1
        info('Create folder %s/%s', site.absolute_url(1), container)
        site.invokeFactory('Folder',
            id=container, title=container.title())
    dataservice = getattr(site, container)
    if new:
        dataservice.selectViewTemplate(templateId='folder_summary_view')
        dataservice.setConstrainTypesMode(1)
        dataservice.setImmediatelyAddableTypes(subobjects)
        dataservice.setLocallyAllowedTypes(subobjects)

    # Returns
    return dataservice

class MigrateOrganisations(object):
    """ Class used to migrate organisations
    """
    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        self.organisations = getOrganisationsData()

    def add_organisation(self, context, datamodel):
        """ Add new organisation
        """
        #org_id = datamodel.getId()
        org_id = _generateNewId(context, datamodel.get('title'), datamodel.get('UID'))

        # Add organisation if it doesn't exists
        if org_id not in context.objectIds():
            info('Adding organisation id: %s', org_id)
            org_id = context.invokeFactory('Organisation', id=org_id)

        # Set properties
        org = getattr(context, org_id)
        self.update_properties(org, datamodel)

        return org_id

    def update_properties(self, org, datamodel):
        """ Update organisation properties
        """
        org.setExcludeFromNav(True)
        form = datamodel()
        org.processForm(data=1, metadata=1, values=form)
        org.setTitle(datamodel.get('title', ''))
        setattr(org, UUID_ATTR, datamodel.get('UID'))

        # Publish
        _publish(org)

        # Reindex
        _reindex(org)
        _reindex(org.getParentNode())


    def __call__(self):
        container = _get_container(self, ORGANISATIONS_CONTAINER, ORGANISATION_SUBOBJECTS)
        index = 0
        info('Import organisations using default data.')

        data = self.organisations
        for org_id in data.keys():
            datamodel = data[org_id]
            self.add_organisation(container, datamodel)
            index += 1

        msg = '%d organisations imported !' % index
        info(msg)
        return _redirect(self, msg, ORGANISATIONS_CONTAINER)

class MigrateDatasets(object):
    """ Class used to migrate datasets.
    """
    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        self.xmlfile = DATASETS_XML

    def add_dataset(self, context, datamodel, has_version):
        """ Add new dataset
        """
        current_versionId = None
        ds_id = _generateNewId(context, datamodel.get('title'), datamodel.get('UID'))

        # Add dataset if it doesn't exists
        if ds_id not in context.objectIds():
            ###info('Adding dataset ID: %s', ds_id)
            ds_id = context.invokeFactory('Data', id=ds_id)
        ds = getattr(context, ds_id)

        # Set version
        if has_version:
            if has_version == True:
                has_version = _get_random(10)
            if not IVersionEnhanced.providedBy(ds):
                alsoProvides(ds, IVersionEnhanced)
            verds = IVersionControl(ds)
            verds.setVersionId(has_version)

        # Set properties
        self.update_dataset(ds, datamodel)
        tagging = IThemeTagging(ds)
        tags = filter(None, datamodel.get('themes', ''))
        tagging.tags = tags

        return has_version

    def update_dataset(self, ds, datamodel):
        """ Update dataset properties
        """
        ds.setExcludeFromNav(True)
        # Set ExpirationDate
        ExpirationDate = datamodel.get('ExpirationDate')
        if not int(ExpirationDate):
            ExpirationDate = DateTime(datamodel.get('effectiveDate', DateTime())) - 30
            ds.setExpirationDate(ExpirationDate)
        datamodel.delete('ExpirationDate')

        form = datamodel()
        ds.processForm(data=1, metadata=1, values=form)
        ds.setTitle(datamodel.get('title', ''))
        setattr(ds, UUID_ATTR, datamodel.get('UID'))

        # Publish
        #TODO: set proper state based on -1/0/1 from XML
        _publish(ds)

        # Reindex
        _reindex(ds)
        _reindex(ds.getParentNode())

    def add_subobject(self, context, datamodel, otype):
        """ Add new subobject
        """
        #dt_id = datamodel.get('id')
        dt_id = _generateNewId(context, datamodel.get('title'), datamodel.get('UID'))
        datamodel.delete('id')

        # Add object if it doesn't exists
        if dt_id not in context.objectIds():
            ###info('Adding %s id: %s' % (otype, dt_id))
            try:
                dt_id = context.invokeFactory(otype, id=dt_id)
            except:
                info('ERROR: could not add %s with UID: %s' % (otype, datamodel.get('UID')))

        # Set properties
        dt = getattr(context, dt_id)
        self.update_subobject(dt, datamodel)

        return dt_id

    def update_subobject(self, dt, datamodel):
        """ Update subobject properties
        """
        # Upload file
        if dt.portal_type == 'DataFile':
            file_path = datamodel.get('data_filename', '')
            if file_path.startswith('/'):
                file_path = file_path[1:]
            file_path = os.path.join(DATAFILES_PATH, file_path)
            try:
                file_ob = open(file_path, 'rb')
                file_data = file_ob.read()
                size = len(file_data)
                filename = file_path.split('/')[-1]
                filename = str(filename)
                fp = StringIO(file_data)
                env = {'REQUEST_METHOD':'PUT'}
                headers = {'content-length': size,
                           'content-disposition':'attachment; filename=%s' % filename}
                fs = FieldStorage(fp=fp, environ=env, headers=headers)

                file_field = dt.getField('file')
                kwargs = {'field': file_field.__name__}
                file_field.getMutator(dt)(FileUpload(fs), **kwargs)
            except IOError:
                info('ERROR: File not uploaded: %s' % file_path)

        # Set properties
        dt.setExcludeFromNav(True)
        form = datamodel()
        dt.processForm(data=1, metadata=1, values=form)
        dt.setTitle(datamodel.get('title', ''))
        setattr(dt, UUID_ATTR, datamodel.get('UID'))

        # Publish
        #TODO: set proper state based on -1/0/1 from XML
        _publish(dt)

        # Reindex
        _reindex(dt)
        _reindex(dt.getParentNode())

    #
    # Browser interface
    #
    def __call__(self):
        container = _get_container(self, DATASERVICE_CONTAINER, DATASERVICE_SUBOBJECTS)
        ctool = getToolByName(container, 'portal_catalog')
        ds_index = 0
        dst_index = 0
        dsf_index = 0
        info('Import datasets using xml file: %s', self.xmlfile)

        #TODO: uncomment below, temporary commented
        ds_info = extract_data(self.xmlfile, 1)[0]['groups_index']
        #ds_info = 20
        ds_range = 0
        ds_step = 10

        while ds_range < ds_info:
            ds_range += ds_step
            data = extract_data(self.xmlfile, 0, ds_range-ds_step, ds_range)
            ds_data = data[0]
            ds_tables = data[1]
            # Add datasets
            for ds_group_id in ds_data.keys():
                datasets = ds_data[ds_group_id]
                has_version = None
                for ds in datasets:

                    #Set EffectiveDate
                    if len(datasets) > 1:
                        if has_version == None:
                            has_version = True
                        ds_index = operator.indexOf(datasets, ds)
                        if ds_index == 0:
                            if not 'effectiveDate' in ds.keys():
                                ds.set('effectiveDate', DateTime('01.01.2002'))
                        else:
                            prev_ds = datasets[ds_index-1].get('effectiveDate')
                            if not 'effectiveDate' in ds.keys():
                                ds.set('effectiveDate', DateTime(prev_ds)+0.1)
                            else:
                                if ds.get('effectiveDate') == prev_ds:
                                    ds.set('effectiveDate', DateTime(prev_ds)+0.1)
                    else:
                        if not 'effectiveDate' in ds.keys():
                            ds.set('effectiveDate', DateTime('01.01.2002'))

                    has_version = self.add_dataset(container, ds, has_version)
                    ds_index += 1

            # Add datatables
            for table_id in ds_tables['tables'].keys():
                table, files = ds_tables['tables'][table_id]

                res = ctool.searchResults({'portal_type' : 'Data',
                                           'UID' : table.get('dataset_id')})
                ds_container = getattr(container, res[0].getId)

                table.delete('dataset_id')
                self.add_subobject(ds_container, table, 'DataTable')
                dst_index += 1

                # Add datafiles
                for file_ob in files:
                    res = ctool.searchResults({'portal_type' : 'DataTable',
                                               'UID' : table_id})
                    if res:
                        dt_container = getattr(ds_container, res[0].getId)
                        self.add_subobject(dt_container, file_ob, 'DataFile')
                        dsf_index += 1
                    else:
                        info('ERROR: cant find table container %s' % table_id)
            transaction.commit()

        #msg = '%d datasets, %d datatables and %d datafiles imported !' % (ds_index, dst_index, dsf_index)
        msg = 'Datasets, datatables and datafiles imported!'
        info(msg)
        return _redirect(self, msg, DATASERVICE_CONTAINER)

class MigrateRelations(object):
    """ Class used to migrate relations.
    """
    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        self.xmlfile = DATASETS_XML

    #
    # Browser interface
    #
    def __call__(self):
        container = _get_container(self, DATASERVICE_CONTAINER, DATASERVICE_SUBOBJECTS)
        index = 0
        info('Import relations and files using xml file: %s', self.xmlfile)
        data = extract_relations(self.xmlfile)

        for key in data.keys():
            rel_categ = data[key].get('category')
            if rel_categ in ['rews', 'rod']:
                ds_uid = data[key].get('id', '')
                cat = getToolByName(self, 'portal_catalog')
                brains = cat.searchResults({'portal_type' : 'Data',
                                            'UID': ds_uid})
                if brains:
                    ds = brains[0].getObject()
                    if rel_categ == 'rod':
                        #Set Reporting obligation(s) (ROD)
                        rel_data = []
                        rel_data = list(ds.getReportingObligations())
                        rel_url = data[key].get('url')
                        rel_url = rel_url.replace('http://rod.eionet.europa.eu/obligations/', '')
                        try:
                            rel_url = int(rel_url)
                        except:
                            info('ERROR,rod url bad format, UID: %s' % ds_uid)
                            continue
                        rel_data.append(str(rel_url))
                        ds.setReportingObligations(rel_data)
                    elif rel_categ == 'rews':
                        #Set Related website(s)/service(s)
                        rel_data = []
                        rel_data = list(ds.getExternalRelations())
                        rel_url = data[key].get('url')
                        rel_data.append(rel_url)
                        ds.setExternalRelations(rel_data)
                    _reindex(ds)
                    _reindex(ds.getParentNode())
                    info('Success, dataset updated, UID: %s' % ds_uid)
                else:
                    info('ERROR, dataset not found, UID: %s' % ds_uid)
                    continue

        msg = '%d relations found !' % len(data.keys())
        info(msg)
        return _redirect(self, msg, DATASERVICE_CONTAINER)
