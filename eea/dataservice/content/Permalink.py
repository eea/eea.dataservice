""" Permalink
"""
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from zope.interface import Interface
from zope.interface import implements
from zope import schema
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

zmi_addPermalinkMapping_html = PageTemplateFile(
    'zmi_permalink_mapping_add.pt', globals())


class IPermalinkSettings(Interface):
    """ Permalink Settings
    """
    versionId = schema.TextLine(
        title=u'Version Id',
        description=u'Version id used instead of id for ds_resolveuid lookup',
        required=True
    )


class PermalinkMapping(SimpleItem):
    """ Permalink Mapping from old versionId to new versionId
    """
    meta_type = "EEA Permalink Mapping"
    security = ClassSecurityInfo()
    implements(IPermalinkSettings)

    def __init__(self, p_id, versionId="Versions Id"):
        super(PermalinkMapping, self).__init__()
        self._setId(p_id)
        self.versionId = versionId


def zmi_addPermalinkMapping(parent, id, versionId, REQUEST=None):
    """ Create a new PermalinkMapping obj """

    ob = PermalinkMapping(id, versionId)
    parent._setObject(id, ob)
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(
            parent.absolute_url() + '/manage_workspace')


def initialize(context):
    """ initialize PermalinkMapping
    """
    from AccessControl.Permissions import view_management_screens
    context.registerClass(
        PermalinkMapping,
        permission=view_management_screens,
        constructors=(zmi_addPermalinkMapping_html, zmi_addPermalinkMapping)
    )
