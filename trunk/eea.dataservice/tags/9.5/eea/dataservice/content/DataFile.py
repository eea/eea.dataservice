""" Data File content type
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATContentTypes.interfaces import IFileContent
from Products.Archetypes.atapi import FileWidget, StringWidget
from Products.Archetypes.atapi import Schema, StringField
from Products.CMFCore.permissions import View
from Products.validation import V_REQUIRED
from eea.dataservice.interfaces import IDatafile
from plone.app.blob.field import BlobField
from zope.interface import implements

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
        name='shortId',
        widget=StringWidget(
            label="Short ID",
            visible=-1,
            description=("Short ID description."),
            label_msgid='dataservice_label_shortid',
            description_msgid='dataservice_help_shortid',
            i18n_domain='eea',
        )
    ),
    ),
)

Datafile_schema = ATFolderSchema.copy() + \
    schema.copy()

class DataFile(ATFolder):
    """ Dataset External File Content Type
    """
    implements(IDatafile, IFileContent)
    archetype_name = portal_type = meta_type = 'DataFile'
    _at_rename_after_creation = True
    schema = Datafile_schema

    security = ClassSecurityInfo()

    security.declareProtected(View, 'get_size')
    def get_size(self):
        """ ZMI / Plone get size method
        """
        f = self.getField('file')
        if f is None:
            return 0
        return f.get_size(self) or 0

    security.declareProtected(View, 'size')
    def size(self):
        """ Get size
        """
        return self.get_size()

    security.declareProtected(View, 'download')
    def download(self, REQUEST=None, RESPONSE=None):
        """ Download the file
        """
        if REQUEST is None:
            REQUEST = self.REQUEST
        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE
        field = self.getField('file')
        return field.download(self, REQUEST, RESPONSE)
