# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

import os
import re
import random
from cStringIO import StringIO
from xml.sax import *
from xml.sax.handler import ContentHandler
from types import StringType
from eea.dataservice.vocabulary import EEA_MPCODE_VOCABULARY
from eea.dataservice.vocabulary import CATEGORIES_DICTIONARY, CATEGORIES_DICTIONARY_ID
from eea.dataservice.vocabulary import REFERENCE_DICTIONARY, REFERENCE_DICTIONARY_ID

import logging
logger = logging.getLogger('eea.dataservice.migration')
info = logger.info

def _generate_table_def(data, table_id):
    res = """<table>"""
    for row in data:
        if row == ('', '', '', '', ''):
            info('ERROR: empty row! Table ID: %s' % table_id)
        res += """
<tr>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
</tr>
""" % (row[0], row[1], row[2], row[3], row[4])
    res += """</table>"""
    return res

def _get_countries(data, dataset_id):
    res = []
    err = 0
    exceptions = ['EU15', 'EU25']
    for k in data.split(','):
        k = k.strip()
        if len(k) == 2:
            if k == 'UK': k = 'GB'
            res.append(k.lower())
        else:
            if k in exceptions:
                continue
            err = 1
            res = []
            info('COUNTRIES: bad format %s !' % dataset_id)
            break
    return res

def _get_relation_parent(data, dataset_id):
    if 'Parent data set' in data or 'Parent dataset' in data:
        if 'Derived data set' in data or len(data.split('Parent data set')) > 2:
            info('RELATION ERROR: %s' % dataset_id)
            data = []
        else:
            href = []
            p = re.compile(r'(href="(.*?)")')
            m = p.search(data)
            if m:
                href = m.group()
                href = href.split('metadetails.asp?id=')
                try:
                    href = int(href[1].replace('"',''))
                except:
                    info('RELATION ERROR: %s' % dataset_id)
            else:
                info('RELATION ERROR: %s' % dataset_id)
            data = href
    else:
        #Derived data set
        data = []
    return data

def _checkQualityData(data, dataset_id):
    res = data
    keys = data.keys()
    if len(keys) != 5:
        info('GIQ: not 5 keys %s !' % dataset_id)
        res = None
    multi = 0
    for key in keys:
        if len(data[key]) > 1: multi = 1
    if multi:
        info('GIQ: multi %s !' % dataset_id)
        res = None
    return res

def _get_data(data):
    res = u''.join(data).strip()
    #res = res.replace('<![CDATA[', '')
    #res = res.replace(']]>', '')
    return res

def _get_random(size=0):
    chars = "ABCDEFGHIJKMNOPQRSTUVWXYZ023456789"
    res = ''
    for k in range(size):
        res += random.choice(chars)
    return res

def _check_last_upload(text, dataset_id):
    if 'mmm' in text:
        info('last_upload ERROR: Dataset: %s -- bad format' % dataset_id)
        return ''
    if len(text) < 9:
        info('last_upload ERROR: Dataset: %s -- bad format' % dataset_id)
    return text

def _generate_random_id():
    c = _get_random
    return '%s-%s-%s-%s-%s' % (c(8), c(4), c(4), c(4), c(12))

def _strip_html_tags(text):
    text = text.replace('&amp;#39;', "'")
    return re.sub(r'<[^>]*?>', '', text)

def _check_integer(text):
    res = 1
    try:
        dummy = int(text)
    except:
        res = 0
    return res

def _extarct_organisation_url(text, dataset_id):
    tmp = ''
    try:
        tmp = text.split('<a href="')[1]
        tmp = tmp.split('">')[0]
        if tmp.endswith('/'):
            tmp = tmp[:-1]
    except:
        info('organisation url ERROR: Dataset: %s -- bad format' % dataset_id)
    return tmp

def _map_reference(text, dataset_id):
    text = text.strip()
    for key, val in REFERENCE_DICTIONARY[REFERENCE_DICTIONARY_ID]:
        if text == val: return key
    if text in ['', 'EPSG:']: return ''
    info('ERROR: reference not mapped well %s' % dataset_id)
    return ''

def _map_categories(text):
    for key, val in CATEGORIES_DICTIONARY[CATEGORIES_DICTIONARY_ID]:
        if text == val: return key
    info('ERROR: category dont match %s' % text)
    return text

