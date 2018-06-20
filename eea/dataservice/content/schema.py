""" Common schema
"""
from datetime import datetime
from DateTime import DateTime
from zope.component import queryAdapter
from zope.interface import implements
from Products.Archetypes.atapi import Schema, LinesField, LinesWidget
from Products.Archetypes.atapi import MultiSelectionWidget, TextField
from Products.Archetypes.atapi import CalendarWidget, DateTimeField
from Products.Archetypes.atapi import TextAreaWidget, RichWidget
from Products.Archetypes.atapi import StringWidget, StringField
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.validation.interfaces.IValidator import IValidator
from Products.validation import validation
from eea.dataservice.content.themes import ThemeTaggable
from eea.forms.fields.ManagementPlanField import ManagementPlanField
from eea.forms.widgets.ManagementPlanWidget import ManagementPlanWidget
from eea.dataservice.vocabulary import COUNTRIES_DICTIONARY_ID
from eea.dataservice.content.themes import IThemeTagging
from eea.dataservice.widgets import MultiOrganisationsWidget

class DataMixin(object):
    """ Common data methods
    """
    def getOrganisationName(self, url):
        """ Organisation Name
        """
        cat = getToolByName(self, 'portal_catalog')
        brains = cat.searchResults({
            'portal_type' : 'Organisation',
            'getUrl': url
        })

        if brains:
            return brains[0]

    def getTemporalCoverage(self):
        """ temporalCoverage Field accessor
        """
        return self.getField('temporalCoverage').getAccessor(self)()

    def getKeywords(self):
        """ Keywords
        """
        res = list(self.Subject())
        res.sort(key=str.lower)
        return ', '.join(res)

    def Rights(self):
        """ Return standard EEA copyrights policy information otherwise
            return the specific one if present.
        """
        value = self.schema['rights'].getRaw(self)

        if value:
            return value
        else:
            ownerfield = self.getField('dataOwner')
            urls = ownerfield.getAccessor(self)()
            orgnames = []
            copyrightholders = ""
            for url in urls:
                orgob = self.getOrganisationName(url)
                if not orgob:
                    continue
                orgnames.append(orgob.Title)

            if orgnames:
                copyrightholders = 'Copyright holder: %s.' % ', '.join(orgnames)

            return ("EEA standard re-use policy: unless otherwise indicated, "
                    "re-use of content on the EEA website for commercial or "
                    "non-commercial purposes is permitted free of charge, "
                    "provided that the source is acknowledged "
                    "(https://www.eea.europa.eu/legal/copyright). "
                    "%s" % copyrightholders)

    def getThemeVocabs(self):
        """ Themes vocabulary
        """
        return None

    def setThemes(self, value, **kw):
        """ Use the tagging adapter to set the themes.
        """
        value = [val for val in value if val is not None]
        tagging = queryAdapter(self, IThemeTagging)
        if tagging:
            tagging.tags = value


class UniqueOrganisationUrlValidator(object):
    """ Validator
    """
    implements(IValidator)

    def __init__(self,
                 name,
                 title='Unique organisation URL',
                 description='Unique organisation URL validator'):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kwargs):

        # http://eea.eu == http://eea.eu/
        if value.endswith('/'):
            value = [value, value[:len(value) - 1]]
        else:
            value = [value, '%s/' % value]

        cat = getToolByName(kwargs['instance'], 'portal_catalog')
        brains = cat.searchResults({'portal_type': 'Organisation',
                                    'getUrl': value})

        if brains:
            for brain in brains:
                org_ob = brain.getObject()
                if kwargs['instance'].UID() != org_ob.UID():
                    return ("Validation failed, there is already an "
                            "organisation poiting to this URL.")
        return 1

validation.register(
    UniqueOrganisationUrlValidator('unique_organisation_url_validator'))

