""" Imagescale adapters
"""
from AccessControl import SpecialUsers
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
#from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from eea.depiction.browser import atfield, atfolder
from eea.depiction.browser.interfaces import IImageView
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.publisher.interfaces import NotFound
import logging

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

        #wftool = getToolByName(context, "portal_workflow")
        #published_states = ['published', 'visible']
        #isdraft = wftool.getInfoFor(context, 'review_state') not in published_states

        q = {}
        #if not isdraft: #handle the case when the figure is "first draft"
            #q['review_state'] = published_states

        objs = self.context.getFolderContents(
                   contentFilter=dict(q, portal_type='EEAFigureFile'), 
                   full_objects = True)

        eeafile = None
        for obj in objs:
            children = obj.getFolderContents(
                            contentFilter=dict(q, portal_type='Image'))
            if not len(children):
                continue

            eeafile = obj
            break

        self.img = queryMultiAdapter((eeafile, request), name=u'imgview')

    def display(self, scalename='thumb'):
        """ Display?
        """
        if not self.img:
            return False
        return self.img.display(scalename)

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

        #wftool = getToolByName(context, "portal_workflow")
        #published_states = ['published', 'visible']
        #isdraft = wftool.getInfoFor(context, 'review_state') not in published_states
        q = {
            'portal_type': ['Image'],
            'sort_on': 'getId',
            'sort_order': 'reverse',
        }
        #if not isdraft:
            #q['review_state'] = published_states

        images = context.getFolderContents(contentFilter=q, full_objects = True)

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
            return not not self.original
        try:
            return self.img.display(scalename)
        except Exception, err:
            logger.exception(err)
            return False

    def __call__(self, scalename='thumb'):
        if self.display(scalename):
            if scalename == 'original':
                setSecurityManager(self.oldSecurityManager) 
                return self.original
            res = self.img(scalename)
            setSecurityManager(self.oldSecurityManager) 
            return res
        raise NotFound(self.request, scalename)
