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
from eea.dataservice.interfaces import IDatatable


schema = Schema((
    StringField(
        name='records',
        widget = StringWidget(
            label="Records",
            description = ("Records description."),
            label_msgid='dataservice_label_records',
            description_msgid='dataservice_help_records',
            i18n_domain='eea.dataservice',
        )
    ),
    StringField(
        name='category',
        default='European data set',
        widget = StringWidget(
            label="Category",
            description = ("Category description."),
            label_msgid='dataservice_label_category',
            description_msgid='dataservice_help_category',
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
    ),
)

Datatable_schema = ATFolderSchema.copy() + \
    schema.copy()

class DataTable(ATFolder):
    """ Dataset Table Content Type
    """
    implements(IDatatable)
    security = ClassSecurityInfo()

    archetype_name  = 'DataTable'
    portal_type     = 'DataTable'
    meta_type       = 'DataTable'
    _at_rename_after_creation = True

    schema = Datatable_schema

registerType(DataTable, PROJECTNAME)