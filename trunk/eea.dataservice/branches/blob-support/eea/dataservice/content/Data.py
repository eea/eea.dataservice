# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from zope.interface import implements
from Products.Archetypes.atapi import *
from Products.CMFCore import permissions
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from zope.app.annotation.interfaces import IAnnotations
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary

from eea.themecentre.interfaces import IThemeTagging
from Products.EEAContentTypes.content.ThemeTaggable import ThemeTaggable

from eea.dataservice.config import *
from eea.dataservice.interfaces import IDataset
from eea.dataservice.versions.versions import _get_random
from eea.dataservice.content.schema import dataservice_schema
from eea.dataservice.fields.GeoQualityField import GeoQualityField
from eea.dataservice.versions.versions import VERSION_ID, _reindex
from eea.dataservice.widgets.GeoQualityWidget import GeoQualityWidget
from eea.dataservice.vocabulary import Obligations, REFERENCE_DICTIONARY_ID


# Schema
schema = Schema((
    TextField(
        name='geoAccuracy',
        languageIndependent=True,
        widget=TextAreaWidget(
            label="Geographic accuracy",
            description="It is applicable to GIS datasets. It indicates the geographic accuracy of location, ground distance as a value in meters.",
            label_msgid='dataservice_label_accurracy',
            description_msgid='dataservice_help_accurracy',
            i18n_domain='eea.dataservice',
        )
    ),

    TextField(
        name='disclaimer',
        languageIndependent=False,
        required=False,
        widget=TextAreaWidget(
            label="Disclaimer",
            description="Disclaimer description.",
            label_msgid='dataservice_label_disclaimer',
            description_msgid='A disclaimer is a statement which generally states that the entity authoring the disclaimer is not responsible for something in some manner.',
            i18n_domain='eea.dataservice',
        )
    ),

    IntegerField(
        name='scale',
        languageIndependent=True,
        required=False,
        validators = ('isInt',),
        widget=IntegerWidget(
            macro='scale_widget',
            label='Scale of the dataset',
            label_msgid='dataservice_label_scale',
            description = ("Gives a rough value of accuracy for the GIS dataset. Example: 1:1000"),
            description_msgid='dataservice_help_scale',
            i18n_domain='eea.dataservice',
            size=20,
        )
    ),

    StringField(
        name='referenceSystem',
        languageIndependent=True,
        required=False,
        vocabulary=NamedVocabulary(REFERENCE_DICTIONARY_ID),
        widget=SelectionWidget(
            macro="reference_widget",
            label="Coordinate reference system",
            description="Coordinate reference system used for the GIS dataset. Example: Lambert Azimutal",
            label_msgid="dataservice_label_system",
            description_msgid="dataservice_help_system",
            i18n_domain="eea.dataservice",
        ),
    ),

    GeoQualityField(
        name='geoQuality',
        languageIndependent=True,
        default=('-1', '-1', '-1', '-1', '-1'),
        vocabulary=NamedVocabulary("quality"),
        widget = GeoQualityWidget(
            format="select",
            label="Geographic information quality",
            description = ("Geographic information quality."),
            label_msgid='dataservice_label_geoQuality',
            description_msgid='dataservice_help_geoQuality',
            i18n_domain='eea.dataservice',
        )
    ),

    LinesField(
        schemata = "relations",
        name='reportingObligations',
        languageIndependent=True,
        multiValued=1,
        vocabulary=Obligations(),
        widget=MultiSelectionWidget(
            macro="obligations_widget",
            label="Environmental reporting obligations (ROD)",
            description="The environmental reporting obligations used to optain the data. Reporting obligations are requirements to provide information agreed between countries and international bodies such as the EEA or international conventions.",
            label_msgid='dataservice_label_obligations',
            description_msgid='dataservice_help_obligations',
            i18n_domain='eea.dataservice',
        )
    ),
),)

dataset_schema = dataservice_schema.copy() + schema.copy()

class Data(ATFolder, ThemeTaggable):
    """ Dataset Content Type
    """
    implements(IDataset)
    security = ClassSecurityInfo()

    archetype_name  = 'Data'
    portal_type     = 'Data'
    meta_type       = 'Data'
    allowed_content_types = ['ATImage', 'File', 'Folder', 'DataTable']
    _at_rename_after_creation = True

    schema = dataset_schema

    security.declareProtected(permissions.View, 'getKeywords')
    def getKeywords(self):
        res = list(self.Subject())
        res.sort(key=str.lower)
        return ', '.join(res)

    security.declareProtected(permissions.View, 'getOrganisationName')
    def getOrganisationName(self, url):
        """ """
        res = None
        cat = getToolByName(self, 'portal_catalog')
        brains = cat.searchResults({'portal_type' : 'Organisation',
                                    'getUrl': url})
        if brains: res = brains[0]
        return res

    security.declarePublic('getThemeVocabs')
    def getThemeVocabs(self):
        """
        """
        pass

    def setThemes(self, value, **kw):
        """ Use the tagging adapter to set the themes. """
        value = filter(None, value)
        tagging = IThemeTagging(self)
        tagging.tags = value


def versionIdHandler(obj, event):
    """ Set a versionId as annotation without setting the
        version marker interface just to have a perma link
        to last version
    """
    hasVersions = obj.unrestrictedTraverse('@@hasVersions')
    if not hasVersions():
        verId = _get_random(10)
        anno = IAnnotations(obj)
        ver = anno.get(VERSION_ID)
        #TODO: tests fails with ver = None when adding an EEAFigure,
        #      remove "if ver:" after fix
        if ver:
            if not ver.values()[0]:
                ver[VERSION_ID] = verId
                _reindex(obj)

registerType(Data, PROJECTNAME)
