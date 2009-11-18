from zope.interface import implements
from zope.publisher.interfaces import NotFound
from Products.Five.browser import BrowserView
from valentine.imagescales.browser.interfaces import IImageView
from valentine.imagescales.browser import atfield, atfolder

class ImageViewFigure(BrowserView):
    """ Get cover image from folder contents
    """
    implements(IImageView)

    def __init__(self, context, request):
        super(ImageViewFigure, self).__init__(context, request)
        eeafile = None
        images = []
        files = self.context.getFolderContents(contentFilter={
            'portal_type': 'EEAFigureFile',
            'review_state': ['published', 'visible'],
        }, full_objects = True)

        for obj in files:
            if obj.getCategory() == 'hard':
                eeafile = obj
                break
        if not eeafile and len(files):
                eeafile = files[0]

        if eeafile:
            ibrains = eeafile.getFolderContents(contentFilter={
                'portal_type': 'ImageFS',
                'review_state': ['published', 'visible'],
            })
            [images.append(brain.getObject()) for brain in ibrains]
            children = [img for img in images
                        if img.getId().lower().endswith('.png')]
            if children:
                self.original = children[0]
                self.img = atfield.ImageView(self.original, request)
            else:
                self.original = None
                self.img = atfolder.ImageView(eeafile, request)
        else:
            self.original = None
            self.img = atfolder.ImageView(context, request)

    def display(self, scalename='thumb'):
        if scalename == 'original':
            return not not self.original
        return self.img.display(scalename)

    def __call__(self, scalename='thumb'):
        if self.display(scalename):
            if scalename == 'original':
                return self.original
            return self.img(scalename)
        raise NotFound(self.request, scalename)


class ImageViewFigureFile(BrowserView):
    """ Get cover image from folder contents
    """
    implements(IImageView)

    def __init__(self, context, request):
        images = []
        super(ImageViewFigureFile, self).__init__(context, request)
        images = context.getFolderContents(contentFilter={
            'portal_type': 'ImageFS',
            'review_state': ['published', 'visible'],
        }, full_objects = True)

        children = [img for img in images
                    if img.getId().lower().endswith('.png')]
        if children:
            self.original = children[0]
            self.img = atfield.ImageView(self.original, request)

        else:
            self.original = None
            self.img = atfolder.ImageView(context, request)

    def display(self, scalename='thumb'):
        if scalename == 'original':
            return not not self.original
        return self.img.display(scalename)

    def __call__(self, scalename='thumb'):
        if self.display(scalename):
            if scalename == 'original':
                return self.original
            return self.img(scalename)
        raise NotFound(self.request, scalename)
