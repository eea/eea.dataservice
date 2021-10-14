""" RestAPI GET enpoints
"""
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter, getUtility
from zope.interface import Interface, implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.schema.interfaces import IVocabularyFactory


@implementer(IExpandableElement)
@adapter(Interface, Interface)
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


@implementer(IPublishTraverse)
class Get(Service):
    """GET"""

    def reply(self):
        """Reply"""
        info = ROD(self.context, self.request)
        return info(expand=True)["rods"]
