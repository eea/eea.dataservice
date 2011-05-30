# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from Products.Archetypes.atapi import Schema, FileWidget, StringField
from Products.Archetypes.atapi import StringWidget, registerType
#from Products.CMFCore import permissions
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATContentTypes.content.folder import ATFolder
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from plone.app.blob.field import BlobField

from eea.dataservice.config import PROJECTNAME
from eea.dataservice.interfaces import IDatafile

schema = Schema((
    BlobField('file',
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
        name='shortId',
        widget = StringWidget(
            label="Short ID",
            visible=-1,
            description = ("Short ID description."),
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
    security = ClassSecurityInfo()

    archetype_name  = 'DataFile'
    portal_type     = 'DataFile'
    meta_type       = 'DataFile'
    _at_rename_after_creation = True

    schema = Datafile_schema

registerType(DataFile, PROJECTNAME)
