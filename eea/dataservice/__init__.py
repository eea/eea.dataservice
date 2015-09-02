""" Dataservice
"""
from Products.CMFCore import utils as cmfutils
from Products.Archetypes.atapi import process_types, listTypes
from eea.dataservice.config import PROJECTNAME, DEFAULT_ADD_CONTENT_PERMISSION

# Register custom content
from eea.dataservice import content
content.register()

def initialize(context):
    """ Initialize product (called by zope2)
    """
    #Initialize portal content
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types=content_types,
        permission=DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors=constructors,
        fti=ftis,
        ).initialize(context)
