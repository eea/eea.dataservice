# -*- coding: utf-8 -*-
__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

from Products.OrderableReferenceField._field import OrderableReferenceField
from Products.CMFCore.permissions import ModifyPortalContent
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

import Data
import Organisation
import DataFile
import DataTable
import EEAFigure
import EEAFigureFile
import ImageFS

# monkey patch, replaces reference field to an orderable reference field
from Products.EEAContentTypes.content.orderablereffield import field
from Products.Archetypes.ClassGen import generateMethods

schema = Data.Dataset_schema
field.schemata = 'relations'


# Data sets relations
field
schema.addField(field)
schema.moveField('relatedItems', pos='bottom');
schema['relatedItems'].widget.label = 'This dataset is derived from'
schema['relatedItems'].widget.description = 'Specify the datasets from which this dataset is derived.'
schema['relatedItems'].widget.startup_directory = 'data'

# Relations to products
prod_field = OrderableReferenceField(
    'relatedProducts',
    schemata = 'relations',
    relationship = 'relatesToProducts',
    multiValued = True,
    isMetadata = True,
    languageIndependent = False,
    index = 'KeywordIndex',
    write_permission = ModifyPortalContent,
    widget = ReferenceBrowserWidget(
        allow_search = True,
        allow_browse = True,
        allow_sorting = True,
        show_indexes = False,
        force_close_on_insert = True,
        label = "Relations to other EEA products",
        label_msgid = "label_related_products",
        description = "Specify relations to other EEA products within Plone.",
        description_msgid = "help_related_products",
        i18n_domain = "plone",
        visible = {'edit' : 'visible', 'view' : 'invisible' }
        )
    )

schema.addField(prod_field)

generateMethods(Data.Data, [field, prod_field])
