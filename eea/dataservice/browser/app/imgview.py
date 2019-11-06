""" Imagescale adapters
"""

import logging
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.publisher.interfaces import NotFound
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from eea.depiction.browser.interfaces import IImageView
from eea.depiction.browser import atfolder
logger = logging.getLogger("eea.dataservice")


class ImageViewFigure(BrowserView):
    """ Get cover image from folder contents
    """
    implements(IImageView)
    _img = False

    @property
    def img(self):
        """ img
        """
        if self._img is False:
            self._img = None

            here = '/'.join(self.context.getPhysicalPath())
            query = {
                'portal_type': 'EEAFigureFile',
                'path': {
                    'query': here,
                    'depth': 1
                },
                'sort_on': 'getObjPositionInParent'
            }

            ctool = getToolByName(self.context, 'portal_catalog')
            brains = ctool.unrestrictedSearchResults(**query)
            for idx, brain in enumerate(brains):
                doc = brain.getObject()
                imgview = queryMultiAdapter((doc, self.request), name=u'imgview')

                if imgview.img and getattr(imgview, 'original', None):
                    self._img = imgview
                    break

        return self._img

    def display(self, scalename='thumb'):
        """ Display?
        """
        if not self.img:
            return False
        return self.img.display(scalename)

    def __call__(self, scalename='thumb'):
        if not self.display(scalename):
            raise NotFound(self.request, scalename)
        return self.img(scalename)


class ImageViewFigureFile(BrowserView):
    """ Get cover image from folder contents
    """
    implements(IImageView)
    _img = False
    original = None

    @property
    def img(self):
        """ img
        """
        if self._img is False:
            self._img = None

            here = '/'.join(self.context.getPhysicalPath())
            query = {
                'portal_type': 'Image',
                'path': {
                    'query': here,
                    'depth': 1
                },
                'sort_on': 'getId'
            }

            ctool = getToolByName(self.context, 'portal_catalog')
            brains = ctool.unrestrictedSearchResults(**query)

            # Get *.zoom.png
            children = [brain for brain in brains
                        if brain.getId.lower().endswith('.zoom.png')]

            # Fallback to *.png
            if not children:
                children = [brain for brain in brains
                            if brain.getId.lower().endswith('.png')]

            #Fallback to *.gif
            if not children:
                children = [brain for brain in brains
                            if brain.getId.lower().endswith('.gif')]

            if children:
                self.original = children[0].getObject()

            if self.original:
                self._img = queryMultiAdapter((
                    self.original, self.request), name=u'imgview')
            else:
                self._img = atfolder.FolderImageView(
                    self.context, self.request)
        return self._img

    def display(self, scalename='thumb'):
        """ Display?
        """
        if not self.img:
            return False

        if scalename == 'original':
            return bool(self.original)
        return self.img.display(scalename)

    def __call__(self, scalename='thumb'):
        if self.display(scalename):
            if scalename == 'original':
                return self.original
            return self.img(scalename)
        raise NotFound(self.request, scalename)
