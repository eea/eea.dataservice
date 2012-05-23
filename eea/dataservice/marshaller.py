""" eea.rdfmarshaller customizations for eea.dataservice
"""

#from eea.dataservice.interfaces import IDatafile

from Products.CMFPlone.utils import getToolByName
from eea.forms.fields.ManagementPlanField import ManagementPlanField
from eea.rdfmarshaller.interfaces import ISurfSession
from eea.rdfmarshaller.marshaller import ATField2Surf, ATCT2Surf
from zope.component import adapts, getMultiAdapter
#from zope.interface import Interface


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


class ExtraMimetype2Surf(ATCT2Surf):
    """generic adapter for content types that want to publish info about
    their file mimetypes
    """
    #adapts(Interface, ISurfSession)

    def _schema2surf(self):
        """override"""
        resource = super(ExtraMimetype2Surf, self)._schema2surf()
        catalog = getToolByName(self.context, "portal_catalog")
        indexer = getMultiAdapter((self.context, catalog), name="filetype")
        mimetypes = indexer()
        if not mimetypes:
            return
        setattr(resource, "dcterms_format", [(m, None) for m in mimetypes])
        resource.save()
        return resource
