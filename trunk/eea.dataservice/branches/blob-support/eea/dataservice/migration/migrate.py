# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

import os
import logging
import operator
from cgi import FieldStorage
from StringIO import StringIO

import transaction
from DateTime import DateTime
from zope.interface import alsoProvides
from ZPublisher.HTTPRequest import FileUpload
from Products.CMFCore.utils import getToolByName
from zope.app.annotation.interfaces import IAnnotations
from Products.statusmessages.interfaces import IStatusMessage

from data import getOrganisationsData
from parser import extract_data, extract_relations
from eea.themecentre.interfaces import IThemeTagging
from eea.dataservice.versions.versions import VERSION_ID
from eea.dataservice.migration.parser import _get_random
from eea.dataservice.versions.interfaces import IVersionControl, IVersionEnhanced
from eea.dataservice.config import DATASERVICE_SUBOBJECTS, ORGANISATION_SUBOBJECTS
from config import (
    DATASERVICE_CONTAINER,
    ORGANISATIONS_CONTAINER,
    DATASETS_XML,
    DATAFILES_PATH,
    TEMPLATE_CONTAINER
)


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
    if len(id) > 250:
        id = id[:250]
        info('WARNING: Object id trunkated, title too long for %s' % uid)
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

def _getState(state):
    """
    """
    state = str(state)
    states = {
        'draft': 'draft',
        '1': 'published',
        '0': 'published_eionet',
        '-1': 'content_pending'}
    return states[state]

