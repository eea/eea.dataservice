""" Imagescale adapters
"""

import logging
from AccessControl import SpecialUsers
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from Products.Five.browser import BrowserView
from eea.depiction.browser import atfield, atfolder
from eea.depiction.browser.interfaces import IImageView
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.publisher.interfaces import NotFound


logger = logging.getLogger("eea.dataservice")

class ImageViewFigure(BrowserView):
    """ Get cover image from folder contents
    """
    implements(IImageView)
    oldSecurityManager = None

    def __init__(self, context, request):
        super(ImageViewFigure, self).__init__(context, request)

        self.oldSecurityManager = getSecurityManager()
        newSecurityManager(request, SpecialUsers.system)

        objs = self.context.objectValues("EEAFigureFile")

        eeafile = None
        for obj in objs:
            children = obj.objectValues("ATBlob")
            if not len(children):
                continue

            eeafile = obj
            break

        self.img = queryMultiAdapter((eeafile, request), name=u'imgview')

    def display(self, scalename='thumb'):
        """ Display?
        """
        if not self.img:
            setSecurityManager(self.oldSecurityManager)
            return False
        res = self.img.display(scalename)
        setSecurityManager(self.oldSecurityManager)
        return res

    def __call__(self, scalename='thumb'):
        if self.display(scalename):
            res = self.img(scalename)
            setSecurityManager(self.oldSecurityManager)
            return res

        setSecurityManager(self.oldSecurityManager)
        raise NotFound(self.request, scalename)


class ImageViewFigureFile(BrowserView):
    """ Get cover image from folder contents
    """
    implements(IImageView)

    def __init__(self, context, request):
        super(ImageViewFigureFile, self).__init__(context, request)

        self.oldSecurityManager = getSecurityManager()
        newSecurityManager(request, SpecialUsers.system)

        images = sorted(context.objectValues("ATBlob"),
                        lambda a, b: cmp(b.getId(), a.getId()))

        # Get *.zoom.png
        children = [zimg for zimg in images
                    if zimg.getId().lower().endswith('.zoom.png')]

        # Fallback to *.png
        if not children:
            children = [pimg for pimg in images
                        if pimg.getId().lower().endswith('.png')]

        #Fallback to *.gif
        if not children:
            children = [gimg for gimg in images
                        if gimg.getId().lower().endswith('.gif')]

        self.original = None
        if children:
            self.original = children[0]

        if self.original:
            self.img = atfield.ATFieldImageView(self.original, request)
        else:
            self.img = atfolder.FolderImageView(context, request)

    def display(self, scalename='thumb'):
        """ Display?
        """
        if scalename == 'original':
            res = bool(self.original)
            setSecurityManager(self.oldSecurityManager)
            return res
        try:
            res = self.img.display(scalename)
            setSecurityManager(self.oldSecurityManager)
            return res
        except Exception, err:
            logger.exception(err)
            setSecurityManager(self.oldSecurityManager)
            return False

    def __call__(self, scalename='thumb'):
        if self.display(scalename):
            if scalename == 'original':
                setSecurityManager(self.oldSecurityManager)
                return self.original
            res = self.img(scalename)
            setSecurityManager(self.oldSecurityManager)
            return res
        setSecurityManager(self.oldSecurityManager)
        raise NotFound(self.request, scalename)
