# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from zope.interface import implements
from Products.Archetypes.atapi import *
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary

from eea.dataservice.config import *
from eea.dataservice.fields import EventFileField
from eea.dataservice.interfaces import IEEAFigureFile
from eea.dataservice.vocabulary import CATEGORIES_DICTIONARY_ID

# Schema
schema = Schema((

    EventFileField('file',
              required=False,
              primary=True,
              widget = FileWidget(
                        description = "Select the file to be added by clicking the 'Browse' button.",
                        description_msgid = "help_file",
                        label= "File",
                        label_msgid = "label_file",
                        i18n_domain = "plone",
                        show_content_type = False,)),

    StringField(
        name='category',
        default='edse',
        vocabulary=NamedVocabulary(CATEGORIES_DICTIONARY_ID),
        widget = SelectionWidget(
            format="select", # possible values: flex, select, radio
            label="Category",
            description = ("Category description."),
            label_msgid='dataservice_label_category',
            description_msgid='dataservice_help_category',
            i18n_domain='eea.dataservice',
        )
    ),

    StringField(
        name='shortId',
        widget = StringWidget(
            label="Short ID",
            visible=-1,
            description = ("Short ID description."),
            label_msgid='dataservice_label_shortid',
            description_msgid='dataservice_help_shortid',
            i18n_domain='eea.dataservice',
        )
    ),

),)

eeafigurefile_schema = ATFolderSchema.copy() + schema.copy()

class EEAFigureFile(ATFolder):
    """ EEAFigureFile Content Type
    """
    implements(IEEAFigureFile)
    security = ClassSecurityInfo()

    archetype_name  = 'EEAFigureFile'
    portal_type     = 'EEAFigureFile'
    meta_type       = 'EEAFigureFile'
    allowed_content_types = ['ATImage', 'ImageFS', 'File', 'Folder', 'DataFile', 'DataTable']
    _at_rename_after_creation = True

    schema = eeafigurefile_schema

registerType(EEAFigureFile, PROJECTNAME)
