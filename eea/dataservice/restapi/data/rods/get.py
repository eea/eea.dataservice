""" RestAPI GET enpoints
"""
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.schema.interfaces import IVocabularyFactory


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

        voc = getUtility(IVocabularyFactory, 'Obligations')
        for term in voc(self.context):
            name = term.value
            if not name or name == '0':
                continue
            title = term.title
            if name in rods:
                rod = {
                    "title": json_compatible(title),
                    "link": json_compatible(
                        "https://rod.eionet.europa.eu/obligations/%s" % name),
                    "name": name
                }
                result['rods']['items'].append(rod)
        return result


class RelatedItemsROD(ROD):
    """ Get data provenances
    """
    def __call__(self, expand=False):
        result = super(RelatedItemsROD, self).__call__(expand)

        if not expand:
            return result

        if IPloneSiteRoot.providedBy(self.context):
            return result

        existing = set()
        getBRefs = getattr(self.context, 'getBRefs', lambda x: [])
        getRelatedItems = getattr(
            self.context, 'getRelatedItems', lambda x: [])
        refs = [ref for ref in getBRefs('relatesTo')].extend(
            getRelatedItems())
        for ref in refs:
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
