""" eea.rdfmarshaller customizations for eea.dataservice
"""
from eea.rdfmarshaller.interfaces import ISurfSession
from eea.rdfmarshaller.marshaller import ATField2Surf
from zope.component import adapts
from eea.dataservice.fields.ManagementPlanField import ManagementPlanField

class ManagementPlanField2Surf(ATField2Surf):
    """ Base implementation of IATField2Surf
    """
    adapts(ManagementPlanField, ISurfSession)

    def value(self, context):
        """ Value
        """
        v = self.field.getAccessor(context)()
        if v and (len(v) == 2):
            return "%s %s" % (v[0], v[1])
        return " - ".join(v)
