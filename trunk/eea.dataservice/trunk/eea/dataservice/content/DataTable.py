""" Data table content type
"""
from zope.interface import implements
from Products.Archetypes.atapi import Schema, StringField, StringWidget
from Products.Archetypes.atapi import SelectionWidget, TextField, RichWidget
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from eea.dataservice.interfaces import IDatatable
from eea.dataservice.vocabulary import CATEGORIES_DICTIONARY_ID

schema = Schema((
    StringField(
        name='category',
        default='edse',
        vocabulary=NamedVocabulary(CATEGORIES_DICTIONARY_ID),
        widget=SelectionWidget(
            format="select", # possible values: flex, select, radio
            label="Category",
            description=("Category description."),
            label_msgid='dataservice_label_category',
            description_msgid='dataservice_help_category',
            i18n_domain='eea',
        )
    ),

    StringField(
        name='records',
        widget=StringWidget(
            label="Records",
            description=("Records description."),
            label_msgid='dataservice_label_records',
            description_msgid='dataservice_help_records',
            i18n_domain='eea',
        )
    ),

    TextField(
        name='tableDefinition',
        languageIndependent=False,
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/html',
        widget=RichWidget(
            label="Table definition",
            description="Table definition description.",
            label_msgid="dataservice_label_table_definition",
            description_msgid="dataservice_help_table_definition",
            i18n_domain="eea",
            rows=10,
        ),
    ),
    ),
)

Datatable_schema = ATFolderSchema.copy() + schema.copy()

class DataTable(ATFolder):
    """ Dataset Table Content Type
    """
    implements(IDatatable)
    archetype_name = portal_type = meta_type = 'DataTable'
    allowed_content_types = ['ATImage', 'File', 'Folder', 'DataFile']
    _at_rename_after_creation = True
    schema = Datatable_schema
