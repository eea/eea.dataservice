""" EEA Figure
"""
from zope.interface import implements
from Products.Archetypes.atapi import Schema, StringField
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFCore.permissions import ModifyPortalContent
from eea.dataservice.interfaces import IEEAFigure
from eea.dataservice.content.schema import dataservice_schema, DataMixin
from eea.dataservice.widgets.FigureTypeWidget import FigureTypeWidget
from eea.dataservice.content.themes import ThemeTaggable
import logging

logger = logging.getLogger('eea.dataservice')
#
# eea.relations
#
from Products.Archetypes.Field import ReferenceField
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
EEAReferenceBrowserWidget = ReferenceBrowserWidget
EEAReferenceField = ReferenceField

try:
    from eea.relations.widget.referencewidget import EEAReferenceBrowserWidget
    from eea.relations.field import EEAReferenceField
except ImportError:
    logger.warn('eea.relations is not installed')

# Schema
schema = Schema((
    # Metadata
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

    EEAReferenceField(
        name='relatedProducts',
        schemata='default',
        relationship='relatesToProducts',
        isMetadata=True,
        multiValued=True,
        languageIndependent=False,
        index='KeywordIndex',
        write_permission=ModifyPortalContent,

        keepReferencesOnCopy=True,
        widget=EEAReferenceBrowserWidget(
            visible={'view':'invisible', 'edit':'visible'},
            #label="Relations to other EEA products",
            label="References to Data Sources and Publications",
            label_msgid="label_related_products",
            description="Specify relations to other EEA products within Plone.",
            description_msgid="help_related_products",
        )
        ),

),)

eeafigure_schema = dataservice_schema.copy() + schema.copy()
eeafigure_schema['dataSource'].required = False
eeafigure_schema['dataSource'].widget.macro = "readonlytext_widget"
eeafigure_schema['dataSource'].widget.label = "Source (deprecated)"
eeafigure_schema['dataSource'].widget.description = """Please 
    use the References field above to select the relevant data sources"""

# Set position on form
eeafigure_schema.moveField('figureType', pos=3)
eeafigure_schema.moveField('dataSource', after="relatedProducts")

class EEAFigure(DataMixin, ATFolder, ThemeTaggable):
    """ EEAFigure Content Type
    """
    implements(IEEAFigure)
    archetype_name = portal_type = meta_type = 'EEAFigure'
    allowed_content_types = [
        'ATImage', 'File', 'Folder', 'DataFile', 'DataTable']
    _at_rename_after_creation = True
    schema = eeafigure_schema
