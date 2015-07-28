""" Custom templates
"""
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five import BrowserView

TEMPLATE_CONTAINER = 'templates'
TEMPLATE_TYPES = ['EEAFigure', 'Data']


def getTemplatesPath(context):
    """ Get template path
    """
    phy_path = []
    phy_path.extend(context.getPhysicalPath()[:-1])
    phy_path.extend([TEMPLATE_CONTAINER])
    return '/'.join(phy_path)


class GetTemplates(object):
    """ Apply selected template metadata to a EEA Figure
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        path = getTemplatesPath(self.context)
        cat = getToolByName(self.context, 'portal_catalog', None)
        return cat(portal_type=TEMPLATE_TYPES,
                   path=path)


class SelectTemplate(BrowserView):
    """ Select template view
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request


class ApplyTemplate(object):
    """ Apply selected template metadata to a EEA Figure
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, template=''):
        if template:
            path = getTemplatesPath(self.context)
            cat = getToolByName(self.context, 'portal_catalog', None)
            res = cat(portal_type=TEMPLATE_TYPES,
                      path=path,
                      getId=template)
            tpl_ob = res[0].getObject()

            for field_name in tpl_ob.schema.keys():
                tpl_field = tpl_ob.getField(field_name)
                tpl_value = tpl_field.getAccessor(tpl_ob)()

                ob_field = self.context.getField(field_name)
                ob_value = ob_field.getAccessor(self.context)()

                if not ob_value and tpl_value:
                    ob_field.getMutator(self.context)(tpl_value)

            cat.reindexObject(self.context)
            msg = "Template metadata applyed."
        else:
            msg = "No template selected."

        if not self.request:
            return msg
        IStatusMessage(self.request).addStatusMessage(msg, type='info')
        return self.request.RESPONSE.redirect(self.context.absolute_url())
