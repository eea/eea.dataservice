# -*- coding: utf-8 -*-

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from datetime import datetime
from DateTime import DateTime

from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.EEAContentTypes.content.ThemeTaggable import ThemeTaggable

from eea.dataservice.fields.ManagementPlanField import ManagementPlanField
from eea.dataservice.widgets.ManagementPlanWidget import ManagementPlanWidget
from eea.dataservice.vocabulary import (
    COUNTRIES_DICTIONARY_ID,
    DatasetYears,
    Organisations
)


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

# Base schema for datasets and figures
dataservice_base_schema = Schema((
    # Metadata
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

    ManagementPlanField(
        name='eeaManagementPlan',
        languageIndependent=True,
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

    DateTimeField(
        name='lastUpload',
        languageIndependent=True,
        required=True,
        default=DateTime(),
        imports="from DateTime import DateTime",
        widget=CalendarWidget(
            show_hm=False,
            label="Last upload",
            description="Date when the data resource was last uploaded in EEA data service. If not manually provided it will conicide with publishing date. It can later be used when a dataset is re-uploaded due to corrections and when a whole new version is not necessary.",
            label_msgid='dataservice_label_last_upload',
            description_msgid='dataservice_help_last_upload',
            i18n_domain='eea.dataservice',
        ),
    ),

    LinesField(
        name='dataOwner',
        languageIndependent=True,
        multiValued=1,
        required=True,
        vocabulary=Organisations(),
        widget=MultiSelectionWidget(
            macro="organisations_widget",
            size=15,
            label="Owner",
            description="An entity or set of entities that owns the data resource. It conicides with the entity that first makes the data public available. The data owner is primarly responsible for the dataset harmonisation, quality assurance and collection from other reporting organisations.",
            label_msgid='dataservice_label_owner',
            description_msgid='dataservice_help_owner',
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
            description="The temporal scope of the content of the data resource. Temporal coverage will typically include a set of years or a time range.",
            label_msgid='dataservice_label_coverage',
            description_msgid='dataservice_help_coverage',
            i18n_domain='eea.dataservice',
        )
    ),

    TextField(
        name='contact',
        languageIndependent=True,
        required=True,
        widget=TextAreaWidget(
            label="Contact person(s) for EEA",
            description="Outside person to be contacted by EEA if questions regarding the data resource arise at a later date, responsible project manager at EEA.",
            label_msgid='dataservice_label_dataset_contact',
            description_msgid='dataservice_help_dataset_contact',
            i18n_domain='eea.dataservice',
        )
    ),

    TextField(
        name='dataSource',
        languageIndependent=True,
        required=True,
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/x-html-safe',
        widget=RichWidget(
            label="Source",
            description="A reference to a resource from which the present data resource is derived. Details such exact body or department, date of delivery, original database, table or GIS layer, scientific literature ...",
            label_msgid="dataservice_label_source",
            description_msgid="dataservice_help_source",
            i18n_domain="eea.dataservice",
            rows=5,
        ),
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
            rows=5,
        ),
    ),

    TextField(
        name='methodology',
        languageIndependent=False,
        required=False,
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/x-html-safe',
        widget=RichWidget(
            label="Methodology",
            description="Description of how the resource was compiled: used tools, applied procedures, additional information to understand the data, further references to used methodologies.",
            label_msgid="dataservice_label_methodology",
            description_msgid="dataservice_help_methodology",
            i18n_domain="eea.dataservice",
            rows=5,
        ),
    ),

    TextField(
        name='units',
        languageIndependent=True,
        required=False,
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/x-html-safe',
        widget=RichWidget(
            label="Unit",
            description="Describes the unit(s) taken in account for the measurement values(s) of the data resource.",
            label_msgid="dataservice_label_unit",
            description_msgid="dataservice_help_unit",
            i18n_domain="eea.dataservice",
            rows=5,
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

dataservice_schema = ATFolderSchema.copy() + \
                     getattr(ThemeTaggable, 'schema', Schema(())).copy() + \
                     dataservice_base_schema.copy()

dataservice_schema['description'].widget.rows = 15
dataservice_schema['description'].required = True
dataservice_schema['themes'].required = True
