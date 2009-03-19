# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from zope.interface import implements
from Products.Archetypes.atapi import *
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.CMFCore import permissions
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATContentTypes.content.folder import ATFolder
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL

from eea.dataservice.config import *
from eea.dataservice.interfaces import IDataset
from eea.dataservice.vocabulary import DatasetYearsVocabulary, EEA_MPCODE_VOCABULARY
from eea.dataservice.vocabulary import COUNTRIES_DICTIONARY_ID


#def addData(self, REQUEST={}):
    #""" Factory method for a Dataset object
    #"""
    #pass

#TODO: delete above if no need, is old regexp to check for 1:10000 format
#from Products.validation.validators.RegexValidator import RegexValidator
#from Products.validation import validation
#validation.register(RegexValidator('isScale',
                                   #r'^1:(\d+)$', 
                                   #errmsg = 'Invalid value, must be e.g. 1:1000000.'))
    
schema = Schema((

    IntegerField(
        name='scale',
        validators = ('isInt',),
        widget=IntegerWidget(
            macro='scale_widget',
            label='Scale of the data set',
            label_msgid='dataservice_label_scale',
            description_msgid='dataservice_help_scale',
            i18n_domain='eea.dataservice',
            size=20,
        )
    ),

    LinesField(
        name='temporal_coverage',
        languageIndependent=True,
        multiValued=1,
        vocabulary=DatasetYearsVocabulary(),
        widget=MultiSelectionWidget(
            macro="coverage_widget",
            label="Temporal coverage",
            description="Temporal coverage description.",
            label_msgid='dataservice_label_coverage',
            description_msgid='dataservice_help_coverage',
            i18n_domain='eea.dataservice',
        )
    ),

    LinesField(
        name='geographic_coverage',
        languageIndependent=True,
        multiValued=1,
        vocabulary=NamedVocabulary("dataservice_countries"),
        widget=MultiSelectionWidget(
            macro="geographic_widget",
            size=8,
            label="Geographical coverage",
            description="Geographical coverage description.",
            label_msgid='dataservice_label_geographic',
            description_msgid='dataservice_help_geographic',
            i18n_domain='eea.dataservice',
        )
    ),

    IntegerField(
        name='eea_mpcode',
        validators = ('isInt',),
        widget=IntegerWidget(
            size=8,
            label='EEA management plan code',
            label_msgid='dataservice_label_eea_mpcode',
            description_msgid='dataservice_help_eea_mpcode',
            i18n_domain='eea.dataservice',
        )
    ),

    TextField(
        name='disclaimer',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Disclaimer",
            description="Disclaimer description.",
            label_msgid='dataservice_label_disclaimer',
            description_msgid='dataservice_help_disclaimer',
            i18n_domain='eea.dataservice',
        )
    ),

    TextField(
        name='contact',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Contact person(s) for EEA",
            description="dataset_contact description.",
            label_msgid='dataservice_label_dataset_contact',
            description_msgid='dataservice_help_dataset_contact',
            i18n_domain='eea.dataservice',
        )
    ),

    TextField(
        name='geoAccuracy',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Geographic accuracy",
            description="Geographic accuracy description.",
            label_msgid='dataservice_label_accurracy',
            description_msgid='dataservice_help_accurracy',
            i18n_domain='eea.dataservice',
        )
    ),

    TextField(
        name='source',
        languageIndependent=False,
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/html',
        index="ZCTextIndex|TextIndex:brains",
        widget=RichWidget(
            label="Source",
            description="Source description.",
            label_msgid="dataservice_label_source",
            description_msgid="dataservice_help_source",
            i18n_domain="eea.dataservice",
            rows=10,
        ),
    ),
    #LinesField(
        #name='source',
        #languageIndependent=True,
        #multiValued=1,
        #default=(u'EEA (European Environment Agency)',),
        #vocabulary=NamedVocabulary("report_creators"),
        #widget=KeywordWidget(
            #label="Source",
            #description="Source description.",
            #label_msgid='dataservice_label_source',
            #description_msgid='dataservice_help_source',
            #i18n_domain='eea.dataservice',
        #)
    #),

    TextField(
        name='moreInfo',
        languageIndependent=False,
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/html',
        index="ZCTextIndex|TextIndex:brains",
        widget=RichWidget(
            label="Additional information",
            description="Additional information description.",
            label_msgid="dataservice_label_moreInfo",
            description_msgid="dataservice_help_moreInfo",
            i18n_domain="eea.dataservice",
            rows=10,
        ),
    ),

    TextField(
        name='methodology',
        languageIndependent=False,
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/html',
        index="ZCTextIndex|TextIndex:brains",
        widget=RichWidget(
            label="Methodology",
            description="methodology description.",
            label_msgid="dataservice_label_methodology",
            description_msgid="dataservice_help_methodology",
            i18n_domain="eea.dataservice",
            rows=10,
        ),
    ),
    
    TextField(
        name='unit',
        languageIndependent=False,
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/html',
        index="ZCTextIndex|TextIndex:brains",
        widget=RichWidget(
            label="Unit",
            description="Unit description.",
            label_msgid="dataservice_label_unit",
            description_msgid="dataservice_help_unit",
            i18n_domain="eea.dataservice",
            rows=10,
        ),
    ),
    
    
    
    
    
    
    
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    

    


    
    TextField(
        name='geographic_coordinates',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Geographic box coordinates",
            description="geographic_coordinates description.",
            label_msgid='dataservice_label_geographic_coordinates',
            description_msgid='dataservice_help_geographic_coordinates',
            i18n_domain='eea.dataservice',
        )
    ),
    
   
   
    TextField(
        name='originator',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Originator",
            description="originator description.",
            label_msgid='dataservice_label_originator',
            description_msgid='dataservice_help_originator',
            i18n_domain='eea.dataservice',
        )
    ),
    
    TextField(
        name='dataset_owner',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Owner",
            description="dataset_owner description.",
            label_msgid='dataservice_label_dataset_owner',
            description_msgid='dataservice_help_dataset_owner',
            i18n_domain='eea.dataservice',
        )
    ),
    
    TextField(
        name='processor',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Processor",
            description="processor description.",
            label_msgid='dataservice_label_processor',
            description_msgid='dataservice_help_processor',
            i18n_domain='eea.dataservice',
        )
    ),
    
    TextField(
        name='reference_system',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Reference system",
            description="reference_system description.",
            label_msgid='dataservice_label_reference_system',
            description_msgid='dataservice_help_reference_system',
            i18n_domain='eea.dataservice',
        )
    ),
    
    
    
    TextField(
        name='system_folder',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="System folder",
            description="system_folder description.",
            label_msgid='dataservice_label_system_folder',
            description_msgid='dataservice_help_system_folder',
            i18n_domain='eea.dataservice',
        )
    ),
),
)

