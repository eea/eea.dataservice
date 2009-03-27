import os
import re
import random
from cStringIO import StringIO
from xml.sax import *
from xml.sax.handler import ContentHandler
from types import StringType
from eea.dataservice.vocabulary import EEA_MPCODE_VOCABULARY
from eea.dataservice.vocabulary import CATEGORIES_DICTIONARY, CATEGORIES_DICTIONARY_ID

import logging
logger = logging.getLogger('eea.dataservice.migration')
info = logger.info

def _get_random(size=0):
    chars = "ABCDEFGHIJKMNOPQRSTUVWXYZ023456789"
    res = ''
    for k in range(size):
        res += random.choice(chars)
    return res

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

def _map_categories(text):
    for key, val in CATEGORIES_DICTIONARY[CATEGORIES_DICTIONARY_ID]:
        if text == val: return key
    info('ERROR: category dont match %s' % text)
    return text

def _map_eea_mpcode(text, dataset_id):
    mpcode = ''
    text_data = []
    text = text.split('-')
    if len(text) != 2:
        info('eea_mpcode ERROR: Dataset: %s -- bad format' % dataset_id)
        return mpcode
    text_data.append(text[0].strip())
    text = text[1].split(':')
    if len(text) != 2:
        info('eea_mpcode ERROR: Dataset: %s -- bad format' % dataset_id)
        return mpcode
    for term in text:
        text_data.append(term.strip())

    for key in EEA_MPCODE_VOCABULARY.keys():
        row_data = EEA_MPCODE_VOCABULARY[key]
        detect = 0
        for term in text_data:
            if str(term) in row_data:
                detect += 1
        if detect == 3:
            mpcode = key
            break
    if mpcode == '':
        info('eea_mpcode ERROR: Dataset: %s -- lookup failed' % dataset_id)
    return mpcode

def _filter_scale(text, dataset_id):
    data = text.split('1:')
    if len(data) == 2:
        return data[1]
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
            info('temporal_coverage ERROR: Dataset: %s -- is not integer.' % dataset_id)
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
        return self.id

DATASET_METADATA_MAPPING = {
    'Additional information':     'moreInfo',
    'Contact person(s) for EEA':  'contact',
    'Disclaimer':                 'disclaimer',
    'EEA management plan code':   'eea_mpcode',
    'Geographic accuracy':        'geoAccuracy',
    'Geographic box coordinates': 'geographic_coordinates',
    'Geographical coverage':      'geographic_coverage',
    'Keyword(s)':                 'subject_existing_keywords',
    'Last upload':                'lastUpload',
    'Methodology':                'methodology',
    'Originator':                 'originator',
    'Owner':                      'dataset_owner',
    'Processor':                  'processor',
    'Reference system':           'reference_system',
    'Relation':                   'relation',
    'Rights':                     'rights',
    'Scale of the data set':      'scale',
    'Source':                     'source',
    'System folder':              'system_folder',
    'Temporal coverage':          'temporal_coverage',
    'Theme':                      'themes',
    'Unit':                       'unit'
}
### Dataset:
    #@param id:                          String;
    #@param short_id:                    String;
    #@param title:                       String;
    #@param description:                 String;
    #@param themes:                      Iterator;
    #@param rights:                      String;
    #@param effectiveDate:               String;
    #@param eea_mpcode:                  Integer;
    #@param moreInfo:                    String;
    #@param disclaimer:                  String;
    #@param source:                      Iterator;
    #@param scale:                       Integer;
    #@param geoAccuracy:                 String;
    #@param methodology:                 String;
    #@param unit:                        String;
    #@param subject_existing_keywords:   Iterator;
    #@param temporal_coverage:           Iterator;
    #@param contact:                     String;
    #@param geographic_coverage:         Iterator;
    #@param reference_system:            String;
    #@param dataset_owner:               String;
    #@param processor:                   String;
    #@param last_upload                  String;

