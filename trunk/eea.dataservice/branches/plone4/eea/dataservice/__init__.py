""" Dataservice
"""
from os.path import dirname

from Globals import package_home
from Products.CMFCore import utils as cmfutils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.Archetypes.atapi import process_types, listTypes
from eea.dataservice.config import PROJECTNAME, DEFAULT_ADD_CONTENT_PERMISSION
from eea.dataservice import pil
# inserted to shut off pylint about unused import
pil

def initialize(context):
    """ Initialize product (called by zope2)
    """
    #Initialize portal content
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)
