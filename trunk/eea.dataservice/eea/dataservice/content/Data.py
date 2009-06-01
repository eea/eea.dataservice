# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from Products.Archetypes.atapi import *
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.CMFCore import permissions
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFCore.utils import getToolByName
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
from zope.interface import implements
from DateTime import DateTime
from AccessControl import ClassSecurityInfo

from Products.EEAContentTypes.content.ThemeTaggable import ThemeTaggable
from eea.themecentre.interfaces import IThemeTagging

from eea.dataservice.config import *
from eea.dataservice.widgets.ManagementPlanWidget import ManagementPlanWidget
from eea.dataservice.widgets.GeoQualityWidget import GeoQualityWidget
from eea.dataservice.fields.ManagementPlanField import ManagementPlanField
from eea.dataservice.fields.GeoQualityField import GeoQualityField
from eea.dataservice.interfaces import IDataset
from eea.dataservice.vocabulary import DatasetYearsVocabulary
from eea.dataservice.vocabulary import OrganisationsVocabulary
from eea.dataservice.vocabulary import COUNTRIES_DICTIONARY_ID
from eea.dataservice.vocabulary import CATEGORIES_DICTIONARY_ID

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
            description="Geographical coverage description.",
            label_msgid='dataservice_label_geographic',
            description_msgid='dataservice_help_geographic',
            i18n_domain='eea.dataservice',
        )
    ),

    GeoQualityField(
        name='geoQuality',
        default=('-1', '-1', '-1', '-1', '-1'),
        vocabulary=NamedVocabulary("quality"),
        widget = GeoQualityWidget(
            format="select",
            label="Geographic information quality",
            description = ("Geographic information quality description."),
            label_msgid='dataservice_label_geoQuality',
            description_msgid='dataservice_help_geoQuality',
            i18n_domain='eea.dataservice',
        )
    ),

    ManagementPlanField(
        name='eeaManagementPlan',
        required=True,
        default=('', ''),
        validators = ('management_plan_code_validator',),
        vocabulary=DatasetYearsVocabulary(),
        widget = ManagementPlanWidget(
            format="select",
            label="EEA Management Plan",
            description = ("EEA Management plan description."),
            label_msgid='dataservice_label_eea_mp',
            description_msgid='dataservice_help_eea_mp',
            i18n_domain='eea.dataservice',
        )
    ),

    DateTimeField(
        name='lastUpload',
        default=DateTime(),
        imports="from DateTime import DateTime",
        widget=CalendarWidget(
            show_hm=False,
            label="Last upload",
            description="Lst upload description.",
            label_msgid='dataservice_label_last_upload',
            description_msgid='dataservice_help_last_upload',
            i18n_domain='eea.dataservice',
        ),
    ),

    IntegerField(
        name='scale',
        validators = ('isInt',),
        widget=IntegerWidget(
            macro='scale_widget',
            label='Scale of the data set',
            label_msgid='dataservice_label_scale',
            description = ("Gives a rough value of accuracy of the dataset."),
            description_msgid='dataservice_help_scale',
            i18n_domain='eea.dataservice',
            size=20,
        )
    ),

    LinesField(
        name='dataOwner',
        multiValued=1,
        required=True,
        vocabulary=OrganisationsVocabulary(),
        widget=MultiSelectionWidget(
            macro="organisations_widget",
            label="Owner",
            description="Owner description.",
            label_msgid='dataservice_label_owner',
            description_msgid='dataservice_help_owner',
            i18n_domain='eea.dataservice',
        )
    ),

    LinesField(
        name='processor',
        multiValued=1,
        vocabulary=OrganisationsVocabulary(),
        widget=MultiSelectionWidget(
            macro="organisations_widget",
            label="Processor",
            description="Processor description.",
            label_msgid='dataservice_label_processor',
            description_msgid='dataservice_help_processor',
            i18n_domain='eea.dataservice',
        )
    ),

    LinesField(
        name='temporalCoverage',
        languageIndependent=True,
        multiValued=1,
        vocabulary=DatasetYearsVocabulary(),
        widget=MultiSelectionWidget(
            macro="temporal_widget",
            helper_js=("temporal_widget.js",),
            label="Temporal coverage",
            description="Temporal coverage description.",
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
            description_msgid='dataservice_help_disclaimer',
            i18n_domain='eea.dataservice',
        )
    ),

    TextField(
        name='contact',
        widget=TextAreaWidget(
            label="Contact person(s) for EEA",
            description="dataset_contact description.",
            label_msgid='dataservice_label_dataset_contact',
            description_msgid='dataservice_help_dataset_contact',
            i18n_domain='eea.dataservice',
        )
    ),

    TextField(
        name='geoAccuracy',
        widget=TextAreaWidget(
            label="Geographic accuracy",
            description="Geographic accuracy description.",
            label_msgid='dataservice_label_accurracy',
            description_msgid='dataservice_help_accurracy',
            i18n_domain='eea.dataservice',
        )
    ),

    TextField(
        name='referenceSystem',
        languageIndependent=False,
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/html',
        widget=RichWidget(
            macro="reference_system_widget",
            helper_js=("reference_system_widget.js",),
            label="Reference system",
            description="Reference system description.",
            label_msgid="dataservice_label_system",
            description_msgid="dataservice_help_system",
            i18n_domain="eea.dataservice",
            rows=10,
        ),
    ),

    TextField(
        name='dataSource',
        languageIndependent=False,
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/html',
        widget=RichWidget(
            label="Source",
            description="Source description.",
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
            description="Additional information description.",
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
            description="methodology description.",
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
            description="Unit description.",
            label_msgid="dataservice_label_unit",
            description_msgid="dataservice_help_unit",
            i18n_domain="eea.dataservice",
            rows=10,
        ),
    ),

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
    allowed_content_types = ['ATImage', 'File', 'Folder', 'DataFile', 'DataTable']
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

    security.declareProtected(permissions.View, 'getTablesByCategory')
    def getTablesByCategory(self):
        """ Return categories and related files
        """
        #TODO: fix me
        res = {}
        for table in self.objectValues('DataTable'):
            cat = table.category
            if not cat in res.keys():
                res[cat] = []
            res[cat].append(table)
        return res

    security.declareProtected(permissions.View, 'getCategoryName')
    def getCategoryName(self, cat_code):
        """ Return category name
        """
        #TODO: fix me
        atvm = getToolByName(self, ATVOCABULARYTOOL)
        vocab = atvm[CATEGORIES_DICTIONARY_ID]
        return getattr(vocab, cat_code).Title()

registerType(Data, PROJECTNAME)