""" Select widget
"""
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import BooleanWidget
from eea.facetednavigation.widgets.vocabulary import CatalogIndexesVocabulary
from eea.facetednavigation.widgets.vocabulary import UseCatalogVocabulary
from eea.facetednavigation.widgets.vocabulary import PortalVocabulariesVocabulary

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from eea.facetednavigation.widgets.widget import CountableWidget

EditSchema = Schema((
    StringField('title',
        required=True,
        widget=StringWidget(
            size=25,
            label='Friendly name',
            label_msgid='faceted_criteria_title',
            description='Title for widget to display in view page',
            description_msgid='help_faceted_criteria_title',
            i18n_domain="eea.dataservice"
        )
    ),
    StringField('index',
        required=True,
        vocabulary=CatalogIndexesVocabulary(),
        widget=SelectionWidget(
            label='Catalog index',
            label_msgid='faceted_criteria_index',
            description='Catalog index to use for search',
            description_msgid='help_faceted_criteria_index',
            i18n_domain="eea.dataservice"
        )
    ),
    StringField('vocabulary',
        vocabulary=PortalVocabulariesVocabulary(),
        widget=SelectionWidget(
            label='Vocabulary',
            label_msgid='faceted_criteria_vocabulary',
            description='Vocabulary to use to render widget items',
            description_msgid='help_faceted_criteria_vocabulary',
            i18n_domain="eea.dataservice"
        )
    ),
    StringField('catalog',
        vocabulary=UseCatalogVocabulary,
        widget=SelectionWidget(
            format='select',
            label='Catalog',
            label_msgid='faceted_criteria_catalog',
            description='Get unique values from catalog as an alternative for vocabulary',
            description_msgid='help_faceted_criteria_catalog',
            i18n_domain="eea.dataservice"
        )
    ),
    BooleanField('count',
        widget=BooleanWidget(
            label='Count results',
            label_msgid='faceted_criteria_count',
            description='Display number of results near each option',
            description_msgid='help_faceted_criteria_count',
            i18n_domain="eea.dataservice"
        )
    ),
    StringField('default',
        widget=StringWidget(
            size=25,
            label='Default value',
            label_msgid='faceted_criteria_default',
            description='Default selected item',
            description_msgid='help_faceted_criteria_select_default',
            i18n_domain="eea.dataservice"
        )
    ),
))

class Widget(CountableWidget):
    """ Widget
    """
    # Widget properties
    widget_type = 'geocoverage'
    widget_label = 'European countries'
    view_js = '++resource++eea.dataservice.facetednavigation.geocoverage.view.js'
    edit_js = '++resource++eea.dataservice.facetednavigation.geocoverage.edit.js'
    view_css = '++resource++eea.dataservice.facetednavigation.geocoverage.view.css'
    edit_css = '++resource++eea.dataservice.facetednavigation.geocoverage.edit.css'

    index = ViewPageTemplateFile('widget.pt')
    edit_schema = EditSchema

    def query(self, form):
        """ Get value from form and return a catalog dict query
        """
        query = {}
        index = self.data.get('index', '')
        index = index.encode('utf-8', 'replace')
        if not index:
            return query

        if self.hidden:
            value = self.default
        else:
            value = form.get(self.data.getId(), '')

        if not value:
            return query

        query[index] = value
        return query