def _map_eea_mpcode(text, dataset_id):
    res = ['', '']
    text_data = []
    text = text.split('-')
    if len(text) != 2:
        info('eea_mpcode ERROR: Dataset: %s -- bad format' % dataset_id)
        return res
    res[0] = text[0].strip()
    text_data.append(text[0].strip())
    text = text[1].split(':')
    if len(text) != 2:
        info('eea_mpcode ERROR: Dataset: %s -- bad format' % dataset_id)
        return res
    for term in text:
        text_data.append(term.strip())

    for key in EEA_MPCODE_VOCABULARY.keys():
        row_data = EEA_MPCODE_VOCABULARY[key]
        detect = 0
        for term in text_data:
            if str(term) in row_data:
                detect += 1
        if detect == 3:
            res[1] = key
            break
    if res[0] == '' or res[1] == '':
        info('eea_mpcode ERROR: Dataset: %s -- lookup failed' % dataset_id)
    return tuple(res)

def _filter_scale(text, dataset_id):
    data = text.split('1:')
    if len(data) == 2:
        return data[1].replace(' ', '')
    else:
        info('scale ERROR: Dataset: %s --not well formated.' % dataset_id)
        return ''

def _filter_temporal_coverage(text, dataset_id):
    orig_text = text
    res = []
    text = text.replace('Range:', '')
    text = text.replace('Range of years available:', '')
    text = text.replace(' and ', ',')
    text = text.replace(' for population data.', '')
    text = text.replace('Projections for year', '')
    text = text.split(',')
    for year in text:
        year = year.strip()
        try:
            if year.find('-') != -1:
                tmp = year.split('-')
                int(tmp[0])
                int(tmp[1])
                res.extend((str(key))
                    for key in range(int(tmp[0]), int(tmp[1])))
            else:
                int(year)
                res.append(str(year))
        except:
            info('temporalCoverage ERROR: Dataset: %s -- is not integer.' % dataset_id)
            break
    res.reverse()
    return res


class MigrationObject(object):
    """ Encapsulate migration object
    """
    def __init__(self):
        """ base migration object
        """
        pass

    def set(self, key, value, process=0):
        if process:
            value = u''.join(value).strip()
            value = value.replace('&amp;#39;', "'")
        return setattr(self, key, value)

    def delete(self, key):
        if hasattr(self, key):
            return delattr(self, key)

    def __call__(self, all=False):
        if all: return self.__dict__
        return dict((key, value) for key, value in self.items()
                    if key not in ('id', 'title'))

    def get(self, key, default=None):
        return getattr(self, key, default)

    def items(self):
        return self.__dict__.items()

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def getId(self):
        return self.UID

DATASET_METADATA_MAPPING = {
    'Additional information':      'moreInfo',
    'Contact person(s) for EEA':   'contact',
    'Disclaimer':                  'disclaimer',
    'EEA management plan code':    'eeaManagementPlan',
    'Geographic accuracy':         'geoAccuracy',
    'Geographic box coordinates':  'geographic_coordinates',
    'Geographical coverage':       'geographicCoverage',
    'Keyword(s)':                  'subject_existing_keywords',
    'Last upload':                 'lastUpload',
    'Methodology':                 'methodology',
    'Originator':                  'originator',
    'Owner':                       'dataOwner',
    'Processor':                   'processor',
    'Coordinate reference system': 'referenceSystem',
    'Relation':                    'relation',
    'Rights':                      'rights',
    'Scale of the data set':       'scale',
    'Source':                      'dataSource',
    'System folder':               'system_folder',
    'Temporal coverage':           'temporalCoverage',
    'Theme':                       'themes',
    'Unit':                        'units'
}
### Dataset:
    #@param id:                          String;
    #@param shortId:                     String;
    #@param relatedGid:                  String;
    #@param title:                       String;
    #@param description:                 String;
    #@param themes:                      Iterator;
    #@param rights:                      String;
    #@param effectiveDate:               String;
    #@param eeaManagementPlan:           Iterator;
    #@param moreInfo:                    String;
    #@param disclaimer:                  String;
    #@param dataSource:                  String;
    #@param scale:                       Integer;
    #@param geoAccuracy:                 String;
    #@param methodology:                 String;
    #@param units:                       String;
    #@param subject_existing_keywords:   Iterator;
    #@param temporalCoverage:            Iterator;
    #@param contact:                     String;
    #@param geographicCoverage:          Iterator;
    #@param referenceSystem:             String;
    #@param dataOwner:                   String;
    #@param processor:                   String;
    #@param last_upload                  String;