DATAFILE_METADATA_MAPPING = {
    'download_file_downloadfilesgid':  'id',
    'download_file_title':             'title',
    'download_file_note':              'description',
    'category':                        'category',
    'download_file_shortID':           'short_id',
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

    def startElement(self, name, attrs):
        # Dataset group info
        if name == 'relatedgid':
            self.groups_index += 1

class dataservice_handler(ContentHandler):
    """ """

    def __init__(self, ds_from, ds_to):
        """ constructor """
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
                ###self.dataset_current.set('group_id', self.dataset_group_current)
                self.dataset_current.set('id', attrs['datasetgid'])
    
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
                self.datafile_current.set('dataset_id', self.dataset_current.get('id'))

            # Datatable metadata
            if name == 'tableGroup':
                self.datatables_context = 1
            if name == 'tableviewgid' and self.datatables_context:
                self.datatable_current = MigrationObject()
                self.datatable_context = 1
                self.datatable_current.set('id', attrs['tableviewgid'])
                self.datatable_current.set('dataset_id', self.dataset_current.get('id'))

            # Datasubtable metadata
            if name == 'tableview_subgid' and self.datatables_context:
                self.datasubtable_context = 1
                self.datasubtable_current = MigrationObject()
                self.datasubtable_current.set('id', attrs['tableview_subgid'])
                self.datasubtable_current.set('datatable_id', self.datatable_current.get('id'))

            # Datarelations metadata
            if name == 'other_services':
                self.datarelations_context = 1
            if name == 'other_services_category':
                self.datarelation_context = 1
                self.datarelation_current = MigrationObject()
                self.datarelation_current.set('id', _generate_random_id())
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
                self.dataset_current = None

            if name == 'dataset_shortID':
                self.dataset_current.set('short_id', self.data, 1)
                
            if name == 'dataset_publish_date':
                self.dataset_current.set('effectiveDate', self.data, 1)

            ###if name == 'dataset_version':
                ###self.dataset_current.set('version_number', self.data, 1)
            
            if name == 'dataset_title':
                self.dataset_current.set('title', self.data, 1)

            if name == 'dataset_note':
                trunc_value = 1500 #TODO: set a true value to be used to trunc
                desc = u''.join(self.data).strip()
                desc = _strip_html_tags(desc)
                if len(desc) > trunc_value: desc = desc[:trunc_value]
                self.dataset_current.set('description', desc)
            
            ###if name == 'dataset_publish_level':
                ###self.dataset_current.set('publish_level', self.data, 1)
            
            ###if name == 'dataset_visible':
                ###self.dataset_current.set('visible', self.data, 1)
                
            # Dataset metadata
            if name == 'metadata_typelabel':
                self.metadata_context = 0
                self.metadata_current = None
                
            if self.metadata_context:
                field_name = DATASET_METADATA_MAPPING[self.metadata_current]
                data = u''.join(self.data).strip()
                data = data.replace('&amp;#39;', "'")
                if name == 'metadata_text':
                    #if field_name == 'last_upload': pass
                    #if field_name == 'moreInfo': pass
                    #if field_name == 'methodology': pass
                    #if field_name == 'unit':pass
                    #if field_name == 'geoAccuracy': pass
                    #if field_name == 'source': pass
                    #if field_name == 'reference_system': pass
                    if field_name == 'dataset_owner':
                        data = _extarct_organisation_url(data, self.dataset_current.get('id'))
                    if field_name == 'proessor':
                        data = _extarct_organisation_url(data, self.dataset_current.get('id'))
                    if field_name == 'temporal_coverage':
                        data = _filter_temporal_coverage(data, self.dataset_current.get('id'))
                    if field_name == 'scale':
                        data = _filter_scale(data, self.dataset_current.get('id'))
                    if field_name == 'geographic_coverage':
                        data = ['ro', 'it', 'ru']
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
                    if field_name == 'rights':
                        data = _strip_html_tags(data)
                    if field_name == 'disclaimer':
                        data = _strip_html_tags(data)
                    if field_name == 'eea_mpcode':
                        data = _map_eea_mpcode(data, self.dataset_current.get('id'))
                    self.dataset_current.set(field_name, data)
                #if name == 'metadata_text_publish_level':
                    ##self.dataset_current.set('%s_publish_level' % field_name, self.data, 1)
                    #pass

            # Datafile metadata
            if self.datafiles_context:
                if name in DATAFILE_METADATA_MAPPING.keys():
                    field_name = DATAFILE_METADATA_MAPPING[name]
                    data = u''.join(self.data).strip()
                    data = data.replace('&amp;#39;', "'")
                    self.datafile_current.set(field_name, data)
            if name == 'tableview_subgid' and self.datafiles_context:
                if self.datafile_current.get('table_id') not in self.data_table_file_structure['tables'].keys():
                    #add table
                    rand_id = _generate_random_id()
                    self.datafile_current.set('table_id', rand_id)
                    table_ob = MigrationObject()
                    table_ob.set('id', rand_id)
                    table_title = self.datafile_current.get('title', '')
                    if not table_title: table_title = self.datafile_current.get('data_filename', '')
                    if not table_title: info('ERROR: no table title %s' % self.datafile_current.get('id'))
                    table_ob.set('title', table_title)
                    table_ob.set('description', _strip_html_tags(self.datafile_current.get('description', '')))
                    table_ob.set('dataset_id', self.dataset_current.get('id'))
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
                    data = u''.join(self.data).strip()
                    data = data.replace('&amp;#39;', "'")
                    self.datatable_current.set('title', data)
                if name == 'tableviewgid':
                    self.datatables[self.datatable_current.get('id')] = self.datatable_current
                    self.datatable_current = None
                    self.datatable_context = 0
            if name == 'tableGroup':
                self.datatables_context = 0

            # Datasubtable metadata
            if self.datasubtable_context:
                if name in DATASUBTABLE_METADATA_MAPPING.keys():
                    field_name = DATASUBTABLE_METADATA_MAPPING[name]
                    data = u''.join(self.data).strip()
                    data = data.replace('&amp;#39;', "'")
                    if field_name == 'description':
                        data = _strip_html_tags(data)
                    self.datasubtable_current.set(field_name, data)
                if name == 'tableview_subgid':
                    # set table parent metadata
                    self.datasubtable_current.set('category', 'edse')
                    self.datasubtable_current.set('dataset_id', self.datatable_current.get('dataset_id'))
                    if self.datasubtable_current.get('id') in self.data_table_file_structure['tables'].keys():
                        info('ERROR: duplicate table IDs %s' % self.datasubtable_current.get('id'))
                    self.data_table_file_structure['tables'][self.datasubtable_current.get('id')] = (self.datasubtable_current, [])

                    self.datasubtables[self.datasubtable_current.get('id')] = self.datasubtable_current
                    self.datasubtable_current = None
                    self.datasubtable_context = 0

            # Datarelations metadata
            if self.datarelation_context:
                if name in DATARELATIONS_METADATA_MAPPING.keys():
                    field_name = DATARELATIONS_METADATA_MAPPING[name]
                    data = u''.join(self.data).strip()
                    data = data.replace('&amp;#39;', "'")
                    self.datarelation_current.set(field_name, data)
            if name == 'other_services_category':
                self.datarelations[self.datarelation_current.get('id')] = self.datarelation_current
                self.datarelation_context = 0
                self.datarelation_current = None
            if name == 'other_services':
                self.datarelations_context = 0

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
    return data.get_datasets()

def extract_tables_files(file_id='', info=0, ds_from=0, ds_to=10000):
    """ Return datatables from old dataservice exported XMLs
    """
    s = extract_basic(file_id)
    parser = dataservice_parser(info, ds_from, ds_to)
    data = parser.parseContent(s)
    return data.get_tables_files()

def extract_relations(file_id='', info=0, ds_from=0, ds_to=10000):
    """ Return relations from old dataservice exported XMLs
    """
    s = extract_basic(file_id)
    parser = dataservice_parser(info, ds_from, ds_to)
    data = parser.parseContent(s)
    return data.get_relations()

if __name__ == '__main__':
    print len(extract_data())