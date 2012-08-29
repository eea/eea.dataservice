""" EEA Figure File
"""
from zope.interface import implements
from Products.Archetypes.atapi import Schema, StringField, StringWidget
from Products.Archetypes.atapi import SelectionWidget, FileWidget
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from plone.app.blob.field import BlobField
from eea.dataservice.interfaces import IEEAFigureFile
from eea.dataservice.vocabulary import CATEGORIES_DICTIONARY_ID
from Products.validation import V_REQUIRED

# Schema
schema = Schema((
    BlobField('file',
              required=False,
              primary=True,
              validators = (('checkFileMaxSize', V_REQUIRED), ),
              widget=FileWidget(
                        description=("Select the file to be added by "
                                       "clicking the 'Browse' button."),
                        description_msgid="help_file",
                        label="File",
                        label_msgid="label_file",
                        i18n_domain="plone",
                        show_content_type=False,)),
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
        name='shortId',
        widget=StringWidget(
            label="Short ID",
            visible= -1,
            description=("Short ID description."),
            label_msgid='dataservice_label_shortid',
            description_msgid='dataservice_help_shortid',
            i18n_domain='eea',
        )
    ),
),)

eeafigurefile_schema = ATFolderSchema.copy() + schema.copy()
class EEAFigureFile(ATFolder):
    """ EEAFigureFile Content Type
    """
    implements(IEEAFigureFile)
    archetype_name = portal_type = meta_type = 'EEAFigureFile'
    allowed_content_types = [
        'ATImage', 'ImageFS', 'File', 'Folder', 'DataFile', 'DataTable']
    _at_rename_after_creation = True
    schema = eeafigurefile_schema