DATAFILE_METADATA_MAPPING = {
    'download_file_downloadfilesgid':  'id',
    'download_file_title':             'title',
    'download_file_note':              'description',
    'category':                        'category',
    'download_file_shortID':           'shortId',
    'download_file_name':              'data_filename',
    'download_file_link':              'download_link',
    'download_file_size':              'filesize',
    'download_file_publish_level':     'publish_level'
}
### Datafile:
#tableview_subgid['tableview_subgid']     'table_id'
#                                         'dataset_id'

#download_file_agreementform

DATATABLE_METADATA_MAPPING = {
    'tableview_title': 'title'
}
#tableview_subgid['tableview_subgid']    'id'
#                                        'category'
#                                        'dataset_id'

DATASUBTABLE_METADATA_MAPPING = {
    'tableviewsub_title':        'title',
    'tableviewsub_note':         'description',
    'tableviewsub_totalrecords': 'records'
}
#tableview_subgid['tableview_subgid']   'id'
#                                       'dataset_id'

DATARELATIONS_METADATA_MAPPING = {
    'other_services_title':   'title',
    'other_services_note':    'description',
    'other_services_url':     'url'
}
#other_services_category['other_services_category']   'category'

class dataservice_info(ContentHandler):
    """ """
    def __init__(self):
        """ constructor """
        self.groups_index = 0

    def get_datasets(self):
        return {'groups_index': self.groups_index}

    def get_tables_files(self):
        return None

    def startElement(self, name, attrs):
        # Dataset group info
        if name == 'relatedgid':
            self.groups_index += 1

