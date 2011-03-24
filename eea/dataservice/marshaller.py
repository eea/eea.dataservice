""" eea.rdfmarshaller customizations for eea.dataservice
"""

from Products.Archetypes.interfaces import IField
from eea.rdfmarshaller.interfaces import IArchetype2Surf, ISurfSession
from eea.rdfmarshaller.marshaller import ATField2RdfSchema
from zope.component import adapts
from zope.interface import implements, Interface


class ManagementField2RdfSchema(ATField2RdfSchema):
    """IArchetype2Surf implemention for Fields"""

    implements(IArchetype2Surf)
    adapts(IField, Interface, ISurfSession)

