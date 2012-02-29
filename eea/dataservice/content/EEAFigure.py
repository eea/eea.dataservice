""" EEA Figure
"""
from zope.interface import implements
from Products.Archetypes.atapi import Schema, StringField
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFCore.permissions import ModifyPortalContent
#from Products.Archetypes.Field import ReferenceField
#from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from eea.dataservice.interfaces import IEEAFigure
from eea.dataservice.content.schema import dataservice_schema, DataMixin
from eea.dataservice.widgets.FigureTypeWidget import FigureTypeWidget
from eea.dataservice.content.themes import ThemeTaggable
from eea.relations.field import EEAReferenceField
from eea.relations.widget import EEAReferenceBrowserWidget


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
        schemata='categorization',
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
            label="References to Date Sources and Publications",
            label_msgid="label_related_products",
            description="Specify relations to other EEA products within Plone.",
            description_msgid="help_related_products",
        )
        ),

),)

eeafigure_schema = dataservice_schema.copy() + schema.copy()
eeafigure_schema['dataSource'].widget.visible = {'edit':'hidden'}

# Set position on form
eeafigure_schema.moveField('figureType', pos=3)

class EEAFigure(DataMixin, ATFolder, ThemeTaggable):
    """ EEAFigure Content Type
    """
    implements(IEEAFigure)
    archetype_name = portal_type = meta_type = 'EEAFigure'
    allowed_content_types = [
        'ATImage', 'File', 'Folder', 'DataFile', 'DataTable']
    _at_rename_after_creation = True
    schema = eeafigure_schema
