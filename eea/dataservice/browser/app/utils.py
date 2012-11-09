""" EEA Dataservice browser utils 
"""
from Products.Five import BrowserView
from Products.CMFPlone.utils import getToolByName

class VisibleRelatedProducts(BrowserView):
    """Registered as @@related_products
    """
    def __call__(self):
        products = self.context.getRelatedProducts()
        mtool = getToolByName(self.context, 'portal_membership')
        return [p for p in products if mtool.checkPermission('View', p)]
