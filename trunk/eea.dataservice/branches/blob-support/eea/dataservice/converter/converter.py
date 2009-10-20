import logging
from PIL import Image
from cStringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL

from eea.dataservice.vocabulary import CONVERSIONS_DICTIONARY_ID

logger = logging.getLogger('eea.dataservice.converter')

class ConvertMap(object):
    """ Convert the map in different image formats
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getFormats(self):
        formats = []
        atvm = getToolByName(self.context, ATVOCABULARYTOOL)
        vocab = atvm[CONVERSIONS_DICTIONARY_ID]
        terms = vocab.getVocabularyDict()

        # Use only published vocabulary items for active convertion
        for key in terms.keys():
            wftool = getToolByName(self.context, 'portal_workflow')
            state = wftool.getInfoFor(vocab[key], 'review_state', '(Unknown)')
            if state == 'published':
                formats.append(key)

        return formats

    def __call__(self, cronjob=0):
        err = 0

        # Delete (if neccesary) old converted images
        for convimg in self.context.objectValues('ImageFS'):
            self.context.manage_delObjects([convimg.getId()])

        # Create converted images
        field = self.context.getField('file')
        accessor = field.getAccessor(self.context)()
        if accessor:
            for format in self.getFormats():
                img_format, img_dpi = format.split('-')
                outfile = StringIO()

                try:
                    im = Image.open(StringIO(self.context.getFile().getBlob().open().read()))
                    if img_dpi == 'default':
                        im.dpi = 400
                        im.save(outfile, img_format)
                    else:
                        im.dpi = int(img_dpi)
                        p_dpi = (im.dpi, im.dpi)
                        im.save(outfile, img_format, dpi=p_dpi)
                except IOError, err:
                    logger.exception('IOError: %s', err)
                    err = 1
                    continue
                except (TypeError, ValueError), err:
                    logger.exception('Invalid dpi value: %s; err: %s',
                                     img_dpi, err)
                    err = 1
                    continue


                file_data = outfile.getvalue()
                if img_dpi == 'default':
                    im_id = accessor.filename + '.' + img_format[:3].lower()
                else:
                    im_id = accessor.filename + '.' + img_dpi + 'dpi.' + img_format[:3].lower()

                if not getattr(self.context, im_id, None):
                    im_id = self.context.invokeFactory('ImageFS', id=im_id)
                im_ob = getattr(self.context, im_id)
                im_ob.setImage(file_data)

                # Set state
                wftool = getToolByName(self.context, 'portal_workflow')
                wftool.doActionFor(im_ob, 'quickPublish',
                                   comment='Set by convert figure action.')
                wftool.doActionFor(im_ob, 'hide',
                                   comment='Set by convert figure action.')
        else:
            logger.exception('Empty accessor: %s', accessor)
            err = 1

        msg = 'Done converting "%s".' % self.context.title_or_id()
        if err:
            msg = 'Some error(s) occured during conversion of "%s".' % self.context.title_or_id()

        if not self.request or cronjob:
            return msg
        IStatusMessage(self.request).addStatusMessage(msg, type='info')
        return self.request.RESPONSE.redirect(self.context.absolute_url())

class ConvertAllMaps(object):
    """ Convert all the maps found in the current context
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if self.request.form.has_key('convert'):
            #Convert
            msg = "Conversion finnished."
            for ob in self.context.objectValues('EEAFigureFile'):
                obConvert = ob.unrestrictedTraverse('@@convertMap')
                obConvert()

            IStatusMessage(self.request).addStatusMessage(msg, type='info')
            return self.request.RESPONSE.redirect(self.context.absolute_url())
        else:
            #Cancel
            msg = "Convertion canceled."
            IStatusMessage(self.request).addStatusMessage(msg, type='info')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

class ConvertAction(object):
    """ Convert all the maps found in the current context
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        msg = "This operation might take some time."
        if not self.request:
            return msg
        IStatusMessage(self.request).addStatusMessage(msg, type='info')
        return self.request.RESPONSE.redirect(self.context.absolute_url() + '/convert_maps')

class CheckFiguresConvertion(object):
    """ Check all EEAFigureFiles if are converted and converts them if not
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, info=0):
        msg = ''
        ctool = getToolByName(self.context, 'portal_catalog')
        res = ctool.searchResults({'portal_type' : 'EEAFigureFile',
                                   'show_inactive': True})

        notConverted = []
        for brain in res:
            ff_ob = brain.getObject()
            if not ff_ob.objectValues('ImageFS'):
                notConverted.append(ff_ob)

        if info:
            msg = "Total EEAFigureFile(s): %s , from which %s are not converted.\r\n" % (str(len(res)), str(len(notConverted)))
            if len(notConverted):
                msg += '\r\nNot converted EEAFigureFile(s):\r\n'
            for ff_ob in notConverted:
                msg += '%s\r\n' % ff_ob.absolute_url()
        else:
            for ff_ob in notConverted:
                convertFigureView = ff_ob.unrestrictedTraverse('@@convertMap')
                convtmp = convertFigureView(cronjob=1)
                msg += 'CONVERTED: %s \r\n' % ff_ob.absolute_url()

        return msg
