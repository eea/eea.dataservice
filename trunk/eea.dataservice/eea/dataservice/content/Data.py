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


schema = Schema((
    StringField(
        name='alec',
        widget=StringField._properties['widget'](
            label="Alec",
            description="Proprietatea lu alec.",
            size=60,
            label_msgid='dataservice_label_alec',
            description_msgid='dataservice_help_alec',
            i18n_domain='dataservice',
        ),
        languageIndependent=1,
        searchable=1,
        default='alec default',
        write_permission=permissions.ModifyPortalContent,
        size=60,
    ),
    
    
    
    
),
)

Dataset_schema = ATFolderSchema.copy() + \
    schema.copy()

class Data(ATFolder):
    """ Dataset Content Type
    """
    #implements(IDataset)
    security = ClassSecurityInfo()
    __implements__ = (getattr(ATFolder,'__implements__',()),)
    
    archetype_name  = 'Data'
    portal_type     = 'Data'
    meta_type       = 'Data'
    _at_rename_after_creation = True

    schema = Dataset_schema
    
    security.declareProtected(permissions.View, 'getAlec')
    def getAlec(self):
        """ """
        return 'Testus: %s' % self.alec

registerType(Data, PROJECTNAME)