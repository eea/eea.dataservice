# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from DateTime import DateTime
from zope.interface import implements
from Products.Archetypes.atapi import *
from Products.CMFCore import permissions
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from zope.app.annotation.interfaces import IAnnotations
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary

from eea.themecentre.interfaces import IThemeTagging
from Products.EEAContentTypes.content.ThemeTaggable import ThemeTaggable

from eea.dataservice.config import *
from eea.dataservice.interfaces import IDataset
from eea.dataservice.vocabulary import DatasetYears
from eea.dataservice.migration.parser import _get_random
from eea.dataservice.vocabulary import COUNTRIES_DICTIONARY_ID
from eea.dataservice.vocabulary import REFERENCE_DICTIONARY_ID
from eea.dataservice.vocabulary import Organisations, Obligations
from eea.dataservice.fields.GeoQualityField import GeoQualityField
from eea.dataservice.versions.versions import VERSION_ID, _reindex
from eea.dataservice.widgets.GeoQualityWidget import GeoQualityWidget
from eea.dataservice.fields.ManagementPlanField import ManagementPlanField
from eea.dataservice.widgets.ManagementPlanWidget import ManagementPlanWidget

# Validators
from Products.validation.interfaces.IValidator import IValidator
from Products.validation import validation
class ManagementPlanCodeValidator:
    __implements__ = IValidator

    def __init__(self,
                 name,
                 title='Management plan code',
                 description='Management plan code validator'):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kwargs):
        try:
            nval = int(value[1])
        except ValueError:
            return ("Validation failed, management plan code is not integer.")
        return 1

validation.register(ManagementPlanCodeValidator('management_plan_code_validator'))

# Schema
schema = Schema((
    LinesField(
        name='geographicCoverage',
        languageIndependent=True,
        multiValued=1,
        default=[],
        vocabulary=NamedVocabulary(COUNTRIES_DICTIONARY_ID),
        widget=MultiSelectionWidget(
            macro="countries_widget",
            helper_js=("countries_widget.js",),
            helper_css=("countries_widget.css",),
            size=8,
            label="Geographical coverage",
            description="The geographical extent of the content of the data resource.",
            label_msgid='dataservice_label_geographic',
            description_msgid='dataservice_help_geographic',
            i18n_domain='eea.dataservice',
        )
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

    ManagementPlanField(
        name='eeaManagementPlan',
        languageIndependent=True,
        required=True,
        default=('', ''),
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

    DateTimeField(
        name='lastUpload',
        languageIndependent=True,
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

    StringField(
        name='referenceSystem',
        languageIndependent=True,
        vocabulary=NamedVocabulary(REFERENCE_DICTIONARY_ID),
        widget=SelectionWidget(
            macro="reference_widget",
            label="Coordinate reference system",
            description="Coordinate reference system used for the dataset.",
            label_msgid="dataservice_label_system",
            description_msgid="dataservice_help_system",
            i18n_domain="eea.dataservice",
        ),
    ),

    IntegerField(
        name='scale',
        languageIndependent=True,
        validators = ('isInt',),
        widget=IntegerWidget(
            macro='scale_widget',
            label='Scale of the dataset',
            label_msgid='dataservice_label_scale',
            description = ("Gives a rough value of accuracy of the dataset."),
            description_msgid='dataservice_help_scale',
            i18n_domain='eea.dataservice',
            size=20,
        )
    ),

    LinesField(
        name='dataOwner',
        languageIndependent=True,
        multiValued=1,
        required=True,
        vocabulary=Organisations(),
        widget=MultiSelectionWidget(
            macro="organisations_widget",
            label="Owner",
            description="An entity that owns the data resource.",
            label_msgid='dataservice_label_owner',
            description_msgid='dataservice_help_owner',
            i18n_domain='eea.dataservice',
        )
    ),

    LinesField(
        name='processor',
        languageIndependent=True,
        multiValued=1,
        vocabulary=Organisations(),
        widget=MultiSelectionWidget(
            macro="organisations_widget",
            label="Processor",
            description="The technical producer or processor of the data.",
            label_msgid='dataservice_label_processor',
            description_msgid='dataservice_help_processor',
            i18n_domain='eea.dataservice',
        )
    ),

    LinesField(
        name='temporalCoverage',
        languageIndependent=True,
        multiValued=1,
        vocabulary=DatasetYears(),
        widget=MultiSelectionWidget(
            macro="temporal_widget",
            helper_js=("temporal_widget.js",),
            label="Temporal coverage",
            description="The temporal scope of the content of the data resource. Temporal coverage will typically include a year or a time range.",
            label_msgid='dataservice_label_coverage',
            description_msgid='dataservice_help_coverage',
            i18n_domain='eea.dataservice',
        )
    ),

    TextField(
        name='disclaimer',
        widget=TextAreaWidget(
            label="Disclaimer",
            description="Disclaimer description.",
            label_msgid='dataservice_label_disclaimer',
            description_msgid='A disclaimer is a statement which generally states that the entity authoring the disclaimer is not responsible for something in some manner.',
            i18n_domain='eea.dataservice',
        )
    ),

    TextField(
        name='contact',
        languageIndependent=True,
        widget=TextAreaWidget(
            label="Contact person(s) for EEA",
            description="Outside person to be contacted by EEA if questions regarding the data \
resource arise at a later date, responsible project manager in EEA and the \
operator who uploaded the data resource and edited metadata. All three roles should be enlisted here.",
            label_msgid='dataservice_label_dataset_contact',
            description_msgid='dataservice_help_dataset_contact',
            i18n_domain='eea.dataservice',
        )
    ),

    TextField(
        name='geoAccuracy',
        languageIndependent=True,
        widget=TextAreaWidget(
            label="Geographic accuracy",
            description="Geographic accuracy of location, ground distance as a value in meters.",
            label_msgid='dataservice_label_accurracy',
            description_msgid='dataservice_help_accurracy',
            i18n_domain='eea.dataservice',
        )
    ),

    TextField(
        name='dataSource',
        languageIndependent=True,
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/html',
        widget=RichWidget(
            label="Source",
            description="A reference to a resource from which the present data resource is derived.",
            label_msgid="dataservice_label_source",
            description_msgid="dataservice_help_source",
            i18n_domain="eea.dataservice",
            rows=10,
        ),
    ),

    TextField(
        name='moreInfo',
        searchable=True,
        languageIndependent=False,
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/html',
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
        name='methodology',
        languageIndependent=False,
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/html',
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
        name='units',
        languageIndependent=False,
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/html',
        widget=RichWidget(
            label="Unit",
            description="Describes the unit(s) taken in account for the measurement values(s) of the data resource.",
            label_msgid="dataservice_label_unit",
            description_msgid="dataservice_help_unit",
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

    # Fields for 'relations' schemata
    LinesField(
        schemata = "relations",
        name='reportingObligations',
        languageIndependent=True,
        multiValued=1,
        vocabulary=Obligations(),
        widget=MultiSelectionWidget(
            macro="obligations_widget",
            label="Reporting obligation(s)",
            description="If the dataset is listed in the ROD information should be identical to the information field called 'Report to' provided there.",
            label_msgid='dataservice_label_obligations',
            description_msgid='dataservice_help_obligations',
            i18n_domain='eea.dataservice',
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

    ),
)

Dataset_schema = ATFolderSchema.copy() + \
               getattr(ThemeTaggable, 'schema', Schema(())).copy() + \
               schema.copy()


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

    schema = Dataset_schema

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