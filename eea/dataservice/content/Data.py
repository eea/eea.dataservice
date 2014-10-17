""" Data content type
"""
import logging
from zope.interface import implements
from Products.Archetypes.atapi import Schema, StringField, TextAreaWidget
from Products.Archetypes.atapi import SelectionWidget, TextField, LinesField
from Products.Archetypes.atapi import IntegerField, IntegerWidget
from Products.Archetypes.atapi import MultiSelectionWidget
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from eea.dataservice.content.themes import ThemeTaggable
from eea.dataservice.interfaces import IDataset
from eea.dataservice.content.schema import dataservice_schema, DataMixin
from eea.dataservice.vocabulary import REFERENCE_DICTIONARY_ID
from eea.geotags.field import GeotagsLinesField
from eea.geotags.widget import GeotagsWidget

logger = logging.getLogger('eea.dataservice')


# Schema
schema = Schema((
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

    GeotagsLinesField('location',
        schemata='categorization',
        required=True,
        widget=GeotagsWidget(
            label='Geographic coverage',
            description="Type in here the exact geographic names/places "\
                "that are covered by the data. Add Countries names only "\
                "if the data displayed is really about the entire country. "\
                "Example of locations/places are lakes, rivers, cities, "\
                "marine areas, glaciers, bioregions like alpine region etc."
        )
    ),
),)

dataset_schema = dataservice_schema.copy() + schema.copy()

# 8523 no longer require at all the geographic coverage
dataset_schema['geographicCoverage'].required = False

# 8523; hide geographicCoverage field since we migrated data to geotags
dataset_schema['geographicCoverage'].widget.visible = \
                            {'view':'invisible', 'edit':'invisible'}

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
