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

from eea.dataservice.config import *
from eea.dataservice.interfaces import IDataset


#def addData(self, REQUEST={}):
    #""" Factory method for a Dataset object
    #"""
    #pass

from Products.validation.validators.RegexValidator import RegexValidator
from Products.validation import validation
validation.register(RegexValidator('isScale',
                                   r'1:[0-9]', 
                                   errmsg = 'Invalid value, must be e.g. 1:1000000.'))
    
schema = Schema((
    IntegerField(
        name='eea_mpcode',
        validators = ('isInt',),
        widget=IntegerWidget(
            label='EEA management plan code',
            label_msgid='dataservice_label_eea_mpcode',
            description_msgid='dataservice_help_eea_mpcode',
            i18n_domain='eea.dataservice',
        )
    ),
    
    TextField(
        name='moreInfo',
        languageIndependent=False,
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/html',
        index="ZCTextIndex|TextIndex:brains",
        widget=RichWidget
        (
            label="Additional information",
            description="Additional information description.",
            label_msgid="dataservice_label_moreInfo",
            description_msgid="dataservice_help_moreInfo",
            i18n_domain="eea.dataservice",
            rows=10,
        ),
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

    LinesField(
        name='source',
        languageIndependent=True,
        multiValued=1,
        default=(u'EEA (European Environment Agency)',),
        vocabulary=NamedVocabulary("report_creators"),
        widget=KeywordWidget(
            label="Source",
            description="Source description.",
            label_msgid='dataservice_label_source',
            description_msgid='dataservice_help_source',
            i18n_domain='eea.dataservice',
        )
    ),

    StringField(
        name='scale',
        validators = ('isScale',),
        searchable=1,
        label="Scale of the data set",
        widget=StringWidget(
            label="Scale of the data set",
            description="Scale of the data set description.",
            size=20,
            label_msgid='publications_label_title',
            description_msgid='dataservice_help_scale',
            i18n_domain='eea.dataservice',
        ),
),


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    TextField(
        name='dataset_contact',
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
        name='geographic_accuracy',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Geographic accuracy",
            description="geographic_accuracy description.",
            label_msgid='dataservice_label_geographic_accuracy',
            description_msgid='dataservice_help_geographic_accuracy',
            i18n_domain='eea.dataservice',
        )
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
        name='geographic_coverage',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Geographical coverage",
            description="geographic_coverage description.",
            label_msgid='dataservice_label_geographic_coverage',
            description_msgid='dataservice_help_geographic_coverage',
            i18n_domain='eea.dataservice',
        )
    ),
    
    TextField(
        name='methodology',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Methodology",
            description="methodology description.",
            label_msgid='dataservice_label_methodology',
            description_msgid='dataservice_help_methodology',
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
    
    TextField(
        name='temporal_coverage',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Temporal coverage",
            description="temporal_coverage description.",
            label_msgid='dataservice_label_temporal_coverage',
            description_msgid='dataservice_help_temporal_coverage',
            i18n_domain='eea.dataservice',
        )
    ),
    
    TextField(
        name='unit',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Unit",
            description="Unit description.",
            label_msgid='dataservice_label_unit',
            description_msgid='dataservice_help_unit',
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

    security.declareProtected(permissions.View, 'getUnit')
    def getUnit(self):
        """ """
        return 'unit'

registerType(Data, PROJECTNAME)