import logging
from zope.interface import implements
from zope.component import queryMultiAdapter
from zope.publisher.interfaces import NotFound
from Products.Five.browser import BrowserView
from valentine.imagescales.browser.interfaces import IImageView
from valentine.imagescales.browser import atfield, atfolder

logger = logging.getLogger("eea.dataservice")

class ImageViewFigure(BrowserView):
    """ Get cover image from folder contents
    """
    implements(IImageView)

    def __init__(self, context, request):
        super(ImageViewFigure, self).__init__(context, request)

        brains = self.context.getFolderContents(contentFilter={
            'portal_type': 'EEAFigureFile',
            'review_state': ['published', 'visible'],
        }, full_objects = True)

        eeafile = None
        for brain in brains:
            children = brain.getFolderContents(contentFilter={
                'portal_type': 'ImageFS',
                'review_state': ['published', 'visible']
            })
            if not len(children):
                continue

            eeafile = brain
            break

        self.img = queryMultiAdapter((eeafile, request), name=u'imgview')

    def display(self, scalename='thumb'):
        if not self.img:
            return False
        return self.img.display(scalename)

    def __call__(self, scalename='thumb'):
        if self.display(scalename):
            return self.img(scalename)
        raise NotFound(self.request, scalename)

class ImageViewFigureFile(BrowserView):
    """ Get cover image from folder contents
    """
    implements(IImageView)

    def __init__(self, context, request):
        super(ImageViewFigureFile, self).__init__(context, request)
        images = context.getFolderContents(contentFilter={
            'portal_type': 'ImageFS',
            'review_state': ['published', 'visible'],
            'sort_on': 'getId',
            'sort_order': 'reverse',
        }, full_objects = True)

        # Get *.zoom.png
        children = [img for img in images
                    if img.getId().lower().endswith('.zoom.png')]

        # Fallback to *.png
        if not children:
            children = [img for img in images
                        if img.getId().lower().endswith('.png')]

        #Fallback to *.gif
        if not children:
            children = [img for img in images
                        if img.getId().lower().endswith('.gif')]

        self.original = None
        if children:
            self.original = children[0]

        if self.original:
            self.img = atfield.ImageView(self.original, request)
        else:
            self.img = atfolder.ImageView(context, request)

    def display(self, scalename='thumb'):
        if scalename == 'original':
            return not not self.original
        try:
            return self.img.display(scalename)
        except Exception, err:
            logger.exception(err)
            return False

    def __call__(self, scalename='thumb'):
        if self.display(scalename):
            if scalename == 'original':
                return self.original
            return self.img(scalename)
        raise NotFound(self.request, scalename)
