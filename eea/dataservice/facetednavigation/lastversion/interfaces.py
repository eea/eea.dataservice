""" Interfaces
"""
from z3c.form import field
from eea.facetednavigation.interfaces import IWidget
from eea.facetednavigation.widgets.interfaces import ISchema
from eea.facetednavigation.widgets.interfaces import DefaultSchemata as DS
from eea.facetednavigation.widgets.interfaces import LayoutSchemata


class ILastVersionWidget(IWidget):
    """ Last version widget
    """


class ILastVersionSchema(ISchema):
    """ Schema
    """


class DefaultSchemata(DS):
    """ Schemata default
    """
    fields = field.Fields(ILastVersionSchema).select(
        u'title',
    )


__all__ = [
    ILastVersionWidget.__name__,
    ILastVersionSchema.__name__,
    DefaultSchemata.__name__,
    LayoutSchemata.__name__,
]
