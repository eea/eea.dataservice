# -*- coding: utf-8 -*-
__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'

import Data
import Organisation
import DataFile
import DataTable

# monkey patch, replaces reference field to an orderable reference field
from Products.EEAContentTypes.content.orderablereffield import field
from Products.Archetypes.ClassGen import generateMethods

schema = Data.Dataset_schema
field.schemata = "relations"

schema.addField(field)
schema.moveField('relatedItems', pos='bottom');
schema['relatedItems'].widget.label = 'This dataset is derived from'
schema['relatedItems'].widget.description = 'Specify the datasets from which this dataset is derived.'
schema['relatedItems'].widget.startup_directory = 'data'
generateMethods(Data.Data, [field])