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
IMPORT_PATH = "SITE/sandbox/soer-figures"
FILES_PATH = "/var/local/soer_files/FINAL_FIGURES"

class BulkImportSoerFigures(BrowserView):
    """ Bulk import of SOER figures """

    import_steps = """
    1. export metadata in XML
    2. import from XML
        1. create EEAFigures
        2. create EEAFigureFiles
        3. extra mappings
        4. [done] transactional import
        5. check encoding during import, e.g. José Barredo
    3. generate import logs
    4. run a full test on unicorn (including files)
    """

    questions = """
    1. what state should have imported figures and files?
    """

    def __call__(self):
        error_detected = False
        import_context = self.context.unrestrictedTraverse(IMPORT_PATH)
        counter = 0

        for row in soer_data['rows'][:2]:
            counter += 1

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
                if row['Object type'] == 'EEAFigure':
                    info('INFO: adding EEAFigure %s' % filepath)
                    #TODO: add logic

                    # pass title?
                    fig_id = import_context.invokeFactory(
                              type_name='EEAFigure',
                              id=import_context.generateUniqueId("EEAFigure"))

                    fig_ob = getattr(context, fig_id)
                    fig_ob.processForm(data=1, metadata=1, values=DATA_DICT)
                    fig_ob.setTitle(ind_title)
                    fig_ob.reindexObject()

                    current_parent = fig_ob
                    error_detected = False
                elif row['Object type'] == 'EEAFigureFile':
                    if error_detected:
                        info('ERROR: EEAFigureFile not added %s', filepath)
                    else:
                        #TODO: add logic
                        pass
                else:
                    error_detected = True
                    info('ERROR: unknown "Object type" on %s', filepath)
            except Exception, err:
                error_detected = True
                info('ERR: import error on %s', filepath)
                info_exception(err)

            if counter % 10 == 0:
                info('INFO: Transaction commited, step %s' % str(counter))
                transaction.commit()

        info('INFO: Done soer figures import!')







