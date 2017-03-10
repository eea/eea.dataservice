""" Version widget
"""
from zope.interface import implements
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from eea.facetednavigation.widgets.widget import Widget as AbstractWidget

from eea.dataservice.facetednavigation.lastversion.interfaces import (
    ILastVersionWidget,
)

class Widget(AbstractWidget):
    """ Widget
    """
    implements(ILastVersionWidget)

    # Widget properties
    widget_type = 'lastversion'
    widget_label = 'Show most recent version'
    view_js = (
        '++resource++eea.dataservice.facetednavigation.dataservice.view.js')
    edit_js = (
        '++resource++eea.dataservice.facetednavigation.dataservice.edit.js')
    view_css = (
        '++resource++eea.dataservice.facetednavigation.dataservice.view.css')
    edit_css = (
        '++resource++eea.dataservice.facetednavigation.dataservice.edit.css')

    index = ViewPageTemplateFile('widget.pt')
    edit_schema = AbstractWidget.edit_schema
