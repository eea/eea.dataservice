""" Fancybox
"""
from zope.component import queryMultiAdapter
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from eea.dataservice.vocabulary import CONVERSIONS_DICTIONARY_ID

class FancyBox(BrowserView):
    """ View to use within fancybox jquery plugin
    """
    def get_title(self, uid, mapping):
        """ Get title by uid from mapping dictionary
        """
        for key, title in mapping.items():
            ext, dpi = key.split('-')
            ext = ext.lower()[:3]
            if dpi != 'default':
                ext = '.%sdpi.%s' % (dpi, ext)
            else:
                ext = '.%s' % ext
            if uid.lower().endswith(ext):
                return title
        return uid

    def get_size(self, brain):
        """ Get size
        """
        size = brain.getObjSize
        if size and size not in ('0 kB', u'0 kB'):
            return size

        displaySize = queryMultiAdapter(
            (self.context, self.request), name=u'displaySize')
        if not displaySize:
            return size

        doc = brain.getObject()
        get_size = getattr(doc, 'get_size', None)
        if not get_size:
            return size

        size = get_size()
        return displaySize(size)

    @property
    def vocabulary(self):
        """ Vocabulary
        """
        brains = self.context.getFolderContents(contentFilter={
            'portal_type': ['Image'],
            'review_state': ['published', 'visible'],
        })
        vtool = getToolByName(self.context, 'portal_vocabularies')
        voc = vtool.get(CONVERSIONS_DICTIONARY_ID, None)
        if voc:
            mapping = voc.getVocabularyDict()
        else:
            mapping = {}

        for brain in brains:
            uid = brain.getId
            if '.zoom.png' in uid:
                continue

            title = self.get_title(uid, mapping)
            size = self.get_size(brain)
            yield (uid, title, size)

class ContainerFancyBox(BrowserView):
    """ Return fancybox for container
    """
    @property
    def box(self):
        """ Box
        """
        imgview = queryMultiAdapter(
            (self.context, self.request), name=u'imgview')

        childview = getattr(imgview, 'img', None)
        child = getattr(childview, 'context', None)
        if not child:
            return self.context.title_or_id()

        fancybox = queryMultiAdapter(
            (child, self.request), name=u'fancybox.html')

        if not fancybox:
            return self.context.title_or_id()
        return fancybox()
