# -*- coding: utf-8 -*-

""" Bulk import of SOER figures - first batch, see #3987 for more details
"""

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'
__credits__ = """contributions: Alec Ghica"""

import transaction
from Products.Five.browser import BrowserView
from eea.dataservice.updates.soer_bulk_import_data import soer_data

# Logging
import logging
logger = logging.getLogger('eea.dataservice')
info = logger.info
info_exception = logger.exception

# Configuration
IMPORT_PATH = "/www/SITE/sandbox/soer-figures"
FILES_PATH = "/var/local/soer_files/FINAL_FIGURES"

class BulkImportSoerFigures(BrowserView):
    """ Bulk import of SOER figures """

    import_steps = """
    1. export metadata in XML
    2. import from XML
        1. create EEAFigures
        2. create EEAFigureFiles
        3. extra mappings
        4. transactional import
        5. check encoding during import, e.g. José Barredo
    3. generate import logs
    4. run a full test on unicorn (including files)
    """

    questions = """
    1. what state should have imported figures and files?
    """

    def __call__(self):
        for row in soer_data['rows']:
            object_type = row["Object type"]
            filepath = row["Filepath"]
            category = row["Category"]
            title = row["Title"]
            creators = row["Creators"]
            contributors = row["Contributors"]
            copyrights = row["Copyrights"]
            keywords = row["Keywords"]
            figure_type = row["Figure type"]
            description = row["Description"]
            themes = row["Themes"]
            geo_coverage = row["Geographical coverage"]
            eea_management_plan = row["EEA Management Plan"]
            last_upload = row["Last upload"]
            owner = row["Owner"]
            processor = row["Processor"]
            tem_coverage = row["Temporal coverage"]
            contact = row["Contact person(s) for EEA"]
            source = row["Source"]
            additional_information = row["Additional information"]
            methodology = row["Methodology"]
            unit = row["Unit"]

            try:
                import pdb; pdb.set_trace()
                if row['Object type'] == 'EEAFigure':
                    pass
                elif row['Object type'] == 'EEAFigureFile':
                    pass
                else:
                    info('ERROR: unknown "Object type" on %s', filepath)
            except Exception, err:
                info('ERR: import error on %s', filepath)
                info_exception(err)

        transaction.commit()
        info('INFO: Done soer figures import!')







