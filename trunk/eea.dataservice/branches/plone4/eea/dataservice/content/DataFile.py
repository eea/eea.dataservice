""" Data File
"""
from Products.Archetypes.atapi import Schema, StringField
from Products.Archetypes.atapi import FileWidget, StringWidget
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATContentTypes.content.folder import ATFolder
from zope.interface import implements
from plone.app.blob.field import BlobField
from eea.dataservice.interfaces import IDatafile

schema = Schema((
    BlobField('file',
              required=False,
              primary=True,
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
            visible= -1,
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
    implements(IDatafile)
    archetype_name = portal_type = meta_type = 'DataFile'
    _at_rename_after_creation = True
    schema = Datafile_schema
