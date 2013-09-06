""" Custom AT Content-Types
"""
from Products.Archetypes.atapi import registerType

from eea.dataservice.config import PROJECTNAME
from eea.dataservice.content import Data
from eea.dataservice.content import Organisation
from eea.dataservice.content import DataFile
from eea.dataservice.content import DataTable
from eea.dataservice.content import EEAFigure
from eea.dataservice.content import EEAFigureFile

def register():
    """ Register AT Content-Types
    """
    registerType(Data.Data, PROJECTNAME)
    registerType(Organisation.Organisation, PROJECTNAME)
    registerType(DataFile.DataFile, PROJECTNAME)
    registerType(DataTable.DataTable, PROJECTNAME)
    registerType(EEAFigure.EEAFigure, PROJECTNAME)
    registerType(EEAFigureFile.EEAFigureFile, PROJECTNAME)
