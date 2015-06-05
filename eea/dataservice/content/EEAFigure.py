""" EEA Figure content type
"""
import logging
from zope.interface import implements
from Products.Archetypes.atapi import Schema, StringField
from Products.ATContentTypes.content.folder import ATFolder
from eea.dataservice.interfaces import IEEAFigure
from eea.dataservice.content.schema import dataservice_schema, DataMixin
from eea.dataservice.widgets.FigureTypeWidget import FigureTypeWidget
from eea.dataservice.content.themes import ThemeTaggable

logger = logging.getLogger('eea.dataservice')

# Schema
schema = Schema((
    StringField(
        name='figureType',
        languageIndependent=False,
        required=True,
        vocabulary_factory=u"Figure types",
        widget=FigureTypeWidget(
            label="Figure type",
            format="select",
            description="Figure type description.",
            label_msgid="dataservice_type",
            description_msgid="dataservice_help_type",
            i18n_domain="eea",
        ),
    ),
),)

eeafigure_schema = dataservice_schema.copy() + schema.copy()
eeafigure_schema['dataSource'].required = False
eeafigure_schema['dataSource'].widget.macro = "readonlytext_widget"
eeafigure_schema['dataSource'].widget.label = "Source (deprecated)"
eeafigure_schema['dataSource'].widget.description = """Please
    use the References field above to select the relevant data sources"""

# 8523; hide geographicCoverage field since we migrated data to geotags
# and no longer require this field

eeafigure_schema['geographicCoverage'].required = False
eeafigure_schema['geographicCoverage'].widget.visible = \
    {'view': 'invisible', 'edit': 'invisible'}

# Set position on form
eeafigure_schema.moveField('figureType', pos=3)
eeafigure_schema.moveField('dataSource', after="units")


class EEAFigure(DataMixin, ATFolder, ThemeTaggable):
    """ EEAFigure Content Type
    """
    implements(IEEAFigure)
    archetype_name = portal_type = meta_type = 'EEAFigure'
    allowed_content_types = [
        'ATImage', 'File', 'Folder', 'DataFile', 'DataTable']
    _at_rename_after_creation = True
    schema = eeafigure_schema