class dataservice_handler(ContentHandler):
    """ """

    def __init__(self, ds_from, ds_to):
        """ constructor """
        self.debug_index = 0
        self.ds_from = ds_from
        self.ds_to = ds_to
        self.ds_index = -1
        self.data = []

        self.data_contacts = []
        self.data_keywords = []

        self.dataset_groups = {}
        self.dataset_group_context = 0
        self.dataset_group_current = None

        self.dataset_context = 0
        self.dataset_current = None
        self.metadata_context = 0
        self.metadata_current = None

        self.data_table_file_structure = {'tables': {}}
        self.datafiles = {}
        self.datafiles_context = 0
        self.datafile_context = 0
        self.datafile_current = None

        self.datatables = {}
        self.datatables_context = 0
        self.datatable_context = 0
        self.datatable_current = None

        self.datasubtables = {}
        self.datasubtable_context = 0
        self.datasubtable_current = None

        self.datarelations = {}
        self.datarelations_context = 0
        self.datarelation_context = 0
        self.datarelation_current = None

        self.quality = {}
        self.quality_name = ''
        self.quality_desc = ''

        self.table_definitions = {}
        self.table_def_context = 0
        self.table_row = {}

    # getters
    def get_datasets(self):
        return self.dataset_groups

    def get_datatables(self):
        return self.datatables

    def get_datasubtables(self):
        return self.datasubtables

    def get_tables_files(self):
        return self.data_table_file_structure

    def get_datafiles(self):
        return self.datafiles

    def get_relations(self):
        return self.datarelations

    def get_mapsandgraphs(self):
        pass

    def check_range(self):
        return self.ds_index in range(self.ds_from,self.ds_to)

    # parser
    def startElement(self, name, attrs):
        # Dataset group
        if name == 'relatedgid':
            self.ds_index += 1
            if self.check_range():
                self.dataset_group_context = 1
                self.dataset_group_current = attrs['relatedgid']
                self.dataset_groups[self.dataset_group_current] = []

        if self.check_range():
            # Dataset basic
            if name == 'datasetgid':
                self.dataset_context = 1
                self.dataset_current = MigrationObject()
                self.dataset_current.set('relatedGid', self.dataset_group_current)
                self.dataset_current.set('UID', attrs['datasetgid'])

            # Dataset metadata
            if name == 'metadata_typelabel':
                self.metadata_context = 1
                self.metadata_current = attrs['metadata_typelabel']

            # Datafile metadata
            if name == 'download_file':
                self.datafiles_context = 1
            if name == 'tableview_subgid' and self.datafiles_context:
                self.datafile_current = MigrationObject()
                self.datafile_context = 1
                table_id = ''
                try: table_id = attrs['tableview_subgid']
                except: pass
                self.datafile_current.set('table_id', table_id)
                self.datafile_current.set('dataset_id', self.dataset_current.get('UID'))

            # Datatable metadata
            if name == 'tableGroup':
                self.datatables_context = 1
            if name == 'tableviewgid' and self.datatables_context:
                self.datatable_current = MigrationObject()
                self.datatable_context = 1
                self.datatable_current.set('id', attrs['tableviewgid'])
                self.datatable_current.set('UID', attrs['tableviewgid'])
                self.datatable_current.set('dataset_id', self.dataset_current.get('UID'))

            # Datasubtable metadata
            if name == 'tableview_subgid' and self.datatables_context:
                self.datasubtable_context = 1
                self.datasubtable_current = MigrationObject()
                self.datasubtable_current.set('id', attrs['tableview_subgid'])
                self.datasubtable_current.set('UID', attrs['tableview_subgid'])
                self.datasubtable_current.set('datatable_id', self.datatable_current.get('id'))

            # Table definitions
            if name == 'tableview_subgid' and self.table_def_context:
                self.table_row['table_id'] = attrs['tableview_subgid']
            if name == 'Table_metadata':
                self.table_def_context = 1

            # Datarelations metadata
            if name == 'other_services':
                self.datarelations_context = 1
            if name == 'other_services_category':
                self.datarelation_context = 1
                self.datarelation_current = MigrationObject()
                self.datarelation_current.set('id', self.dataset_current.get('UID'))
                self.datarelation_current.set('category', _map_categories(attrs['other_services_category']))

    def endElement(self, name):
        if self.check_range():
            # Dataset group
            if name == 'relatedgid':
                self.dataset_group_context = 0
                self.dataset_group_current = None

            # Dataset basic
            if name == 'datasetgid':
                self.dataset_current.set('subject_existing_keywords', self.data_keywords)
                self.data_keywords = []
                self.dataset_current.set('contact', '\r\n'.join(self.data_contacts))
                self.data_contacts = []

                self.dataset_groups[self.dataset_group_current].append(self.dataset_current)
                self.dataset_context = 0
                if self.debug_index > 1:
                    info('DEBUG MULTI (%s): %s' % (self.debug_index, self.dataset_current.get('UID')))
                #if self.debug_index == 0:
                #    info('DEBUG ZERO: %s' % self.dataset_current.get('UID'))
                self.debug_index = 0
                self.dataset_current = None
                self.quality = {}

            if name == 'dataset_shortID':
                self.dataset_current.set('shortId', self.data, 1)

            if name == 'dataset_publish_date':
                self.dataset_current.set('effectiveDate', self.data, 1)

            if name == 'dataset_version':
                self.dataset_current.set('version_number', self.data, 1)

            if name == 'dataset_title':
                self.dataset_current.set('title', self.data, 1)

            if name == 'dataset_note':
                desc = _get_data(self.data)
                desc = _strip_html_tags(desc)
                desc_split = desc.split('.')
                more_info = ''
                if len(desc_split) > 1:
                    more_info = '.'.join(desc_split[1:])
                self.dataset_current.set('description', desc_split[0])
                self.dataset_current.set('moreInfo', more_info)

            ###if name == 'dataset_publish_level':
                ###self.dataset_current.set('publish_level', self.data, 1)

            if name == 'dataset_visible':
                self.dataset_current.set('ExpirationDate', self.data, 1)

            # Dataset metadata
            if name == 'metadata_typelabel':
                self.metadata_context = 0
                self.metadata_current = None

            if self.metadata_context:
                field_name = DATASET_METADATA_MAPPING[self.metadata_current]
                data = _get_data(self.data)
                data = data.replace('&amp;#39;', "'")
                if name == 'metadata_text':
                    #if field_name == 'methodology': pass

                    if field_name == 'relation':
                        data = _get_relation_parent(data, self.dataset_current.get('UID'))
                        if data:
                            rel_ob = MigrationObject()
                            rel_ob.set('category', 'parent')
                            rel_ob.set('url', data)
                            rel_ob.set('id', self.dataset_current.get('UID'))
                            self.datarelations[_generate_random_id()] = rel_ob

                    if field_name == 'referenceSystem':
                        data = _map_reference(data, self.dataset_current.get('UID'))
                    if field_name == 'lastUpload':
                        data = _check_last_upload(data, self.dataset_current.get('UID'))
                    if field_name == 'geoAccuracy':
                        curr_value = self.dataset_current.get('geoAccuracy', '')
                        if curr_value and data: curr_value += '\r\n'
                        curr_value += data
                        data = curr_value
                    if field_name == 'dataSource':
                        curr_value = self.dataset_current.get('dataSource', '')
                        if curr_value and data: curr_value += '<br />'
                        curr_value += data
                        data = curr_value
                    if field_name == 'units':
                        curr_value = self.dataset_current.get('units', '')
                        if curr_value and data: curr_value += '<br />'
                        curr_value += data
                        data = curr_value
                    if field_name == 'moreInfo':
                        curr_value = self.dataset_current.get('moreInfo', '')
                        if curr_value and data: curr_value += '<br />'
                        curr_value += data
                        data = curr_value
                    if field_name == 'dataOwner':
                        curr_value = self.dataset_current.get('dataOwner', [])
                        curr_value.append(_extarct_organisation_url(data, self.dataset_current.get('UID')))
                        data = curr_value
                    if field_name == 'processor':
                        curr_value = self.dataset_current.get('processor', [])
                        curr_value.append(_extarct_organisation_url(data, self.dataset_current.get('UID')))
                        data = curr_value
                    if field_name == 'temporalCoverage':
                        self.debug_index += 1
                        data = _filter_temporal_coverage(data, self.dataset_current.get('UID'))
                    if field_name == 'scale':
                        if data:
                            data = _filter_scale(data, self.dataset_current.get('UID'))
                    if field_name == 'geographicCoverage':
                        data = _get_countries(data, self.dataset_current.get('UID'))
                    if field_name == 'subject_existing_keywords':
                        self.data_keywords.extend(data.split(','))
                    if field_name == 'contact':
                        data = _strip_html_tags(data)
                        self.data_contacts.append(data)
                    if field_name == 'themes':
                        data = data.replace('airpollution', 'air')
                        data = data.replace('assesment', 'reporting')
                        data = data.replace(' ', '')
                        data = data.split(',')
                        curr_value = self.dataset_current.get('themes', [])
                        curr_value.extend(data)
                        data = curr_value
                    if field_name == 'rights':
                        data = _strip_html_tags(data)
                        if 'eea' in data.lower() and 'free' in data.lower():
                            data = ''
                    if field_name == 'disclaimer':
                        data = _strip_html_tags(data)
                    if field_name == 'eeaManagementPlan':
                        data = _map_eea_mpcode(data, self.dataset_current.get('UID'))
                        self.dataset_current.set('eeaManagementPlanYear', data[0])
                        self.dataset_current.set('eeaManagementPlanCode', data[1])

                    if not field_name in ['eeaManagementPlan', 'relation']:
                        self.dataset_current.set(field_name, data)
                #if name == 'metadata_text_publish_level':
                    ##self.dataset_current.set('%s_publish_level' % field_name, self.data, 1)
                    #pass

            # Datafile metadata
            if self.datafiles_context:
                if name in DATAFILE_METADATA_MAPPING.keys():
                    field_name = DATAFILE_METADATA_MAPPING[name]
                    data = _get_data(self.data)
                    data = data.replace('&amp;#39;', "'")
                    self.datafile_current.set(field_name, data)
            if name == 'tableview_subgid' and self.datafiles_context:
                if self.datafile_current.get('table_id') not in self.data_table_file_structure['tables'].keys():
                    #add table
                    rand_id = _generate_random_id()
                    self.datafile_current.set('table_id', rand_id)
                    table_ob = MigrationObject()
                    table_ob.set('id', rand_id)
                    table_ob.set('UID', rand_id)
                    table_title = self.datafile_current.get('title', '')
                    if not table_title: table_title = self.datafile_current.get('data_filename', '')
                    if not table_title: info('ERROR: no table title %s' % self.datafile_current.get('id'))
                    table_ob.set('title', table_title)
                    table_ob.set('description', _strip_html_tags(self.datafile_current.get('description', '')))
                    table_ob.set('dataset_id', self.dataset_current.get('UID'))
                    table_ob.set('category', _map_categories(self.datafile_current.get('category', '')))
                    self.data_table_file_structure['tables'][rand_id] = (table_ob, [])
                try:
                    if not self.datafile_current.get('title'):
                        self.datafile_current.set('title', self.datafile_current.get('data_filename').split('/')[-1])
                    self.data_table_file_structure['tables'][self.datafile_current.get('table_id')][1].append(self.datafile_current)
                except:
                    info('ERROR: no associated table for this file %s' % self.datafile_current.get('id'))

                self.datafiles[self.datafile_current.get('id')] = self.datafile_current
                self.datafile_current = None
                self.datafile_context = 1
            if name == 'download_file':
                self.datafiles_context = 0

            # Datatable metadata
            if self.datatable_context and not self.datasubtable_context:
                if name == 'tableview_title':
                    data = _get_data(self.data)
                    data = data.replace('&amp;#39;', "'")
                    self.datatable_current.set('title', data)
                if name == 'tableviewgid':
                    #self.datatables[self.datatable_current.get('id')] = self.datatable_current

                    dt_tmp = self.datatables.get(self.dataset_current.get('UID'), {})
                    dt_tmp[self.datatable_current.get('UID')] = self.datatable_current
                    self.datatables[self.dataset_current.get('UID')] = dt_tmp

                    self.datatable_current = None
                    self.datatable_context = 0
            if name == 'tableGroup':
                self.datatables_context = 0

            # Datasubtable metadata
            if self.datasubtable_context:
                if name in DATASUBTABLE_METADATA_MAPPING.keys():
                    field_name = DATASUBTABLE_METADATA_MAPPING[name]
                    data = _get_data(self.data)
                    data = data.replace('&amp;#39;', "'")
                    if field_name == 'description':
                        data = _strip_html_tags(data)
                    self.datasubtable_current.set(field_name, data)
                if name == 'tableview_subgid':
                    # set table parent metadata
                    self.datasubtable_current.set('category', 'edse')
                    self.datasubtable_current.set('dataset_id', self.datatable_current.get('dataset_id'))
                    if self.datasubtable_current.get('UID') in self.data_table_file_structure['tables'].keys():
                        info('ERROR: duplicate table IDs %s' % self.datasubtable_current.get('UID'))
                    self.data_table_file_structure['tables'][self.datasubtable_current.get('UID')] = (self.datasubtable_current, [])

                    self.datasubtables[self.datasubtable_current.get('UID')] = self.datasubtable_current
                    self.datasubtable_current = None
                    self.datasubtable_context = 0

            # Datarelations metadata
            if self.datarelation_context:
                if name in DATARELATIONS_METADATA_MAPPING.keys():
                    field_name = DATARELATIONS_METADATA_MAPPING[name]
                    data = _get_data(self.data)
                    data = data.replace('&amp;#39;', "'")
                    self.datarelation_current.set(field_name, data)
            if name == 'other_services_category':
                self.datarelations[_generate_random_id()] = self.datarelation_current
                self.datarelation_context = 0
                self.datarelation_current = None
            if name == 'other_services':
                self.datarelations_context = 0

            # Geographic information quality
            if name == 'quality_name':
                self.quality_name = _get_data(self.data)
                self.quality[self.quality_name] = self.quality.get(self.quality_name, []) #pairs of (value, description)
            if name == 'quality_description':
                self.quality_desc = _get_data(self.data)
            if name == 'quality_value':
                self.quality[self.quality_name].append((_get_data(self.data), self.quality_desc))
            if name == 'quality_stamp':
                data = _checkQualityData(self.quality, self.dataset_current.get('UID'))
                if data:
                    for key in data.keys():
                        if key == 'Completeness':
                            self.dataset_current.set('geoQualityCom', data[key][0][0])
                            #self.dataset_current.set('geoQualityComDesc', data)
                        if key == 'Logical consistency':
                            self.dataset_current.set('geoQualityLog', data[key][0][0])
                            #self.dataset_current.set('geoQualityLogDesc', data)
                        if key == 'Position accuracy':
                            self.dataset_current.set('geoQualityPos', data[key][0][0])
                            #self.dataset_current.set('geoQualityPosDesc', data)
                        if key == 'Temporal accuracy':
                            self.dataset_current.set('geoQualityTem', data[key][0][0])
                            #self.dataset_current.set('geoQualityTemDesc', data)
                        if key == 'Thematic accuracy':
                            self.dataset_current.set('geoQualityThe', data[key][0][0])
                            #self.dataset_current.set('geoQualityTheDesc', data)

            # Table definitons
            if name == 'Table_metadata':
                for table_id in self.table_definitions.keys():
                    if table_id not in self.data_table_file_structure['tables'].keys():
                        info('ERROR table definition: %s' % table_id)
                    else:
                        table, files = self.data_table_file_structure['tables'][table_id]
                        table.set('tableDefinition', _generate_table_def(self.table_definitions[table_id], table_id))
                        self.data_table_file_structure['tables'][table_id] = (table, files)

                self.table_definitions = {}
                self.table_def_context = 0
            if name != 'tableview_subgid' and self.table_def_context:
                data = _get_data(self.data)
                if name == 'tableviewsub_metadata_item':
                    self.table_row['item'] = data
                if name == 'tableviewsub_metadata_definition':
                    self.table_row['def'] = data
                if name == 'tableviewsub_metadata_note':
                    self.table_row['note'] = data
                if name == 'tableviewsub_metadata_datatype':
                    self.table_row['type'] = data
                if name == 'tableviewsub_metadata_primarykey':
                    self.table_row['key'] = data
            if name == 'tableview_subgid' and self.table_def_context:
                row = (self.table_row.get('item', ''), self.table_row.get('def', ''),
                       self.table_row.get('note', ''), self.table_row.get('type', ''),
                       self.table_row.get('key', ''))
                td_data = self.table_definitions.get(self.table_row['table_id'], [])
                td_data.append(row)
                self.table_definitions[self.table_row['table_id']] = td_data
                self.table_row = {}

            # XML ends
            if name == 'data':
                info('End parsing of datasets XML')

        self.data = []

    def characters(self, content):
        if self.check_range():
            self.data.append(content)

