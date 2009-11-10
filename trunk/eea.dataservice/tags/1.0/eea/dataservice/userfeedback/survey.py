""" Survey for download files
"""
from zope.interface import implements
from zope.app.annotation.interfaces import IAnnotations
from zope.component import queryUtility, getMultiAdapter
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.app.schema.vocabulary import IVocabularyFactory
from interfaces import ISurvey, ISurveySupport, ISurveyView

ANNO_KEY = 'EEAUserFeedback-DISABLED'

class SurveySupport(BrowserView):
    implements(ISurveySupport)
    @property
    def disabled(self):
        """ Can enable
        """
        anno = IAnnotations(self.context)
        if anno.get(ANNO_KEY):
            return True
        return False

    @property
    def enabled(self):
        """ Can disable
        """
        anno = IAnnotations(self.context)
        if anno.get(ANNO_KEY):
            return False
        return True

class Survey(BrowserView):
    """ Survey form and support
    """
    implements(ISurvey)
    #
    # Private interface
    #
    def _redirect(self, msg):
        if self.request:
            url = self.context.absolute_url()
            IStatusMessage(self.request).addStatusMessage(msg, type='info')
            self.request.response.redirect(url)
        return msg

    @property
    def _versions(self):
        versions = getMultiAdapter((self.context, self.request),
                                   name=u'getVersions')
        if not versions:
            raise StopIteration
        versions = versions()
        for version in versions.values():
            yield version
    #
    # Public interface
    #
    def enable(self):
        """ Enable
        """
        for version in self._versions:
            anno = IAnnotations(version)
            if anno.get(ANNO_KEY):
                del anno[ANNO_KEY]
        return self._redirect('EEAUserFeedback enabled')

    def disable(self):
        """ Disable
        """
        for version in self._versions:
            anno = IAnnotations(version)
            anno[ANNO_KEY] = True
        return self._redirect('EEAUserFeedback disabled')

class SurveyView(BrowserView):
    """ Survey view
    """
    implements(ISurveyView)
    def vocabulary(self, name):
        vocab = queryUtility(IVocabularyFactory, name=name.decode('utf-8'))
        if not vocab:
            raise StopIteration
        for item in vocab(self.context):
            yield item.value, item.title