# Base schema for datasets and figures
dataservice_base_schema = Schema((
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
            label="Geographic coverage",
            description=("Type in here the exact geographic names/places "
                "that are covered by the data. Add Countries names only if "
                "the data displayed is really about the entire country. "
                "Example of locations/places are lakes, rivers, cities, "
                "marine areas, glaciers, bioregions like alpine region etc."),
            label_msgid='dataservice_label_geographic',
            description_msgid='dataservice_help_geographic',
            i18n_domain='eea',
        )
    ),

    ManagementPlanField(
        name='eeaManagementPlan',
        languageIndependent=True,
        required=True,
        default=(datetime.now().year, ''),
        validators=('management_plan_code_validator',),
        vocabulary_factory=u"Temporal coverage",
        widget=ManagementPlanWidget(
            format="select",
            label="EEA Management Plan",
            description=("EEA Management plan code."),
            label_msgid='dataservice_label_eea_mp',
            description_msgid='dataservice_help_eea_mp',
            i18n_domain='eea',
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
            description=("Date when the data resource was last uploaded in "
                         "EEA data service. If not manually provided it will "
                         "coincide with publishing date. It can later be used "
                         "when a dataset is re-uploaded due to corrections "
                         "and when a whole new version is not necessary."),
            label_msgid='dataservice_label_last_upload',
            description_msgid='dataservice_help_last_upload',
            i18n_domain='eea',
        ),
    ),

    LinesField(
        name='dataOwner',
        languageIndependent=True,
        multiValued=1,
        required=True,
        vocabulary_factory=u'Organisations',
        widget=MultiOrganisationsWidget(
            label="Owner",
            description=("An entity or set of entities that owns the "
                         "resource. The owner is responsible for the "
                         "reliability of the resource."),
            label_msgid='dataservice_label_owner',
            description_msgid='dataservice_help_owner',
            i18n_domain='eea',
        )
    ),

    LinesField(
        name='processor',
        languageIndependent=True,
        required=False,
        multiValued=1,
        vocabulary_factory=u"Organisations",
        widget=MultiOrganisationsWidget(
            label="Processor",
            description="The technical producer or processor of the resource.",
            label_msgid='dataservice_label_processor',
            description_msgid='dataservice_help_processor',
            i18n_domain='eea',
        )
    ),

    TextField(
        name='contact',
        languageIndependent=True,
        required=True,
        widget=TextAreaWidget(
            label="Contact person(s) for EEA",
            description=("Outside person to be contacted by EEA if questions "
                         "regarding the data resource arise at a later date, "
                         "responsible project manager at EEA."),
            label_msgid='dataservice_label_dataset_contact',
            description_msgid='dataservice_help_dataset_contact',
            i18n_domain='eea',
        )
    ),

    TextField(
        name='dataSource',
        languageIndependent=True,
        required=True,
        allowable_content_types=('text/html', 'text/plain',),
        default_content_type='text/html',
        default_output_type='text/x-html-safe',
        widget=RichWidget(
            label="Source",
            description=("A reference to a resource from which the present "
                         "resource is derived. Details such exact body "
                         "or department, date of delivery, original database, "
                         "table or GIS layer, scientific literature ..."),
            label_msgid="dataservice_label_source",
            description_msgid="dataservice_help_source",
            i18n_domain="eea",
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
            i18n_domain="eea",
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
            description=("Description of how the resource was compiled: used "
                         "tools, applied procedures, additional information "
                         "to understand the data, further references to used "
                         "methodologies."),
            label_msgid="dataservice_label_methodology",
            description_msgid="dataservice_help_methodology",
            i18n_domain="eea",
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
            description=("Describes the unit(s) taken in account for the "
                         "measurement values(s) of the data resource."),
            label_msgid="dataservice_label_unit",
            description_msgid="dataservice_help_unit",
            i18n_domain="eea",
            rows=5,
        ),
    ),

    # Field used only for redirects to old http://dataservice.eea.europa.eu
    StringField(
        name='shortId',
        widget=StringWidget(
            label="Short ID",
            visible=-1,
            description=("Short ID description."),
            label_msgid='dataservice_label_shortid',
            description_msgid='dataservice_help_shortid',
            i18n_domain='eea',
        )
    ),

    # Fields for 'relations' schemata
    LinesField(
        schemata="categorization",
        name='externalRelations',
        languageIndependent=True,
        widget=LinesWidget(
            label="External links, non EEA websites",
            description=("External links, non EEA websites. "
                         "Please write http:// in front of the links."),
            label_msgid='dataservice_label_external',
            description_msgid='dataservice_help_external',
            i18n_domain='eea',
        )
    ),
),)

dataservice_schema = ATFolderSchema.copy() + \
                     getattr(ThemeTaggable, 'schema', Schema(())).copy() + \
                     dataservice_base_schema.copy()

dataservice_schema['description'].widget.rows = 15
dataservice_schema['description'].required = True
