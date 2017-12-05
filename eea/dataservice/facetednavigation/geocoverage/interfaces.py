""" Interfaces
"""
from z3c.form import field
from eea.facetednavigation.widgets.checkbox.interfaces import (
  ICheckboxSchema,
  DefaultSchemata as DS,
  LayoutSchemata,
  DisplaySchemata,
  CountableSchemata,
)


class IGeoCoverageSchema(ICheckboxSchema):
    """ Schema
    """


class DefaultSchemata(DS):
    """ Schemata default
    """
    fields = field.Fields(IGeoCoverageSchema).select(
        u'title',
        u'index',
        u'operator',
        u'operator_visible',
        u'catalog',
        u'default'
    )


__all__ = [
    IGeoCoverageSchema.__name__,
    DefaultSchemata.__name__,
    LayoutSchemata.__name__,
    DisplaySchemata.__name__,
    CountableSchemata.__name__,
]
