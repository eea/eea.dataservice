# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from zope.interface import implements
from Products.Archetypes.atapi import *
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

schema = Schema((

    TextField(
        name='information',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Additional information",
            description="information descrition.",
            label_msgid='dataservice_label_information',
            description_msgid='dataservice_help_information',
            i18n_domain='eea.dataservice',
        )
    ),
    
    TextField(
        name='dataset_contact',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Contact person(s) for EEA",
            description="dataset_contact descrition.",
            label_msgid='dataservice_label_dataset_contact',
            description_msgid='dataservice_help_dataset_contact',
            i18n_domain='eea.dataservice',
        )
    ),
    
    TextField(
        name='dataset_disclaimer',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Disclaimer",
            description="dataset_disclaimer descrition.",
            label_msgid='dataservice_label_dataset_disclaimer',
            description_msgid='dataservice_help_dataset_disclaimer',
            i18n_domain='eea.dataservice',
        )
    ),
    
    TextField(
        name='management_plan',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="EEA management plan code",
            description="management_plan descrition.",
            label_msgid='dataservice_label_management_plan',
            description_msgid='dataservice_help_management_plan',
            i18n_domain='eea.dataservice',
        )
    ),
    
    TextField(
        name='geographic_accuracy',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Geographic accuracy",
            description="geographic_accuracy descrition.",
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
            description="geographic_coordinates descrition.",
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
            description="geographic_coverage descrition.",
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
            description="methodology descrition.",
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
            description="originator descrition.",
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
            description="dataset_owner descrition.",
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
            description="processor descrition.",
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
            description="reference_system descrition.",
            label_msgid='dataservice_label_reference_system',
            description_msgid='dataservice_help_reference_system',
            i18n_domain='eea.dataservice',
        )
    ),
    
    TextField(
        name='scale',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Scale of the data set",
            description="scale descrition.",
            label_msgid='dataservice_label_scale',
            description_msgid='dataservice_help_scale',
            i18n_domain='eea.dataservice',
        )
    ),
    
    TextField(
        name='dataset_source',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="Source",
            description="dataset_source descrition.",
            label_msgid='dataservice_label_dataset_source',
            description_msgid='dataservice_help_dataset_source',
            i18n_domain='eea.dataservice',
        )
    ),
    
    TextField(
        name='system_folder',
        index="ZCTextIndex|TextIndex:brains",
        widget=TextAreaWidget(
            label="System folder",
            description="system_folder descrition.",
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
            description="temporal_coverage descrition.",
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
            description="Unit descrition.",
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