def _migrationSetState(obj, new_state):
    """ Set states of imported content
    """
    if new_state == 'draft':
        return

    wftool = getToolByName(obj.context, 'portal_workflow')

    if new_state == 'published':
        wftool.doActionFor(obj, 'quickPublish',
                           comment='Set by migration script.')
    elif new_state == 'published_eionet':
        wftool.doActionFor(obj, 'publishEionet',
                           comment='Set by migration script.')
    elif new_state == 'content_pending':
        wftool.doActionFor(obj, 'submitContentReview',
                           comment='Set by migration script.')
    elif new_state == 'visible':
        wftool.doActionFor(obj, 'quickPublish',
                           comment='Set by migration script.')
        wftool.doActionFor(obj, 'hide',
                           comment='Set by migration script.')

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

    # Add templates folder
    if TEMPLATE_CONTAINER not in dataservice.objectIds():
        info('Create template folder %s/%s/%s', site.absolute_url(1),
            container, TEMPLATE_CONTAINER)
        dataservice.invokeFactory('Folder',
            id=TEMPLATE_CONTAINER, title='Templates of Datasets')
        templates = getattr(dataservice, TEMPLATE_CONTAINER)
        templates.selectViewTemplate(templateId='folder_summary_view')
        templates.setConstrainTypesMode(1)
        templates.setImmediatelyAddableTypes(subobjects)
        templates.setLocallyAllowedTypes(subobjects)

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
        else:
            info('ERROR Organisation id already exist: %s', org_id)

        # Set properties
        org = getattr(context, org_id)
        self.update_properties(org, datamodel)

        return org_id

    def update_properties(self, org, datamodel):
        """ Update organisation properties
        """
        form = datamodel()
        org.processForm(data=1, metadata=1, values=form)
        org.setTitle(datamodel.get('title', ''))
        org._setUID(datamodel.get('UID'))

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
            try:
                ds_id = context.invokeFactory('Data', id=ds_id)
            except:
                info('ERROR: adding dataset with id: %s and UID: %s' % (ds_id, datamodel.get('UID')))
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
        # Set ExpirationDate
        #ExpirationDate = datamodel.get('ExpirationDate')
        #if not int(ExpirationDate):
            #ExpirationDate = DateTime(datamodel.get('effectiveDate', DateTime())) - 30
            #ds.setExpirationDate(ExpirationDate)
        #datamodel.delete('ExpirationDate')

        # Set versionId
        anno = IAnnotations(ds)
        ver = anno.get(VERSION_ID)
        ver[VERSION_ID] = datamodel.get('relatedGid')
        datamodel.delete('relatedGid')

        form = datamodel()
        ds.processForm(data=1, metadata=1, values=form)
        ds.setTitle(datamodel.get('title', ''))
        ds._setUID(datamodel.get('UID'))

        # Set state
        state = datamodel.get('publish_level', 'draft')
        _migrationSetState(ds, _getState(state))

        # Reindex
        _reindex(ds)
        _reindex(ds.getParentNode())

    def add_extra_files(self, context, mypath):
        """ Recursively add all extra DataFiles and folders
            (to be found only in the fs dump)
        """
        try:
            for filename in os.listdir(mypath):
                if filename in ['download', 'downloads', '.svn']:
                    continue
                if os.path.isdir(os.path.join(mypath, filename)):
                    #TODO: set state as 'internal state'
                    context.invokeFactory('Folder',
                                          id=filename,
                                          title=filename)
                    myfolder = getattr(context, filename)
                    myfolder.selectViewTemplate(templateId='folder_summary_view')
                    myfolder.setConstrainTypesMode(1)
                    myfolder.setImmediatelyAddableTypes(FIGURES_SUBOBJECTS)
                    myfolder.setLocallyAllowedTypes(FIGURES_SUBOBJECTS)
                    self.add_extra_files(myfolder, os.path.join(mypath, filename))
                else:
                    datamodel = MigrationObject()
                    datamodel.set('title', filename)
                    datamodel.set('download_file_name', os.path.join(mypath, filename))
                    #datamodel.set('category' , None) #TODO: we set this?
                    datamodel.set('publish_level', 'draft')
                    self.add_subobject(context, datamodel, 'DataFile')
        except OSError:
            pass

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
            if file_path.find(DATAFILES_PATH[1:]) == -1:
                if file_path.startswith('/'):
                    file_path = file_path[1:]
                file_path = os.path.join(DATAFILES_PATH, file_path)
            try:
                file_ob = open(file_path, 'rb')
                file_data = file_ob.read()
                size = len(file_data)
                filename = file_path.split('/')[-1]
                filename = filename.encode('utf-8')
                fp = StringIO(file_data)
                fp.filename = filename
                dt.setFile(fp, _migration_=True)
            except IOError:
                info('ERROR: File not uploaded: %s' % file_path)

        # Set properties
        form = datamodel()
        dt.processForm(data=1, metadata=1, values=form)
        dt.setTitle(datamodel.get('title', ''))
        dt._setUID(datamodel.get('UID'))

        # Set state
        state = datamodel.get('publish_level', 'draft')
        _migrationSetState(dt, _getState(state))

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

        #ds_info = extract_data(self.xmlfile, 1)[0]['groups_index']
        ds_info = 10 #TODO: debug, cleanup me
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

                    # Set EffectiveDate
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

                    chk_res = ctool.searchResults({'portal_type' : 'Data',
                                                   'show_inactive': True,
                                                   'UID' : ds.get('UID')})
                    if not chk_res:
                        has_version = self.add_dataset(container, ds, has_version)
                        ds_index += 1

                    # Add (extra) DataFiles and folders, they will have an "internal state"
                    sys_folder = ds.get('system_folder', None)
                    if sys_folder:
                        sys_folder = sys_folder.lower()
                        if sys_folder.startswith('/'):
                            sys_folder = sys_folder[1:]
                        sys_folder = os.path.join(DATAFILES_PATH, sys_folder)
                        res = ctool.searchResults({'portal_type' : 'Data',
                                                   'show_inactive': True,
                                                   'UID' : ds.get('UID')})
                        if res:
                            context = getattr(container, res[0].getId)
                            self.add_extra_files(context, sys_folder)
                        else:
                            info('ERROR: cant find dataset for system_folder %s' % sys_folder)

            # Add datatables
            for table_id in ds_tables['tables'].keys():
                table, files = ds_tables['tables'][table_id]

                res = ctool.searchResults({'portal_type' : 'Data',
                                           'show_inactive': True,
                                           'UID' : table.get('dataset_id')})
                chk_res = ctool.searchResults({'portal_type' : 'DataTable',
                                           'show_inactive': True,
                                           'UID' : table.get('UID')})
                ds_container = getattr(container, res[0].getId)

                table.delete('dataset_id')
                if not chk_res:
                    self.add_subobject(ds_container, table, 'DataTable')
                    dst_index += 1

                # Add datafiles
                for file_ob in files:
                    res = ctool.searchResults({'portal_type' : 'DataTable',
                                               'show_inactive': True,
                                               'UID' : table_id})
                    chk_res = ctool.searchResults({'portal_type' : 'DataFile',
                                                   'show_inactive': True,
                                                   'UID' : file_ob.get('UID')})
                    if res:
                        if not chk_res:
                            dt_container = getattr(ds_container, res[0].getId)
                            self.add_subobject(dt_container, file_ob, 'DataFile')
                            dsf_index += 1
                    else:
                        info('ERROR: cant find table container %s' % table_id)
            transaction.savepoint()

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
            if rel_categ in ['rews', 'rod', 'parent', 'mg', 'indicator']:
                ds_uid = data[key].get('id', '')
                cat = getToolByName(self, 'portal_catalog')
                brains = cat.searchResults({'portal_type': 'Data',
                                            'show_inactive': True,
                                            'UID': ds_uid})
                if brains:
                    ds = brains[0].getObject()
                    if rel_categ == 'rod':
                        # Set Reporting obligation(s) (ROD)
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
                    elif rel_categ == 'mg':
                        # Set maps&graphs relation
                        mg_shortId = data[key].get('shortId')
                        rel_data = list(ds.getRelatedProducts())
                        mg = cat.searchResults({'portal_type' : 'EEAFigure',
                                                'show_inactive': True,
                                                'getShortId': mg_shortId})
                        if mg:
                            mg_ob = mg[0].getObject()
                            rel_data.append(mg_ob)
                            try:
                                ds.setRelatedProducts(rel_data)
                            except:
                                info('M&G relation ERROR: error on setRelatedProducts:%s for UID:%s' % (mg_shortId, ds.UID()))
                            if len(mg) > 1:
                                info('M&G relation WARNING, too many figures for shortId: %s' % mg_shortId)
                        else:
                            info('M&G relation ERROR, mg shortId not found: %s' % mg_shortId)
                    elif rel_categ == 'rews':
                        # Set Related website(s)/service(s)
                        rel_data = []
                        rel_data = list(ds.getExternalRelations())
                        rel_url = data[key].get('url')
                        rel_data.append(rel_url)
                        ds.setExternalRelations(rel_data)
                    elif rel_categ == 'indicator':
                        # Set Interactive viewers
                        rel_data = []
                        rel_data = list(ds.getRelatedProducts())
                        rel_id = str(data[key].get('url')).split('/')[-1]
                        parent = cat.searchResults({'show_inactive': True,
                                                    'getId': rel_id})
                        if parent:
                            parent_ob = parent[0].getObject()
                            rel_data.append(parent_ob)
                            try:
                                ds.setRelatedProducts(rel_data)
                            except:
                                info('PARENT ERROR: error on setRelatedProducts:%s for UID:%s' % (rel_id, ds.UID()))
                            if len(parent) > 1:
                                info('PARENT WARNING, too many data sets for RelatedProducts Id: %s' % rel_id)
                        else:
                            info('PARENT ERROR, data set RelatedProducts Id not found: %s' % rel_id)
                    elif rel_categ == 'parent':
                        # Set derived data set relation
                        rel_data = []
                        rel_data = list(ds.getRelatedItems())
                        rel_shortId = str(data[key].get('url'))
                        parent = cat.searchResults({'portal_type' : 'Data',
                                                    'show_inactive': True,
                                                    'getShortId': rel_shortId})
                        if parent:
                            parent_ob = parent[0].getObject()
                            rel_data.append(parent_ob)
                            try:
                                ds.setRelatedItems(rel_data)
                            except:
                                info('PARENT ERROR: error on setRelatedItems:%s for UID:%s' % (rel_shortId, ds.UID()))
                            if len(parent) > 1:
                                info('PARENT WARNING, too many data sets for shortId: %s' % rel_shortId)
                        else:
                            info('PARENT ERROR, data set shortId not found: %s' % rel_shortId)
                    _reindex(ds)
                    _reindex(ds.getParentNode())
                    #info('Success, dataset updated, UID: %s' % ds_uid)
                else:
                    info('ERROR, dataset not found, UID: %s' % ds_uid)
                    continue

        msg = '%d relations found !' % len(data.keys())
        info(msg)
        return _redirect(self, msg, DATASERVICE_CONTAINER)
