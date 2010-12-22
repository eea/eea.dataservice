# -*- coding: utf-8 -*-

""" Bulk import of SOER figures - first batch, see #3987 for more details
"""

__author__ = """European Environment Agency (EEA)"""
__docformat__ = 'plaintext'
__credits__ = """contributions: Alec Ghica"""

from eea.dataservice.updates.soer_bulk_import_data import soer_data
from eea.themecentre.interfaces import IThemeTagging
from Products.Five.browser import BrowserView
import transaction

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
    1. [done] export metadata in JSON
    2. [-] import from XML
        1. [-] import EEAFigures
        2. [-] import EEAFigureFiles
        3. [-] extra mappings
        4. [done] transactional import
        5. [-] check encoding during import, e.g. José Barredo
        6. [-] after import owner should not be "alec" but "Carlsten"
    3. [-] generate import logs ( includin mandatory fields warnings )
    4. [-] run a full test on unicorn (including files)
    """

    questions = """
    1. what state should have imported figures and files?
    """

    def __call__(self):
        #import pdb; pdb.set_trace()

        current_parent = None
        import_context = self.context.unrestrictedTraverse(IMPORT_PATH)
        counter = 0

        for row in soer_data['rows'][:2]:
            counter += 1
            data_dict = {}

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

            # General metadata
            data_dict['description'] = description
            data_dict['creators'] = creators
            data_dict['rights'] = copyrights

            try:
                if object_type == 'EEAFigure':
                    info('INFO: adding EEAFigure %s' % filepath)

                    fig_id = import_context.invokeFactory(
                              type_name='EEAFigure',
                              id=import_context.generateUniqueId("EEAFigure"))
                    fig_ob = getattr(import_context, fig_id)

                    # Setting EEAFigures metadata
                    data_dict['subject_existing_keywords'] = \
                             keywords.split(',')

                    if not figure_type:
                        figure_type = 'Map'
                    data_dict['figureType'] = figure_type

                    themes = themes.split(',')
                    tagging = IThemeTagging(fig_ob)
                    if len(themes) > 3:
                        info('ERROR: more then 3 themes')
                    themes = filter(None, themes[:3]) # pick first 3 themes
                    tagging.tags = themes
                    #TODO: themes vocabulary to check if theme name is valid

                    data_dict['geographicCoverage'] = geo_coverage
                    data_dict['eeaManagementPlan'] = eea_management_plan
                    data_dict['lastUpload'] = last_upload
                    #data_dict['dataOwner'] = owner
                    #data_dict['processor'] = processor
                    data_dict['temporalCoverage'] = tem_coverage
                    data_dict['contact'] = contact
                    data_dict['dataSource'] = source
                    data_dict['moreInfo'] = additional_information
                    data_dict['methodology'] = methodology
                    data_dict['units'] = unit

                    fig_ob.setTitle(title)
                    fig_ob.processForm(data=1, metadata=1, values=data_dict)
                    fig_ob.reindexObject()

                    current_parent = fig_ob
                    error_detected = False
                elif object_type == 'EEAFigureFile':
                    if current_parent:
                        info('INFO: adding EEAFigureFile %s' % filepath)

                        #data_dict['filepath'] = filepath
                        data_dict['category'] = category

                        #TODO: add logic
                        pass
                    else:
                        info('ERROR: EEAFigureFile not added %s', filepath)

                else:
                    info('ERROR: unknown "Object type" on %s', filepath)
            except Exception, err:
                if object_type == 'EEAFigure':
                    current_parent = None
                info('ERROR: import error on %s', filepath)
                info_exception(err)

            if counter % 10 == 0:
                info('INFO: Transaction commited, step %s' % str(counter))
                transaction.commit()

        info('INFO: Done soer figures import!')
        return "Done soer figures import!"







