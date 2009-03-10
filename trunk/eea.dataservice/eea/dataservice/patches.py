from zope import event
from events import ObjectPortalTypeChanged
from Products.CMFCore.DynamicType import DynamicType
from collective.monkey.monkey import warn
#
# Patch CMFCore.DynamicType.DynamicType._setPortalTypeName
#
def notify_portal_type_changed(original_method):
    def wrapper(self, pt, *args, **kwargs):
        """ Set the portal type name.

        Called by portal_types during construction, records an ID that will be
        used later to locate the correct ContentTypeInformation.
        """
        res = original_method(self, pt, *args, **kwargs)
        event.notify(ObjectPortalTypeChanged(self, pt))
        return res
    return wrapper

warn("Patching CMFCore.DynamicType.DynamicType._setPortalTypeName in order to raise ObjectPortalTypeChanged")
DynamicType._setPortalTypeName = notify_portal_type_changed(
    DynamicType._setPortalTypeName)