Dataset_schema = ATFolderSchema.copy() + \
    schema.copy()

class Data(ATFolder):
    """ Dataset Content Type
    """
    implements(IDataset)
    security = ClassSecurityInfo()

    archetype_name  = 'Data'
    portal_type     = 'Data'
    meta_type       = 'Data'
    _at_rename_after_creation = True

    schema = Dataset_schema

    def getMpCodeName(self, code):
        """  return management plan code title """
        return EEA_MPCODE_VOCABULARY[code]

    security.declareProtected(permissions.View, 'getCountryInfo')
    def getCountryInfo(self):
        """ """
        atvm = getToolByName(self, ATVOCABULARYTOOL)
        vocab = atvm[COUNTRIES_DICTIONARY_ID]
        
        res = {'groups': {}, 'countries': {}}
        for ob in vocab.objectValues():
            ob_key = ob.getId()
            ob_value = ob.Title()
            
            if len(ob.objectValues()) > 0:
                res['groups'][ob_key] = ob_value
            else:
                res['countries'][ob_key] = ob_value
        return res

    security.declareProtected(permissions.View, 'getCountryGroups')
    def getCountryGroups(self):
        """ """
        res = self.getCountryInfo()['groups']
        return [(key, res[key]) for key in res.keys()]

    security.declareProtected(permissions.View, 'getCountries')
    def getCountries(self):
        """ """
        res = self.getCountryInfo()['countries']
        return [(key, res[key]) for key in res.keys()]

    security.declareProtected(permissions.View, 'formatTempCoverage')
    def formatTempCoverage(self):
        """ """
        field = self.getField('temporal_coverage')
        data = field.getAccessor(self)()
        data = list(data)
        data.reverse()
        res_list = []
        res = ''
        cyear = None

        for year in data:
            if len(res_list) > 0:
                if cyear is None:
                    tmpyear = int(res_list[-1])
                else:
                    tmpyear = int(cyear)
                tmpyear = tmpyear + 1
                if int(year) == tmpyear:
                    cyear = year
                else:
                    if cyear is None:
                        res_list.append(str(year))
                    else:
                        res_list.append('-%s' % str(year))
                        cyear = None
            else:
                res_list.append(str(year))
        if cyear is not None:
            res_list.append('-%s' % str(year))

        res = ', '.join(res_list)
        return res.replace(', -', '-')

registerType(Data, PROJECTNAME)