class dataservice_parser:
    """ """

    def __init__(self, info=0, ds_from=0, ds_to=0):
        """ """
        self.info = info
        self.ds_from = ds_from
        self.ds_to = ds_to

    def parseContent(self, file):
        parser = make_parser()
        if self.info:
            chandler = dataservice_info()
        else:
            chandler = dataservice_handler(self.ds_from, self.ds_to)
        parser.setContentHandler(chandler)
        try:    parser.setFeature(chandler.feature_external_ges, 0)
        except: pass
        inputsrc = InputSource()

        if type(file) is StringType:
            inputsrc.setByteStream(StringIO(file))
        else:
            filecontent = file.read()
            inputsrc.setByteStream(StringIO(filecontent))
        parser.parse(inputsrc)
        return chandler

def extract_basic(file_id):
    """ Read file
    """
    splitdir = os.path.split(os.path.abspath(os.path.dirname(__file__)))
    product_dir = os.path.join(*splitdir)
    file_path = os.path.join(product_dir, file_id)

    f = open(file_path);
    return f.read()

def extract_data(file_id='', info=0, ds_from=0, ds_to=0):
    """ Return datasets from old dataservice exported XMLs
    """
    s = extract_basic(file_id)
    parser = dataservice_parser(info, ds_from, ds_to)
    data = parser.parseContent(s)
    return (data.get_datasets(), data.get_tables_files())

def extract_relations(file_id='', info=0, ds_from=0, ds_to=10000):
    """ Return relations from old dataservice exported XMLs
    """
    s = extract_basic(file_id)
    parser = dataservice_parser(info, ds_from, ds_to)
    data = parser.parseContent(s)
    return data.get_relations()

if __name__ == '__main__':
    print len(extract_data())
