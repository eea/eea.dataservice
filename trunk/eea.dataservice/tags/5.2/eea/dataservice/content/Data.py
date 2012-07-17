""" Data
"""
from zope.interface import implements
from Products.Archetypes.atapi import Schema, StringField, TextAreaWidget
from Products.Archetypes.atapi import SelectionWidget, TextField, LinesField
from Products.Archetypes.atapi import IntegerField, IntegerWidget
from Products.Archetypes.atapi import MultiSelectionWidget
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFCore.permissions import ModifyPortalContent
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.Archetypes.Field import ReferenceField

from eea.dataservice.content.themes import ThemeTaggable
from eea.dataservice.interfaces import IDataset
from eea.dataservice.content.schema import dataservice_schema, DataMixin
from eea.dataservice.vocabulary import REFERENCE_DICTIONARY_ID
import logging

logger = logging.getLogger('eea.dataservice')
#
# eea.relations
#
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
EEAReferenceBrowserWidget = ReferenceBrowserWidget

try:
    from eea.relations.widget.referencewidget import EEAReferenceBrowserWidget
except ImportError:
    logger.warn('eea.relations is not installed')

# Schema
schema = Schema((
    # Metadata
    TextField(
        name='geoAccuracy',
        languageIndependent=True,
        widget=TextAreaWidget(
            label="Geographic accuracy",
            description=("It is applicable to GIS datasets. It indicates the "
                         "geographic accuracy of location, ground distance as "
                         "a value in meters."),
            label_msgid='dataservice_label_accurracy',
            description_msgid='dataservice_help_accurracy',
            i18n_domain='eea',
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
            description_msgid=('A disclaimer is a statement which generally '
                               'states that the entity authoring the '
                               'disclaimer is not responsible for something '
                               'in some manner.'),
            i18n_domain='eea',
        )
    ),

    IntegerField(
        name='scale',
        languageIndependent=True,
        required=False,
        validators=('isInt',),
        widget=IntegerWidget(
            macro='scale_widget',
            label='Scale of the dataset',
            label_msgid='dataservice_label_scale',
            description=("Gives a rough value of accuracy for the GIS "
                           "dataset. Example: 1:1000"),
            description_msgid='dataservice_help_scale',
            i18n_domain='eea',
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
            description=("Coordinate reference system used for the GIS "
                         "dataset. Example: Lambert Azimutal"),
            label_msgid="dataservice_label_system",
            description_msgid="dataservice_help_system",
            i18n_domain="eea",
        ),
    ),

    # Fields for 'relations' schemata
    LinesField(
        schemata="categorization",
        name='reportingObligations',
        languageIndependent=True,
        multiValued=1,
        vocabulary_factory=u"Obligations",
        widget=MultiSelectionWidget(
            macro="obligations_widget",
            label="Environmental reporting obligations (ROD)",
            description=("The environmental reporting obligations used to "
                         "optain the data. Reporting obligations are "
                         "requirements to provide information agreed between "
                         "countries and international bodies such as the EEA "
                         "or international conventions."),
            label_msgid='dataservice_label_obligations',
            description_msgid='dataservice_help_obligations',
            i18n_domain='eea',
        )
    ),

    ReferenceField(
        'relatedProducts',
        schemata="categorization",
        relationship='relatesToProducts',
        multiValued=True,
        isMetadata=True,
        languageIndependent=False,
        index='KeywordIndex',
        write_permission=ModifyPortalContent,
        widget=EEAReferenceBrowserWidget(
            allow_search=True,
            allow_browse=True,
            allow_sorting=True,
            show_indexes=False,
            force_close_on_insert=True,
            label="Relations to other EEA products",
            label_msgid="label_related_products",
            description="Specify relations to other EEA products within Plone.",
            description_msgid="help_related_products",
            i18n_domain="plone",
            visible={'edit' : 'visible', 'view' : 'invisible' }
            )
        ),

    ReferenceField(
        'relatedItems',
        schemata="categorization",
        relationship='relatesTo',
        multiValued=True,
        isMetadata=True,
        languageIndependent=False,
        index='KeywordIndex',
        write_permission=ModifyPortalContent,
        widget=EEAReferenceBrowserWidget(
            allow_search=True,
            allow_browse=True,
            allow_sorting=True,
            show_indexes=False,
            force_close_on_insert=True,
            label="This dataset is derived from",
            label_msgid="dataservice_label_related_items",
            description=("Specify the datasets from which this dataset "
                         "is derived."),
            description_msgid="dataservice_help_related_items",
            i18n_domain="plone",
            startup_directory='data',
            visible={'edit' : 'visible', 'view' : 'invisible' }
            )
        )
),)

dataset_schema = dataservice_schema.copy() + schema.copy()

# Set position on form
dataset_schema.moveField('disclaimer', after='contact')
dataset_schema.moveField('geoAccuracy', before='contact')
dataset_schema.moveField('referenceSystem', before='geoAccuracy')
dataset_schema.moveField('scale', before='referenceSystem')
dataset_schema.moveField('relatedItems', pos='bottom')

class Data(DataMixin, ATFolder, ThemeTaggable):
    """ Dataset Content Type
    """
    implements(IDataset)
    archetype_name = portal_type = meta_type = 'Data'
    allowed_content_types = ['ATImage', 'File', 'Folder', 'DataTable']
    _at_rename_after_creation = True
    schema = dataset_schema
