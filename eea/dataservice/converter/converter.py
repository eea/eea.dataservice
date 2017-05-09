""" Map Converter
"""

import logging
from cStringIO import StringIO
from AccessControl import SpecialUsers
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from PIL import Image

import zc.twist

import transaction
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from eea.dataservice.vocabulary import CONVERSIONS_DICTIONARY_ID
from plone.app.async.interfaces import IAsyncService
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.component import queryUtility

logger = logging.getLogger('eea.dataservice.converter')
log = logger.info


class Convertor(object):
    """Convert an Image to a usable image file
    """

    def __init__(self, context):
        self.context = context
        self.formats = []

    def getFormats(self):
        """ Get formats
        """
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
        im.convert('RGB').save(output, fmt)

    def is_image(self, im_id):
        """ Check if attachment is an image
        """
        data_sufixes = ['doc', 'pdf', 'docx', 'xls', 'xlsx', 'zip', 'ai',
                        'csv', 'ppt', 'txt', 'xlsm', ]
        im_id = im_id.lower()
        return not bool([x for x in data_sufixes if im_id.endswith(x)])

    def run(self, cronjob=0, purge=True):
        """ call
        """
        err = 0

        # Create converted images
        normalizer = queryUtility(IFileNameNormalizer)
        field = self.context.getField('file')
        accessor = field.getAccessor(self.context)()
        if accessor:
            for fmt in self.getFormats():
                img_format, img_dpi = fmt.split('-')
                if not self.is_image(accessor.filename):
                    err = 1
                    continue

                if img_dpi == 'default':
                    im_id = '.'.join((
                        accessor.filename, img_format[:3].lower()))
                elif img_format == 'ZOOM':
                    im_id = '.'.join((accessor.filename, 'zoom.png'))
                else:
                    im_id = '.'.join((
                        accessor.filename, img_dpi + 'dpi',
                        img_format[:3].lower()))

                im_id = normalizer.normalize(im_id)

                outfile = StringIO()
                try:
                    im = Image.open(StringIO(
                        self.context.getFile().getBlob().open().read()))
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
                    im_id = self.context.invokeFactory('Image', id=im_id)
                im_ob = getattr(self.context, im_id)
                im_ob.setImage(file_data)
                im_ob.reindexObject()

            # Delete (if neccesary) old converted images
            if purge:
                # 68012 use system user instead of context user as it might
                # not have permission to otherwise delete the leftover images
                oldSecurityManager = getSecurityManager()
                newSecurityManager(None, SpecialUsers.system)
                for cid in self.context.objectIds('ATBlob'):
                    if accessor.filename not in cid:
                        self.context.manage_delObjects([cid])
                setSecurityManager(oldSecurityManager)
        else:
            logger.exception('Empty accessor: %s', accessor)
            err = 1

        return err


class ConvertMap(object):
    """ Convert the map in different image formats
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, cronjob=0, purge=True):
        job = Convertor(self.context)
        err = job.run(cronjob, purge)

        msg = 'Done converting "%s".' % self.context.title_or_id()
        log('INFO: %s', msg)

        if err:
            msg = 'Some error(s) occured during conversion of "%s".' % (
                self.context.title_or_id(),
            )

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
            if not ff_ob.objectValues('ATBlob'):
                notConverted.append(ff_ob)

        if info:
            msg = ("Total EEAFigureFile(s): %s , "
                   "from which %s are not converted."
                   "\r\n" % (str(len(res)), str(len(notConverted))))

            if len(notConverted):
                msg += '\r\nNot converted EEAFigureFile(s):\r\n'
            for ff_ob in notConverted:
                msg += '%s\r\n' % ff_ob.absolute_url()
        else:
            for ff_ob in notConverted:
                log('INFO: Start converting %s', ff_ob.getId())
                convertFigureView = ff_ob.unrestrictedTraverse('@@convertMap')
                convertFigureView(cronjob=1)
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
        images = self.context.objectValues('ATBlob')
        if images:
            res = images[0].ModificationDate()
        return res


def task_convert_figure(figure,):
    """A plone.app.async task that converts figures
    """
    c = Convertor(figure)
    result = c.run(cronjob=1)
    return result


class QueueConvert(BrowserView):
    """Use plone.async to queue a task to convert this Image object
    """

    def __call__(self):
        async = getUtility(IAsyncService)
        job = async.queueJob(task_convert_figure, self.context)
        anno = IAnnotations(self.context)
        anno['convert_figure_job'] = job._p_oid
        return "OK"


class GetJobStatus(BrowserView):
    """Gets the status for convert jobs
    """

    def __call__(self):
        anno = IAnnotations(self.context)
        job_oid = anno.get('convert_figure_job')
        job = self.getAsyncJob(job_oid)
        if not job:
            return "nojob"
        else:
            if isinstance(job, dict):
                status = job['status']
                result = job['result']
            else:
                status = job.status
                result = job.result
            if status == 'completed-status' and \
                (isinstance(result, zc.twist.Failure) or result == 1):
                status = 'error-status'
            # 30695 remove actual job after it is completed in order
            # to avoid object import error when making a new version
            # or when importing the object after being exported
            if status == 'completed-status':
                anno['convert_figure_job'] = \
                    {'status': 'completed-status', 'result': 0}
            return status

    def getAsyncJob(self, oid):
        """ return async job
        """
        service = getUtility(IAsyncService)
        queue = service.getQueues()['']

        for job in queue:
            # job queued
            if job._p_oid == oid:
                return job
        for da in queue.dispatchers.values():
            for agent in da.values():
                for job in agent:
                    # job active
                    if job._p_oid == oid:
                        return job
                for job in agent.completed:
                    if isinstance(job.result, zc.twist.Failure):
                        # job dead
                        if job._p_oid == oid:
                            return job
                    else:
                        # job completed
                        if job._p_oid == oid:
                            return job
        return None
