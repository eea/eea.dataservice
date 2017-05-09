""" EEA Figure File content type
"""
from zope.interface import implements
from Products.Archetypes.atapi import Schema, StringField, StringWidget
from Products.Archetypes.atapi import SelectionWidget, FileWidget
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATContentTypes.interfaces import IFileContent
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.validation import V_REQUIRED
from Products.CMFCore.permissions import View
from plone.app.blob.field import BlobField
from eea.dataservice.interfaces import IEEAFigureFile
from eea.dataservice.vocabulary import CATEGORIES_DICTIONARY_ID
from AccessControl import ClassSecurityInfo

# Schema
schema = Schema((
    BlobField('file',
              required=False,
              primary=True,
              validators=(('checkFileMaxSize', V_REQUIRED), ),
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
            format="select",  # possible values: flex, select, radio
            label="Category",
            description="Category description.",
            label_msgid='dataservice_label_category',
            description_msgid='dataservice_help_category',
            i18n_domain='eea',
        )
    ),
    StringField(
        name='shortId',
        widget=StringWidget(
            label="Short ID",
            visible=-1,
            description="Short ID description.",
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
    implements(IEEAFigureFile, IFileContent)
    archetype_name = portal_type = meta_type = 'EEAFigureFile'
    allowed_content_types = [
        'ATImage', 'File', 'Folder', 'DataFile', 'DataTable']
    _at_rename_after_creation = True
    schema = eeafigurefile_schema

    security = ClassSecurityInfo()

    @security.protected('get_size')
    def get_size(self):
        """ ZMI / Plone get size method
        """
        f = self.getField('file')
        if f is None:
            return 0
        return f.get_size(self) or 0

    @security.protected(View)
    def size(self):
        """ Get size
        """
        return self.get_size()

    @security.protected(View)
    def download(self, REQUEST=None, RESPONSE=None):
        """ Download the file
        """
        if REQUEST is None:
            REQUEST = self.REQUEST
        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE
        field = self.getField('file')
        return field.download(self, REQUEST, RESPONSE)
