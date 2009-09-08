from os.path import dirname

from Globals import package_home
from Products.CMFCore import utils as cmfutils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.Archetypes.atapi import process_types, listTypes
from config import PROJECTNAME, DEFAULT_ADD_CONTENT_PERMISSION

ppath = cmfutils.ProductsPath
cmfutils.ProductsPath.append(dirname(package_home(globals())))
registerDirectory('skins', globals())
cmfutils.ProductsPath = ppath

import catalog

def initialize(context):
    """initialize product (called by zope)"""

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
