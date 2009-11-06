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
        files = self.context.objectValues('EEAFigureFile')
        for obj in files:
            if obj.getCategory() == 'hard':
                eeafile = obj
                break
        if not eeafile and len(files):
                eeafile = files[0]

        if eeafile:
            children = [img for img in eeafile.objectValues('ImageFS')
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
        super(ImageViewFigureFile, self).__init__(context, request)
        children = [img for img in context.objectValues('ImageFS')
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
