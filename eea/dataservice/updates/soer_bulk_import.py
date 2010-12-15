# -*- coding: utf-8 -*-

""" Bulk import of SOER figures - first batch, see #3987 for more details
"""

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'
__credits__ = """contributions: Alec Ghica"""

from Products.Five.browser import BrowserView
from eea.dataservice.updates.soer_bulk_import_data import soer_data

# Logging
import logging
logger = logging.getLogger('eea.dataservice')
info = logger.info
info_exception = logger.exception


class BulkImportSoerFigures(BrowserView):
    """ Bulk import of SOER figures """

    import_steps = """
    1. export metadata in XML
    2. import from XML
        1. create EEAFigures
        2. create EEAFigureFiles
        3. extra mappings
        4. transactional
    3. generate import logs
    4. run a full test on unicorn (including files)
    """

    questions = """
    1. on http://unicorn:3333/project.html?project=1984853699455 the first
        7 rows must be deleted as are just my tooltip and example right?
    """

    def __call__(self):
        try:
            info('INFO: Done soer figures import!')
        except Exception, err:
            info('ERR: import error')
            info_exception(err)