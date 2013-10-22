""" eea.rdfmarshaller customizations for eea.dataservice
"""

from Products.CMFPlone.utils import getToolByName
from Products.Archetypes.atapi import LinesField
from eea.forms.fields.ManagementPlanField import ManagementPlanField
from eea.rdfmarshaller.archetypes.fields import ATField2Surf
from eea.rdfmarshaller.interfaces import ISurfResourceModifier
from eea.rdfmarshaller.interfaces import ISurfSession
from zope.component import adapts, getMultiAdapter
from zope.interface import Interface, implements


class ManagementPlanField2Surf(ATField2Surf):
    """ Base implementation of IATField2Surf
    """
    adapts(ManagementPlanField, Interface, ISurfSession)

    def value(self):
        """ Value
        """
        v = self.field.getAccessor(self.context)()
        if v and (len(v) == 2):
            return "%s %s" % (v[0], v[1])
        return (" - ".join(v), None)


class TemporalCoverageField2Surf(ATField2Surf):
    """ temporalCoverage rdf export which removes export if it's value contains
    -1 from the dynamic entry
    """
    adapts(LinesField, Interface, ISurfSession)

    def value(self):
        """ Value
        """
        v = self.field.getAccessor(self.context)()
        return "" if (v and v[0] == '-1') else v


class ExtraMimetype2SurfModifier(object):
    """Modifier for content types that want to publish info about
    their file mimetypes
    """

    implements(ISurfResourceModifier)

    def __init__(self, context):
        self.context = context

    def run(self, resource, *args, **kwds):
        """change the rdf resource
        """
        catalog = getToolByName(self.context, "portal_catalog")
        indexer = getMultiAdapter((self.context, catalog), name="filetype")
        mimetypes = indexer()
        if not mimetypes:
            return
        setattr(resource, "dcterms_format", [(m, None) for m in mimetypes])
        resource.save()
        return resource
