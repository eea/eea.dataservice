import os
import re
from cStringIO import StringIO
from xml.sax import *
from xml.sax.handler import ContentHandler
from types import StringType

import logging
logger = logging.getLogger('eea.dataservice.migration')
info = logger.info

def _strip_html_tags(text):
    return re.sub(r'<[^>]*?>', '', text)

def _check_integer(text):
    res = 1
    try:
        dummy = int(text)
    except:
        res = 0
    return res

class Dataset(object):
    """ Encapsulate report
    """
    def __init__(self):
        """
            @param id:                String;
            @param title              String;
            @param description        String;
            @param themes:            Iterator;
            @param rights:            String;
            @param effectiveDate      String;
            @param eea_mpcode         Integer;
            @param moreInfo           String;
            @param disclaimer         String;
            @param source             Iterator;
            @param scale              Integer;
            @param geoAccuracy        Integer;
            @param methodology        String;
            @param unit               String;
            
        """
        pass

    def set(self, key, value, process=0):
        if process: value = u''.join(value).strip()
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
    'Contact person(s) for EEA':  'dataset_contact',
    'Disclaimer':                 'disclaimer',
    'EEA management plan code':   'eea_mpcode',
    'Geographic accuracy':        'geoAccuracy',
    'Geographic box coordinates': 'geographic_coordinates',
    'Geographical coverage':      'geographic_coverage',
    'Keyword(s)':                 'keywords',
    'Last upload':                'effectiveDate',
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

        self.dataset_groups = {}
        self.dataset_group_context = 0
        self.dataset_group_current = None
        self.dataset_context = 0
        self.dataset_current = None
        self.metadata_context = 0
        self.metadata_current = None

    # getters
    def get_datasets(self):
        return self.dataset_groups

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
                self.dataset_current = Dataset()
                ###self.dataset_current.set('group_id', self.dataset_group_current)
                self.dataset_current.set('id', attrs['datasetgid'])
    
            # Dataset metadata
            if name == 'metadata_typelabel':
                self.metadata_context = 1
                self.metadata_current = attrs['metadata_typelabel']
            
    def endElement(self, name):
        if self.check_range():
            # Dataset group
            if name == 'relatedgid':
                self.dataset_group_context = 0
                self.dataset_group_current = None
    
            # Dataset basic
            if name == 'datasetgid':
                self.dataset_groups[self.dataset_group_current].append(self.dataset_current)
                self.dataset_context = 0
                self.dataset_current = None
    
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
                if name == 'metadata_text':
                    #if field_name == 'effectiveDate': pass
                    #if field_name == 'moreInfo': pass
                    #if field_name == 'methodology': pass
                    #if field_name == 'unit':pass
                    if field_name == 'geoAccuracy':
                        #TODO: fix/filter imported values
                        data = '999'
                    if field_name == 'scale':
                        #TODO: fix/filter imported values
                        data = '1:100000000'
                    if field_name == 'source': 
                        #TODO: fix/filter imported values to match vocab values
                        data = ['EEA (European Environment Agency)']
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
                        if not _check_integer(data):
                            info('DATA ERROR: %s is not integer. Dataset: %s' % \
                                   (data, self.dataset_current.get('id')))
                            data = ''
                    self.dataset_current.set(field_name, data)
                if name == 'metadata_text_publish_level':
                    self.dataset_current.set('%s_publish_level' % field_name, self.data, 1)

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

def extract_data(file_id='', info=0, ds_from=0, ds_to=0):
    """ Return data from old dataservice exported XMLs
    """
    splitdir = os.path.split(os.path.abspath(os.path.dirname(__file__)))
    product_dir = os.path.join(*splitdir)
    file_path = os.path.join(product_dir, file_id)
    
    f = open(file_path);
    s = f.read()
    parser = dataservice_parser(info, ds_from, ds_to)
    data = parser.parseContent(s)
    return data.get_datasets()

if __name__ == '__main__':
    print len(extract_data())