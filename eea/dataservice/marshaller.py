""" eea.rdfmarshaller customizations for eea.dataservice
"""

from Products.Archetypes.interfaces import IField
from eea.rdfmarshaller.interfaces import IArchetype2Surf, ISurfSession
from eea.rdfmarshaller.marshaller import ATField2RdfSchema, ATField2Surf
from zope.component import adapts
from zope.interface import implements, Interface
from eea.dataservice.fields.ManagementPlanField import ManagementPlanField


class ManagementPlanField2Surf(ATField2Surf):
    """Base implementation of IATField2Surf"""
    adapts(ManagementPlanField, ISurfSession)

    def value(self, context):
        v = self.field.getAccessor(context)()
        if v and (len(v) == 2):
            return "Year: %s, code: %s" % (v[0], v[1])
        return " - ".join(v)


