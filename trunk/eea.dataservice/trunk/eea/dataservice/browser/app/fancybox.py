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

    @property
    def vocabulary(self):
        brains = self.context.getFolderContents(contentFilter={
            'portal_type': 'ImageFS',
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
            size = brain.getObjSize
            yield (uid, title, size)

class ContainerFancyBox(BrowserView):
    """ Return fancybox for container
    """
    @property
    def box(self):
        imgview = queryMultiAdapter((self.context, self.request), name=u'imgview')
        childview = getattr(imgview, 'img', None)
        child = getattr(childview, 'context', None)
        if not child:
            return self.context.title_or_id()

        fancybox = queryMultiAdapter((child, self.request), name=u'fancybox.html')
        if not fancybox:
            return self.context.title_or_id()
        return fancybox()
