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

from eea.dataservice.config import *
from eea.dataservice.interfaces import IDataset
from eea.dataservice.vocabulary import DatasetYearsVocabulary
from eea.dataservice.vocabulary import OrganisationsVocabulary
from eea.dataservice.vocabulary import EEA_MPCODE_VOCABULARY, COUNTRIES_DICTIONARY_ID
from eea.dataservice.vocabulary import CATEGORIES_DICTIONARY_ID


#def addData(self, REQUEST={}):
#    """ Factory method for a Dataset object
#    """
#    pass

schema = Schema((
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

    #StringField(
        #name='dataOwner',
        #vocabulary=OrganisationsVocabulary(),
        #widget = SelectionWidget(
            #format="select",
            #macro="organisation_widget",
            #label="Owner",
            #description = ("Owner description."),
            #label_msgid='dataservice_label_owner',
            #description_msgid='dataservice_help_owner',
            #i18n_domain='eea.dataservice',
        #)
    #),
    LinesField(
        name='dataOwner',
        multiValued=1,
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

    StringField(
        name='processor',
        vocabulary=OrganisationsVocabulary(),
        widget = SelectionWidget(
            format="select",
            macro="organisation_widget",
            label="Processor",
            description = ("Processor description."),
            label_msgid='dataservice_label_processor',
            description_msgid='dataservice_help_processor',
            i18n_domain='eea.dataservice',
        )
    ),

    LinesField(
        name='temporal_coverage',
        languageIndependent=True,
        multiValued=1,
        vocabulary=DatasetYearsVocabulary(),
        widget=MultiSelectionWidget(
            macro="coverage_widget",
            label="Temporal coverage",
            description="Temporal coverage description.",
            label_msgid='dataservice_label_coverage',
            description_msgid='dataservice_help_coverage',
            i18n_domain='eea.dataservice',
        )
    ),

    LinesField(
        name='geographic_coverage',
        languageIndependent=True,
        multiValued=1,
        vocabulary=NamedVocabulary(COUNTRIES_DICTIONARY_ID),
        widget=MultiSelectionWidget(
            macro="geographic_widget",
            size=8,
            label="Geographical coverage",
            description="Geographical coverage description.",
            label_msgid='dataservice_label_geographic',
            description_msgid='dataservice_help_geographic',
            i18n_domain='eea.dataservice',
        )
    ),

    IntegerField(
        name='eea_mpcode',
        validators = ('isInt',),
        widget=IntegerWidget(
            size=8,
            label='EEA management plan code',
            label_msgid='dataservice_label_eea_mpcode',
            description_msgid='dataservice_help_eea_mpcode',
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
        name='source',
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
    #LinesField(
        #name='source',
        #languageIndependent=True,
        #multiValued=1,
        #default=(u'EEA (European Environment Agency)',),
        #vocabulary=NamedVocabulary("report_creators"),
        #widget=KeywordWidget(
            #label="Source",
            #description="Source description.",
            #label_msgid='dataservice_label_source',
            #description_msgid='dataservice_help_source',
            #i18n_domain='eea.dataservice',
        #)
    #),

    TextField(
        name='reference_system',
        languageIndependent=False,
        allowable_content_types=('text/html',),
        default_content_type='text/html',
        default_output_type='text/html',
        widget=RichWidget(
            label="Reference system",
            description="Reference system description.",
            label_msgid="dataservice_label_system",
            description_msgid="dataservice_help_system",
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
        name='unit',
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
    schema.copy()

class Data(ATFolder):
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

    security.declareProtected(permissions.View, 'getTablesByCategory')
    def getTablesByCategory(self):
        """ Return categories and related files
        """
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
        atvm = getToolByName(self, ATVOCABULARYTOOL)
        vocab = atvm[CATEGORIES_DICTIONARY_ID]
        return getattr(vocab, cat_code).Title()

    security.declareProtected(permissions.View, 'getOrganisationName')
    def getOrganisationName(self, url):
        """ """
        res = None
        cat = getToolByName(self, 'portal_catalog')
        brains = cat.searchResults({'portal_type' : 'Organisation',
                                 'getUrl': url})
        if brains: res = brains[0]
        return res

    security.declareProtected(permissions.View, 'getMpCodeName')
    def getMpCodeName(self, code):
        """  return management plan code title """
        return EEA_MPCODE_VOCABULARY[code]

    security.declareProtected(permissions.View, 'getCountryInfo')
    def getCountryInfo(self):
        """ """
        atvm = getToolByName(self, ATVOCABULARYTOOL)
        vocab = atvm[COUNTRIES_DICTIONARY_ID]

        res = {'groups': {}, 'countries': {}}
        for ob in vocab.objectValues():
            ob_key = ob.getId()
            ob_value = ob.Title()

            if len(ob.objectValues()) > 0:
                res['groups'][ob_key] = ob_value
            else:
                res['countries'][ob_key] = ob_value
        return res

    security.declareProtected(permissions.View, 'getCountryGroups')
    def getCountryGroups(self):
        """ """
        res = self.getCountryInfo()['groups']
        return [(key, res[key]) for key in res.keys()]

    security.declareProtected(permissions.View, 'getCountries')
    def getCountries(self):
        """ """
        res = self.getCountryInfo()['countries']
        return [(key, res[key]) for key in res.keys()]

    security.declareProtected(permissions.View, 'formatTempCoverage')
    def formatTempCoverage(self):
        """ """
        field = self.getField('temporal_coverage')
        data = field.getAccessor(self)()
        data = list(data)
        data.reverse()
        res_list = []
        res = ''
        cyear = None

        for year in data:
            if len(res_list) > 0:
                if cyear is None:
                    tmpyear = int(res_list[-1])
                else:
                    tmpyear = int(cyear)
                tmpyear = tmpyear + 1
                if int(year) == tmpyear:
                    cyear = year
                else:
                    if cyear is None:
                        res_list.append(str(year))
                    else:
                        res_list.append('-%s' % str(year))
                        cyear = None
            else:
                res_list.append(str(year))
        if cyear is not None:
            res_list.append('-%s' % str(year))

        res = ', '.join(res_list)
        return res.replace(', -', '-')

registerType(Data, PROJECTNAME)