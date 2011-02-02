import logging
import transaction
from PIL import Image
from cStringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.statusmessages.interfaces import IStatusMessage
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL

from eea.dataservice.vocabulary import CONVERSIONS_DICTIONARY_ID

logger = logging.getLogger('eea.dataservice.converter')
info = logger.info

class ConvertMap(object):
    """ Convert the map in different image formats
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.formats = []

    def getFormats(self):
        if self.formats:
            return self.formats

        # By default generate zooming image PNG 75dpi
        self.formats = ['ZOOM-75']

        atvm = getToolByName(self.context, ATVOCABULARYTOOL)
        vocab = atvm[CONVERSIONS_DICTIONARY_ID]
        terms = vocab.getVocabularyDict()

        # Use only published vocabulary items for active convertion
        for key in terms.keys():
            wftool = getToolByName(self.context, 'portal_workflow')
            state = wftool.getInfoFor(vocab[key], 'review_state', '(Unknown)')
            if state == 'published':
                self.formats.append(key)
        return self.formats

    def get_aspect_ratio(self, width, height, to=2048):
        """ Get resize aspect ratio

            >>> ConvertMap(None, None).get_aspect_ratio(1024, 800, 640)
            (640, 500)

            >>> ConvertMap(None, None).get_aspect_ratio(1024, 1280)
            (1638, 2048)
        """
        to_w = to_h = to
        sw = float(to_w) / width
        sh = float(to_h) / height
        if sw == sh:
            return to_w, to_h
        elif sw < sh:
            to_h = int(round(sw * height))
        else:
            to_w = int(round(sh * width))
        return to_w, to_h

    def handle_image(self, im, output, fmt='PNG'):
        """ Convert to fmt: 2048x2048px, 75dpi with a tolerance of 20%
        """
        width, height = im.size
        if width >= 1640 or height >= 1640:
            im.dpi = 75
        else:
            dw = int(round(2048.0 / width))
            dh = int(round(2048.0 / height))
            im.dpi = 75 * min(dw, dh)
        im.load()

        width, height = im.size
        if width > 2450 or height > 2450:
            width, height = self.get_aspect_ratio(width, height, to=2048)
            try:
                im = im.resize((width, height), Image.ANTIALIAS)
            except AttributeError:
                im = im.resize((width, height))
        im.save(output, fmt)

    def __call__(self, cronjob=0, purge=True):
        err = 0

        # Delete (if neccesary) old converted images
        if purge:
            for convimg in self.context.objectValues('ImageFS'):
                self.context.manage_delObjects([convimg.getId()])

        # Create converted images
        field = self.context.getField('file')
        accessor = field.getAccessor(self.context)()
        if accessor:
            for format in self.getFormats():
                img_format, img_dpi = format.split('-')

                if img_dpi == 'default':
                    im_id = '.'.join((accessor.filename, img_format[:3].lower()))
                elif img_format == 'ZOOM':
                    im_id = '.'.join((accessor.filename, 'zoom.png'))
                else:
                    im_id = '.'.join((accessor.filename, img_dpi + 'dpi', img_format[:3].lower()))

                outfile = StringIO()
                try:
                    im = Image.open(StringIO(self.context.getFile().getBlob().open().read()))
                    if img_format == 'ZOOM':
                        self.handle_image(im, outfile, 'PNG')
                    else:
                        self.handle_image(im, outfile, img_format)
                except IOError, err:
                    logger.exception('IOError: %s', err)
                    err = 1
                    continue
                except (TypeError, ValueError), err:
                    logger.exception('Invalid dpi value: %s; err: %s',
                                     img_dpi, err)
                    err = 1
                    continue
                except OverflowError, err:
                    logger.exception('OverflowError: %s', err)
                    err = 1
                    continue

                file_data = outfile.getvalue()
                if not getattr(self.context, im_id, None):
                    im_id = self.context.invokeFactory('ImageFS', id=im_id)
                im_ob = getattr(self.context, im_id)
                im_ob.setImage(file_data)

                # We changed ImageFS worflow from eea_data_workflow to eea_imagefs_workflow
                # and we dont need anymore the below transitions

                ## Set state
                #wftool = getToolByName(self.context, 'portal_workflow')
                #try:
                    #wftool.doActionFor(im_ob, 'quickPublish',
                                       #comment='Set by convert figure action.')
                    #wftool.doActionFor(im_ob, 'hide',
                                       #comment='Set by convert figure action.')
                    #info('INFO: Convertion created %s', im_ob.getId())
                #except WorkflowException, err:
                    #logger.exception('WorkflowException: %s ImageFS %s', err, im_ob.absolute_url())
        else:
            logger.exception('Empty accessor: %s', accessor)
            err = 1

        msg = 'Done converting "%s".' % self.context.title_or_id()
        info('INFO: %s', msg)
        if err:
            msg = 'Some error(s) occured during conversion of "%s".' % self.context.title_or_id()

        if not self.request or cronjob:
            return msg
        IStatusMessage(self.request).addStatusMessage(msg, type='info')
        return self.request.RESPONSE.redirect(self.context.absolute_url())

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
                info('INFO: Start converting %s', ff_ob.getId())
                convertFigureView = ff_ob.unrestrictedTraverse('@@convertMap')
                convtmp = convertFigureView(cronjob=1)
                msg += 'CONVERTED: %s \r\n' % ff_ob.absolute_url()
                transaction.savepoint()

        return msg

class ConvertionInfo(object):
    """ Return info about the last convertion(s)
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        res = None
        images = self.context.objectValues('ImageFS')
        if images:
            res = images[0].ModificationDate()
        return res
