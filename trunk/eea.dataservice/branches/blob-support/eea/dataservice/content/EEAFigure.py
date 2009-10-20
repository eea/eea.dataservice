# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from datetime import datetime
from DateTime import DateTime

from zope.interface import implements
from Products.Archetypes.atapi import *
from Products.CMFCore import permissions
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFCore.permissions import ModifyPortalContent
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.OrderableReferenceField._field import OrderableReferenceField
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

from Products.EEAContentTypes.content.ThemeTaggable import ThemeTaggable
from eea.themecentre.interfaces import IThemeTagging

from eea.dataservice.config import *
from eea.dataservice.interfaces import IEEAFigure
from eea.dataservice.widgets.FigureTypeWidget  import FigureTypeWidget
from eea.dataservice.fields.ManagementPlanField import ManagementPlanField
from eea.dataservice.widgets.ManagementPlanWidget import ManagementPlanWidget
from eea.dataservice.vocabulary import (
    COUNTRIES_DICTIONARY_ID,
    DatasetYears,
    FigureTypes,
    Organisations
)


# Schema
schema = Schema((

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
            i18n_domain="eea.dataservice",
        ),
    ),

    LinesField(
        name='temporalCoverage',
        languageIndependent=True,
        required=True,
        multiValued=1,
        vocabulary=DatasetYears(),
        widget=MultiSelectionWidget(
            macro="temporal_widget",
            helper_js=("temporal_widget.js",),
            size=15,
            label="Temporal coverage",
            description="The temporal scope of the content of the data resource. Temporal coverage will typically include a year or a time range.",
            label_msgid='dataservice_label_coverage',
            description_msgid='dataservice_help_coverage',
            i18n_domain='eea.dataservice',
        )
    ),

    LinesField(
        name='processor',
        languageIndependent=True,
        required=False,
        multiValued=1,
        vocabulary=Organisations(),
        widget=MultiSelectionWidget(
            macro="organisations_widget",
            size=15,
            label="Processor",
            description="The technical producer or processor of the data.",
            label_msgid='dataservice_label_processor',
            description_msgid='dataservice_help_processor',
            i18n_domain='eea.dataservice',
        )
    ),

    ManagementPlanField(
        name='eeaManagementPlan',
        required=False,
        default=(datetime.now().year, ''),
        #validators = ('management_plan_code_validator',),
        vocabulary=DatasetYears(),
        widget = ManagementPlanWidget(
            format="select",
            label="EEA Management Plan",
            description = ("EEA Management plan code."),
            label_msgid='dataservice_label_eea_mp',
            description_msgid='dataservice_help_eea_mp',
            i18n_domain='eea.dataservice',
        )
    ),

    LinesField(
        name='dataOwner',
        multiValued=1,
        required=True,
        vocabulary=Organisations(),
        widget=MultiSelectionWidget(
            macro="organisations_widget",
            size=15,
            label="Owner",
            description="An entity or set of entities that owns the resource. It conicides with the entity that first makes the data public available. The data owner is primarly responsible for the dataset harmonisation, quality assurance and collection from other reporting organisations.",
            label_msgid='dataservice_label_owner',
            description_msgid='dataservice_help_owner',
            i18n_domain='eea.dataservice',
        )
    ),

    DateTimeField(
        name='lastUpload',
        languageIndependent=True,
        required=True,
        default=DateTime(),
        imports="from DateTime import DateTime",
        widget=CalendarWidget(
            show_hm=False,
            label="Last upload",
            description="Shows the date when the data resource was last uploaded in EEA data Dataset service.",
            label_msgid='dataservice_label_last_upload',
            description_msgid='dataservice_help_last_upload',
            i18n_domain='eea.dataservice',
        ),
    ),

    LinesField(
        name='geographicCoverage',
        languageIndependent=True,
        required=True,
        multiValued=1,
        default=[],
        vocabulary=NamedVocabulary(COUNTRIES_DICTIONARY_ID),
        widget=MultiSelectionWidget(
            macro="countries_widget",
            helper_js=("countries_widget.js",),
            helper_css=("countries_widget.css",),
            size=15,
            label="Geographical coverage",
            description="The geographical extent of the content of the data resource.",
            label_msgid='dataservice_label_geographic',
            description_msgid='dataservice_help_geographic',
            i18n_domain='eea.dataservice',
        )
    ),

    TextField(
        name='contact',
        required=True,
        widget=TextAreaWidget(
            label="Contact persons for EEA",
            description="Outside person to be contacted by EEA if questions regarding the data resource arise at a later date, responsible project manager in EEA.",
            label_msgid='dataservice_label_dataset_contact',
            description_msgid='dataservice_help_dataset_contact',
            i18n_domain='eea.dataservice',
        )
    ),

    TextField(
        name='moreInfo',
        searchable=True,
        languageIndependent=False,
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/x-html-safe',
        widget=RichWidget(
            label="Additional information",
            description="Other relevant information.",
            label_msgid="dataservice_label_moreInfo",
            description_msgid="dataservice_help_moreInfo",
            i18n_domain="eea.dataservice",
            rows=10,
        ),
    ),

    TextField(
        name='units',
        languageIndependent=False,
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/x-html-safe',
        widget=RichWidget(
            label="Units",
            description="Describes the units taken in account for the measurement values of the data resource.",
            label_msgid="dataservice_label_unit",
            description_msgid="dataservice_help_unit",
            i18n_domain="eea.dataservice",
            rows=10,
        ),
    ),

    TextField(
        name='methodology',
        languageIndependent=False,
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/x-html-safe',
        widget=RichWidget(
            label="Methodology",
            description="Description of how the resource was compiled.",
            label_msgid="dataservice_label_methodology",
            description_msgid="dataservice_help_methodology",
            i18n_domain="eea.dataservice",
            rows=10,
        ),
    ),

    TextField(
        name='dataSource',
        languageIndependent=True,
        required=True,
        allowable_content_types=('text/html',),
        default_content_type = 'text/html',
        default_output_type = 'text/x-html-safe',
        widget=RichWidget(
            label="Source",
            description="A reference to a data resource from which the present data resource is derived.",
            label_msgid="dataservice_label_source",
            description_msgid="dataservice_help_source",
            i18n_domain="eea.dataservice",
            rows=10,
        ),
    ),

    # Fields used only for redirects to old http://dataservice.eea.europa.eu
    StringField(
        name='shortId',
        widget = StringWidget(
            label="Short ID",
            visible=-1,
            description = ("Short ID description."),
            label_msgid='dataservice_label_shortid',
            description_msgid='dataservice_help_shortid',
            i18n_domain='eea.dataservice',
        )
    ),

    StringField(
        name='relatedGid',
        widget = StringWidget(
            label="Related GID",
            visible=-1,
            description = ("Related GID description."),
            label_msgid='dataservice_label_relatedgid',
            description_msgid='dataservice_help_relatedgid',
            i18n_domain='eea.dataservice',
        )
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

    LinesField(
        schemata = "relations",
        name='externalRelations',
        languageIndependent=True,
        widget=LinesWidget(
            label="External links, non EEA websites",
            description="External links, non EEA websites. Please write http:// in front of the links.",
            label_msgid='dataservice_label_external',
            description_msgid='dataservice_help_external',
            i18n_domain='eea.dataservice',
        )
    ),

),)

eeafigure_schema = ATFolderSchema.copy() + \
               getattr(ThemeTaggable, 'schema', Schema(())).copy() + \
               schema.copy()

eeafigure_schema['description'].widget.rows = 15
eeafigure_schema['description'].required = True
eeafigure_schema['themes'].required = True

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
        if brains: res = brains[0]
        return res

    security.declareProtected(permissions.View, 'getKeywords')
    def getKeywords(self):
        res = list(self.Subject())
        res.sort(key=str.lower)
        return ', '.join(res)

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

registerType(EEAFigure, PROJECTNAME)