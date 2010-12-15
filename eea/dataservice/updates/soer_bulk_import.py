# -*- coding: utf-8 -*-

""" Bulk import of SOER figures - first batch, see #3987 for more details
"""

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'
__credits__ = """contributions: Alec Ghica"""

from Products.Five.browser import BrowserView

# Logging
import logging
logger = logging.getLogger('eea.dataservice')
info = logger.info
info_exception = logger.exception


class BulkImportSoerFigures(BrowserView):
    """ Bulk import of SOER figures """

    def __call__(self):
        try:
            info('INFO: Done soer figures import!')
        except Exception, err:
            info('ERR: import error')
            info_exception(err)