# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from Products.Archetypes.atapi import *
from Products.CMFCore import permissions
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATContentTypes.content.folder import ATFolder
from zope.interface import implements
from AccessControl import ClassSecurityInfo

from eea.dataservice.config import *
from eea.dataservice.interfaces import IDatafile


schema = Schema((
    StringField(
        name='short_id',
        widget = StringWidget(
            label="Short ID",
            description = ("Short ID description."),
            label_msgid='dataservice_label_shortid',
            description_msgid='dataservice_help_shortid',
            i18n_domain='eea.dataservice',
        )
    ),
    StringField(
        name='table_id',
        widget = StringWidget(
            label="Table ID",
            description = ("Table ID description."),
            label_msgid='dataservice_label_tableid',
            description_msgid='dataservice_help_tableid',
            i18n_domain='eea.dataservice',
        )
    ),
    StringField(
        name='dataset_id',
        widget = StringWidget(
            label="Dataset ID",
            description = ("Dataset ID description."),
            label_msgid='dataservice_label_datasetid',
            description_msgid='dataservice_help_datasetid',
            i18n_domain='eea.dataservice',
        )
    ),
    StringField(
        name='category',
        widget = StringWidget(
            label="Category",
            description = ("Category description."),
            label_msgid='dataservice_label_category',
            description_msgid='dataservice_help_category',
            i18n_domain='eea.dataservice',
        )
    ),
    StringField(
        name='filename',
        widget = StringWidget(
            label="Filename",
            description = ("Filename description."),
            label_msgid='dataservice_label_filename',
            description_msgid='dataservice_help_filename',
            i18n_domain='eea.dataservice',
        )
    ),
    StringField(
        name='filesize',
        widget = StringWidget(
            label="Filesize",
            description = ("Filesize description."),
            label_msgid='dataservice_label_filesize',
            description_msgid='dataservice_help_filesize',
            i18n_domain='eea.dataservice',
        )
    ),
    StringField(
        name='download_link',
        widget = StringWidget(
            label="Download link",
            description = ("Download link description."),
            label_msgid='dataservice_label_download_link',
            description_msgid='dataservice_help_download_link',
            i18n_domain='eea.dataservice',
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