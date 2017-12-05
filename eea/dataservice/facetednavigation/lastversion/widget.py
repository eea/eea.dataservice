""" Version widget
"""
from zope.interface import implements
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from eea.facetednavigation.widgets.widget import Widget as AbstractWidget

from eea.dataservice.facetednavigation.lastversion.interfaces import (
    ILastVersionWidget,
)
from eea.dataservice.facetednavigation.lastversion.interfaces import (
    DefaultSchemata,
    LayoutSchemata
)

class Widget(AbstractWidget):
    """ Widget
    """
    implements(ILastVersionWidget)

    # Widget properties
    widget_type = 'lastversion'
    widget_label = 'Show most recent version'

    index = ViewPageTemplateFile('widget.pt')
    groups = (DefaultSchemata, LayoutSchemata)
