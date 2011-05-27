# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'


from zope.interface import implements
from Products.Archetypes.atapi import Schema, StringField, registerType
from Products.CMFCore import permissions
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
#from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFCore.permissions import ModifyPortalContent
#from Products.ATContentTypes.content.folder import ATFolderSchema
#from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.OrderableReferenceField._field import OrderableReferenceField
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

from eea.themecentre.interfaces import IThemeTagging
from Products.EEAContentTypes.content.ThemeTaggable import ThemeTaggable

from eea.dataservice.config import PROJECTNAME
from eea.dataservice.interfaces import IEEAFigure
from eea.dataservice.vocabulary import FigureTypes
from eea.dataservice.content.schema import dataservice_schema
from eea.dataservice.widgets.FigureTypeWidget import FigureTypeWidget


# Schema
schema = Schema((
    # Metadata
    StringField(
        name='figureType',
        languageIndependent=False,
        required=True,
        vocabulary=FigureTypes(),
        widget=FigureTypeWidget(
            label="Figure type",
            format="select",
            description="Figure type description.",
            label_msgid="dataservice_type",
            description_msgid="dataservice_help_type",
            i18n_domain="eea",
        ),
    ),

    # Fields for 'relations' schemata
    OrderableReferenceField('relatedProducts',
        schemata = 'relations',
        relationship = 'relatesToProducts',
        multiValued = True,
        isMetadata = True,
        languageIndependent = False,
        index = 'KeywordIndex',
        write_permission = ModifyPortalContent,
        widget = ReferenceBrowserWidget(
            macro = "figure_referencebrowser",
            helper_css = ("figure_widget.css",),
            helper_js = ('referencebrowser.js', 'select_lists.js', 'figure_widget.js'),
            allow_search = True,
            allow_browse = True,
            allow_sorting = True,
            show_indexes = False,
            force_close_on_insert = True,
            label = "Relations to other EEA products",
            label_msgid = "label_related_products",
            description = "Specify relations to other EEA products within Plone.",
            description_msgid = "help_related_products",
            i18n_domain = "plone",
            visible = {'edit' : 'visible', 'view' : 'invisible' }
        )
    ),
),)

eeafigure_schema = dataservice_schema.copy() + schema.copy()

# Set position on form
eeafigure_schema.moveField('figureType', pos=3)

class EEAFigure(ATFolder, ThemeTaggable):
    """ EEAFigure Content Type
    """
    implements(IEEAFigure)
    security = ClassSecurityInfo()

    archetype_name  = 'EEAFigure'
    portal_type     = 'EEAFigure'
    meta_type       = 'EEAFigure'
    allowed_content_types = ['ATImage', 'File', 'Folder', 'DataFile', 'DataTable']
    _at_rename_after_creation = True

    schema = eeafigure_schema

    security.declareProtected(permissions.View, 'getOrganisationName')
    def getOrganisationName(self, url):
        """ """
        res = None
        cat = getToolByName(self, 'portal_catalog')
        brains = cat.searchResults({'portal_type' : 'Organisation',
                                    'getUrl': url})
        if brains:
            res = brains[0]
        return res

    security.declareProtected(permissions.View, 'getKeywords')
    def getKeywords(self):
        res = list(self.Subject())
        res.sort(key=str.lower)
        return ', '.join(res)

    security.declarePublic('Rights')
    def Rights(self):
        """
         return standard EEA copyrights policy information otherwise return the specific one if present.
        """
        value = self.schema['rights'].getRaw(self)

        if value:
            return value
        else:
            ownerfield = self.getField('dataOwner')
            urls = ownerfield.getAccessor(self)()
            orgnames = ""
            copyrightholders = ""
            for url in urls:
                orgob = self.getOrganisationName(url)
                orgname = orgob.Title
                orgnames = orgnames + orgname + ', '
            if len(orgnames)>0:
                copyrightholders = 'Copyright holder: ' + orgnames
                copyrightholders = copyrightholders[:-2] + '.'

            return "EEA standard re-use policy: unless otherwise indicated, re-use of content on the EEA website for commercial or non-commercial purposes is permitted free of charge, provided that the source is acknowledged (http://www.eea.europa.eu/legal/copyright). " + copyrightholders

    security.declarePublic('getThemeVocabs')
    def getThemeVocabs(self):
        """
        """
        pass

    def setThemes(self, value, **kw):
        """ Use the tagging adapter to set the themes. """
        value = [val for val in value if val] #value = filter(None, value)
        tagging = IThemeTagging(self)
        tagging.tags = value

registerType(EEAFigure, PROJECTNAME)
