""" RestAPI GET enpoints
"""
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from eea.dataservice.interfaces import IReportingObligations

class ROD(object):
    """ Get data provenances
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {"rods": {
            "@id": "{}/@rods".format(self.context.absolute_url()),
        }}

        if not expand:
            return result

        if IPloneSiteRoot.providedBy(self.context):
            return result

        result['rods']['items'] = []

        rods = getattr(self.context, 'reportingObligations', None) or []
        if not rods:
            return result

        obligations = getUtility(IReportingObligations)
        for name, term in obligations().items():
            name = str(name)
            if not name or name == '0':
                continue

            title = term.get('title')
            link = "https://rod.eionet.europa.eu/obligations/%s" % name

            source_title = term.get('source_title', title)
            source_name = term.get("source_id", name)
            source_link = "https://rod.eionet.europa.eu/instruments/%s" % source_name

            if name in rods:
                rod = {
                    "name": name,
                    "title": json_compatible(title),
                    "link": json_compatible(link),
                    "source_name": json_compatible(source_name),
                    "source_title": json_compatible(source_title),
                    "source_link": json_compatible(source_link),
                }
                result['rods']['items'].append(rod)
        return result


class RelatedItemsROD(ROD):
    """ Get data provenances
    """
    def refs(self):
        """ Get all references: related items and back references
        """
        getBRefs = getattr(self.context, 'getBRefs', lambda x: [])
        for ref in getBRefs('relatesTo'):
            yield ref

        getRelatedItems = getattr(
            self.context, 'getRelatedItems', lambda x: [])
        for ref in getRelatedItems():
            yield ref

    def __call__(self, expand=False):
        result = super(RelatedItemsROD, self).__call__(expand)

        if not expand:
            return result

        if IPloneSiteRoot.providedBy(self.context):
            return result

        existing = set()
        for ref in self.refs():
            if getattr(ref, 'portal_type', None) not in [
                'Data', 'ExternalDataSpec']:
                continue

            rods = ROD(ref, self.request).__call__(expand=True)
            for rod in rods.get('rods', {}).get('items', []):
                name = rod.get('name', '')
                if name in existing:
                    continue

                result['rods']['items'].append(rod)
                existing.add(name)
        return result


@implementer(IPublishTraverse)
class Get(Service):
    """GET"""

    def reply(self):
        """Reply"""
        info = ROD(self.context, self.request)
        return info(expand=True)["rods"]


@implementer(IPublishTraverse)
class GetRelatedItems(Service):
    """GET"""

    def reply(self):
        """Reply"""
        info = RelatedItemsROD(self.context, self.request)
        return info(expand=True)["rods"]
